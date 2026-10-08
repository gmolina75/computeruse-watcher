from __future__ import annotations
import sys
from cuw.platform_abstraction.base import PlatformWatcher
from cuw.platform_abstraction.windows import WindowsWatcher
from cuw.platform_abstraction.generic import GenericWatcher

def get_watcher() -> PlatformWatcher:
    system = sys.platform
    if system.startswith("win"):
        return WindowsWatcher()
    # For Linux and macOS we currently return the generic watcher.
    # macOS AppKit support can be plugged in later under platform_abstraction/macos.py
    return GenericWatcher()
