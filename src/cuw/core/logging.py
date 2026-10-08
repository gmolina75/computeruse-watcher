from __future__ import annotations
import logging
from pathlib import Path
from typing import Any

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

def setup_logging(level: str = "INFO", log_path: Path | None = None) -> logging.Logger:
    """Configure structured logging for cuw. Returns root logger."""
    handlers: list[logging.Handler] = []
    fmt = logging.Formatter(LOG_FORMAT)

    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(fmt)
        handlers.append(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    handlers.append(ch)

    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=handlers)
    return logging.getLogger("cuw")
