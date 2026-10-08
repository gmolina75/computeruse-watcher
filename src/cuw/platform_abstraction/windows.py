from __future__ import annotations
import ctypes
from ctypes import wintypes, Structure, POINTER
import platform
import socket
import getpass

class _LASTINPUTINFO(Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]

_u = ctypes.windll.user32
_k = ctypes.windll.kernel32
_u.GetLastInputInfo.argtypes = [POINTER(_LASTINPUTINFO)]
_u.GetLastInputInfo.restype = wintypes.BOOL

def _get_idle_seconds() -> float:
    lii = _LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
    if not _u.GetLastInputInfo(ctypes.byref(lii)):
        return 0.0
    ticks = _k.GetTickCount()
    return max(0.0, (ticks - lii.dwTime) / 1000.0)

def _get_foreground_info() -> tuple[str, str] | None:
    hwnd = _u.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wintypes.DWORD()
    _u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    proc_name = ""
    try:
        import psutil
        try:
            p = psutil.Process(int(pid.value))
            proc_name = p.name() or ""
        except Exception:
            proc_name = ""
    except Exception:
        proc_name = ""
    length = _u.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        _u.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value or ""
        return proc_name, title
    return proc_name, ""

class WindowsWatcher:
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
        try:
            return _get_foreground_info()
        except Exception:
            return None

    def idle_seconds(self) -> float:
        try:
            return _get_idle_seconds()
        except Exception:
            return 0.0
