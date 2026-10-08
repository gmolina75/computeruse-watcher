from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

class BrokerConfig(BaseModel):
    host: str = Field(default=os.getenv("CUW_BROKER", "localhost"))
    port: int = Field(default=int(os.getenv("CUW_PORT", "1883")))
    username: str | None = os.getenv("CUW_USERNAME") or None
    password: str | None = os.getenv("CUW_PASSWORD") or None
    tls: bool = Field(default=False)
    keepalive: int = 60

    @field_validator("port")
    @classmethod
    def port_range(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("port out of range")
        return v

class AgentConfig(BaseModel):
    poll_interval_sec: float = 2.0
    idle_threshold_sec: float = 300.0
    mqtt_topic_prefix: str = "client/os_watcher"
    data_dir: Path = Path(os.getenv("CUW_DATA_DIR", ".data"))
    db_path: Path = Path(os.getenv("CUW_DB_PATH", ".data/cache.db"))
    log_path: Path | None = None
    broker: BrokerConfig = BrokerConfig()

    def model_post_init(self, __context: object) -> None:
        # ensure paths inside data_dir by default
        if self.db_path == Path(".data/cache.db") and self.data_dir:
            self.db_path = self.data_dir / "cache.db"
