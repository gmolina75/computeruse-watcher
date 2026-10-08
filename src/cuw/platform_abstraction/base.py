from __future__ import annotations
import platform
import socket
import getpass
from typing import Protocol

class PlatformWatcher(Protocol):
    @property
    def hostname(self) -> str: ...
    @property
    def os_name(self) -> str: ...
    @property
    def os_version(self) -> str: ...
    @property
    def username(self) -> str | None: ...

    def active_window(self) -> tuple[str, str] | None:
        """Return (process_name, window_title) or None."""
        ...

    def idle_seconds(self) -> float:
        """Seconds since last input."""
        ...
