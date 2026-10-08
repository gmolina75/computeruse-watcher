from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from cuw.core.config import AgentConfig
from cuw.core.db import DB
from cuw.core.events import FocusEvent, IdleEvent, SystemEvent, utc_iso
from cuw.network.mqtt_client import MQTTClient
from cuw.platform_abstraction import get_watcher

log = logging.getLogger("cuw.daemon")

OFFLINE_PAYLOAD = '{"status": "offline"}'
ONLINE_PAYLOAD = {"status": "online"}


class StateMachine:
    """Event-first state machine: SQLite cache → MQTT sync, focus tracking, idle detection."""

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
        self._idle_emitted: bool = False

    def _status_topic(self) -> str:
        return f"{self.cfg.mqtt_topic_prefix}/{self.watcher.hostname}/status"

    def _events_topic(self) -> str:
        return f"{self.cfg.mqtt_topic_prefix}/{self.watcher.hostname}/events"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _publish_status_online(self) -> None:
        payload = {
            "status": "online",
            "os": self.watcher.os_name,
            "os_version": self.watcher.os_version,
            "timestamp": self._now_iso(),
        }
        self.db.insert_event("system", {**payload, "hostname": self.watcher.hostname, "username": self.watcher.username})
        self.mqtt.publish_json(self._status_topic(), payload, retain=True)

    def start(self) -> None:
        self.mqtt.connect(self._status_topic(), OFFLINE_PAYLOAD)
        self._publish_status_online()
        log.info("Daemon started on %s", self.watcher.hostname)

    def stop(self) -> None:
        self.mqtt.disconnect()
        self.db.close()
        log.info("Daemon stopped")

    def tick(self) -> None:
        self._sync_pending()
        self._track_focus()
        self._track_idle()

    def _track_focus(self) -> None:
        active = self.watcher.active_window()
        if not active:
            return
        proc, title = active
        if self._prev_proc != active:
            if self._prev_proc and self._prev_start is not None:
                duration = time.time() - self._prev_start
                self._emit_focus(self._prev_proc[0], self._prev_proc[1], duration)
            self._prev_proc = active
            self._prev_start = time.time()
            self._idle_emitted = False

    def _track_idle(self) -> None:
        try:
            idle = self.watcher.idle_seconds()
        except Exception:
            return
        if idle > self.cfg.idle_threshold_sec and not self._idle_emitted:
            ev = IdleEvent(
                hostname=self.watcher.hostname,
                os=self.watcher.os_name,
                os_version=self.watcher.os_version,
                username=self.watcher.username,
                idle_seconds=idle,
            )
            payload = ev.model_dump(mode="json")
            self.db.insert_event("idle", payload)
            self.mqtt.publish_json(self._events_topic(), payload)
            self._idle_emitted = True

    def _emit_focus(self, proc: str, title: str, duration: float) -> None:
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
        sent_ids: list[int] = []
        for r in rows:
            payload = json.loads(r["payload"])
            success = self.mqtt.publish_json(self._events_topic(), payload)
            if success:
                sent_ids.append(r["id"])
        if sent_ids:
            self.db.mark_sent(sent_ids)