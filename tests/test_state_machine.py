from __future__ import annotations

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


def test_state_machine_focus_change(cfg: AgentConfig) -> None:
    with patch("cuw.daemon.state_machine.get_watcher") as gw, \
         patch("cuw.daemon.state_machine.MQTTClient") as MqttMock:
        w = _make_watcher()
        gw.return_value = w
        sm = StateMachine(cfg)
        sm.start()
        sm.tick()
        # second tick, same window -> no new event
        sm.tick()
        sm.tick()
        # change window -> should emit previous
        w.active_window.return_value = ("notepad.exe", "untitled")
        sm.tick()
        # check DB before closing
        rows = list(sm.db.pending(limit=50))
        sm.stop()
        assert len(rows) >= 1
        assert any(r["event_type"] == "focus_change" for r in rows)