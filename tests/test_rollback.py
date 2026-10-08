from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cuw.core.config import AgentConfig, BrokerConfig
from cuw.daemon.state_machine import StateMachine


@pytest.fixture
def cfg(tmp_path: Path) -> AgentConfig:
    return AgentConfig(
        data_dir=tmp_path / "data",
        db_path=tmp_path / "data" / "cache.db",
        poll_interval_sec=0.1,
        idle_threshold_sec=10,
        broker=BrokerConfig(host="localhost", port=1883),
    )


def _make_watcher() -> MagicMock:
    w = MagicMock()
    w.hostname = "test-host"
    w.os_name = "Windows"
    w.os_version = "10"
    w.username = "tester"
    w.active_window.return_value = ("chrome.exe", "Gmail")
    w.idle_seconds.return_value = 0.0
    return w


def test_rollback_when_mqtt_down(cfg: AgentConfig) -> None:
    """Events must persist in SQLite when MQTT is unreachable."""
    with patch("cuw.daemon.state_machine.get_watcher") as gw, \
         patch("cuw.daemon.state_machine.MQTTClient") as MqttMock:
        gw.return_value = _make_watcher()
        mqtt = MqttMock.return_value
        mqtt.is_connected.return_value = False
        mqtt.publish_json.return_value = False  # simulate broker down
        sm = StateMachine(cfg)
        sm.start()
        sm.tick()
        sm.tick()
        rows = list(sm.db.pending(limit=50))
        sm.stop()
        assert len(rows) > 0, "events should be queued locally when MQTT fails"
        assert all(r["sent_status"] == 0 for r in rows)


def test_sync_after_reconnect(cfg: AgentConfig) -> None:
    """Pending events are flushed when MQTT reconnects."""
    with patch("cuw.daemon.state_machine.get_watcher") as gw, \
         patch("cuw.daemon.state_machine.MQTTClient") as MqttMock:
        gw.return_value = _make_watcher()
        mqtt = MqttMock.return_value
        # first pass: broker down
        mqtt.publish_json.return_value = False
        sm = StateMachine(cfg)
        sm.start()
        sm.tick()
        sm.tick()
        pending_before = list(sm.db.pending(limit=50))
        sm.stop()
        assert len(pending_before) > 0

        # second pass: broker back up
        mqtt.publish_json.return_value = True
        sm2 = StateMachine(cfg)
        sm2.start()
        sm2.tick()
        pending_after = list(sm2.db.pending(limit=50))
        sm2.stop()
        assert len(pending_after) == 0, "all pending events should be flushed"


def test_idle_event_emitted_after_threshold(cfg: AgentConfig) -> None:
    """Idle event fires once when idle_seconds crosses threshold."""
    with patch("cuw.daemon.state_machine.get_watcher") as gw, \
         patch("cuw.daemon.state_machine.MQTTClient") as MqttMock:
        gw.return_value = _make_watcher()
        mqtt = MqttMock.return_value
        mqtt.publish_json.return_value = True
        sm = StateMachine(cfg)
        sm.start()
        sm.tick()
        # simulate idle crossing threshold
        gw.return_value.idle_seconds.return_value = 15.0
        sm.tick()
        rows = list(sm.db.pending(limit=50))
        sm.stop()
        assert any(r["event_type"] == "idle" for r in rows)