from __future__ import annotations
from pathlib import Path
from cuw.core.config import AgentConfig
from cuw.core.logging import setup_logging
from cuw.core.db import DB
from cuw.network.mqtt_client import MQTTClient
from cuw.platform_abstraction import get_watcher
import logging

log = logging.getLogger("cuw.daemon")

class StateMachine:
    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = DB(cfg.db_path)
        self.watcher = get_watcher()
        self.mqtt = MQTTClient(
            host=cfg.broker.host,
            port=cfg.broker.port,
            username=cfg.broker.username,
            password=cfg.broker.password,
            tls=cfg.broker.tls,
            client_id=f"cuw-{self.watcher.hostname}",
        )
        self._prev_proc: tuple[str, str] | None = None
        self._prev_start: float | None = None

    def _status_topic(self) -> str:
        return f"{self.cfg.mqtt_topic_prefix}/{self.watcher.hostname}/status"

    def _events_topic(self) -> str:
        return f"{self.cfg.mqtt_topic_prefix}/{self.watcher.hostname}/events"

    def _publish_status_online(self) -> None:
        payload = {
            "status": "online",
            "os": self.watcher.os_name,
            "os_version": self.watcher.os_version,
            "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        }
        self.db.insert_event("system", {**payload, "hostname": self.watcher.hostname, "os": self.watcher.os_name, "os_version": self.watcher.os_version, "username": self.watcher.username})
        self.mqtt.publish_json(self._status_topic(), payload, retain=True)

    def start(self) -> None:
        lwt = json_placeholder = '{"status":"offline"}'
        self.mqtt.connect(self._status_topic(), '{"status":"offline"}')
        self._publish_status_online()
        log.info("Daemon started on %s", self.watcher.hostname)

    def stop(self) -> None:
        self.mqtt.disconnect()
        self.db.close()
        log.info("Daemon stopped")

    def tick(self) -> None:
        # Sync pending events
        self._sync_pending()
        # Focus change detection
        active = self.watcher.active_window()
        if active:
            proc, title = active
            if self._prev_proc != active:
                # finalize previous
                if self._prev_proc and self._prev_start is not None:
                    duration = __import__("time").time() - self._prev_start
                    self._emit_focus(self._prev_proc[0], self._prev_proc[1], start=self._prev_start, duration=duration)
                self._prev_proc = active
                self._prev_start = __import__("time").time()
            else:
                # keep running
                pass
        # Idle detection
        try:
            idle = self.watcher.idle_seconds()
            if idle > self.cfg.idle_threshold_sec:
                # emit idle (only when crossing threshold)
                pass
        except Exception:
            pass

    def _emit_focus(self, proc: str, title: str, start: float, duration: float) -> None:
        from cuw.core.events import FocusEvent, utc_iso
        ev = FocusEvent(
            hostname=self.watcher.hostname,
            os=self.watcher.os_name,
            os_version=self.watcher.os_version,
            username=self.watcher.username,
            process_name=proc,
            window_title=title,
            start_time=utc_iso(),
            duration_seconds=duration,
        )
        payload = ev.model_dump(mode="json")
        self.db.insert_event("focus_change", payload)
        self.mqtt.publish_json(self._events_topic(), payload)

    def _sync_pending(self) -> None:
        rows = list(self.db.pending(limit=200))
        sent_ids = []
        for r in rows:
            success = self.mqtt.publish_json(self._events_topic(), eval(r["payload"]))
            if success:
                sent_ids.append(r["id"])
        if sent_ids:
            self.db.mark_sent(sent_ids)
