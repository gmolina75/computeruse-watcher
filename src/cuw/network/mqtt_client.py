from __future__ import annotations
import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Callable

import paho.mqtt.client as mqtt

log = logging.getLogger("cuw.mqtt")

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class MQTTClient:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
        tls: bool = False,
        client_id: str | None = None,
        on_connect: Callable[[str, int], None] | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tls = tls
        self.client_id = client_id
        self.on_connect = on_connect
        self._client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        if username:
            self._client.username_pw_set(username, password)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._lock = threading.Lock()
        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):  # pragma: no cover
        self._connected = rc == 0
        log.info("MQTT connected rc=%s", rc)
        if self.on_connect:
            try:
                self.on_connect(self.host, rc)
            except Exception:
                log.exception("on_connect callback error")

    def _on_disconnect(self, client, userdata, rc):  # pragma: no cover
        self._connected = False
        log.warning("MQTT disconnected rc=%s", rc)

    def connect(self, lwt_topic: str, lwt_payload: str) -> None:
        with self._lock:
            if self.tls:
                self._client.tls_set()
            self._client.will_set(lwt_topic, payload=lwt_payload, qos=1, retain=False)
            self._client.connect(self.host, self.port, keepalive=60)
            self._client.loop_start()

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def is_connected(self) -> bool:
        return bool(self._connected)

    def publish_json(self, topic: str, payload: dict, retain: bool = False) -> bool:
        try:
            message = json.dumps(payload, separators=(",", ":"), default=str)
            rc = self._client.publish(topic, payload=message, qos=1, retain=retain)
            return rc.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            log.exception("mqtt publish failed")
            return False
