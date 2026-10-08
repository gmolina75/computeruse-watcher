from __future__ import annotations

import platform
import socket
import getpass
from typing import Optional

try:
    import Xlib.display
    import Xlib.X
    _HAS_XLIB = True
except Exception:
    _HAS_XLIB = False


class LinuxWatcher:
    """Linux X11-based watcher. Uses python-xlib for foreground window detection."""
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
        if not _HAS_XLIB:
            return None
        try:
            d = Xlib.display.Display()
            root = d.screen().root
            window = root.get_input_focus().id
            if not window:
                return None
            tree = window.query_tree()
            active = tree.children[0] if tree.children else None
            if not active:
                return None
            name = active.get_wm_name() or ""
            # Get process name from /proc via window title (best effort)
            proc = ""
            try:
                import psutil
                for p in psutil.process_iter(["name", "cmdline"]):
                    if name in (p.info["name"] or "") or any(name in c for c in (p.info["cmdline"] or [])):
                        proc = p.info["name"]
                        break
            except Exception:
                pass
            return proc or name, name
        except Exception:
            return None

    def idle_seconds(self) -> float:
        try:
            import Xlib.display
            d = Xlib.display.Display()
            root = d.screen().root
            # XScreenSaver extension
            try:
                from Xlib.ext.xscreensaver import query
                info = query(d, root)
                if info and info.idle:
                    return info.idle / 1000.0
            except Exception:
                pass
            return 0.0
        except Exception:
            return 0.0