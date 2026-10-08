from __future__ import annotations
import platform
import socket
import getpass
from typing import Optional

class GenericWatcher:
    """Fallback watcher for unknown platforms (Linux generic, placeholder for macOS)."""
    @property
    def hostname(self) -> str:
        return socket.gethostname()

    @property
    def os_name(self) -> str:
        return platform.system()

    @property
    def os_version(self) -> str:
        return platform.release()

    @property
    def username(self) -> str | None:
        try:
            return getpass.getuser()
        except Exception:
            return None

    def active_window(self) -> tuple[str, str] | None:
        # No native window info without extra deps; return None gracefully.
        return None

    def idle_seconds(self) -> float:
        # Best-effort use psutil if available.
        try:
            import psutil
            # psutil has no cross-platform idle, return 0 as conservative
            return 0.0
        except Exception:
            return 0.0
