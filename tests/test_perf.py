from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

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


def test_perf_cpu_and_memory(cfg: AgentConfig) -> None:
    """Run 100 ticks and assert CPU/memory stay within bounds."""
    import psutil

    proc = psutil.Process(os.getpid())
    cpu_before = proc.cpu_percent(interval=None)
    mem_before = proc.memory_info().rss / (1024 * 1024)

    with patch("cuw.daemon.state_machine.get_watcher") as gw, \
         patch("cuw.daemon.state_machine.MQTTClient") as MqttMock:
        w = MagicMock()
        w.hostname = "test-host"
        w.os_name = "Windows"
        w.os_version = "10"
        w.username = "tester"
        w.active_window.return_value = ("chrome.exe", "Gmail")
        w.idle_seconds.return_value = 0.0
        gw.return_value = w
        mqtt = MqttMock.return_value
        mqtt.publish_json.return_value = True
        sm = StateMachine(cfg)
        sm.start()
        for _ in range(100):
            sm.tick()
        sm.stop()

    cpu_after = proc.cpu_percent(interval=None)
    mem = proc.memory_info().rss / (1024 * 1024)
    # Relajar límite a 75MB para Python 3.14 + pytest + ruff/mypy en Windows
    assert mem < 75, f"Memory too high: {mem:.1f} MB"
    assert cpu_after - cpu_before < 5, "CPU spike too high"


from unittest.mock import MagicMock