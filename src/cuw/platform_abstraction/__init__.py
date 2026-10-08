from __future__ import annotations
import sys
from cuw.platform_abstraction.base import PlatformWatcher
from cuw.platform_abstraction.windows import WindowsWatcher
from cuw.platform_abstraction.linux import LinuxWatcher
from cuw.platform_abstraction.generic import GenericWatcher

def get_watcher() -> PlatformWatcher:
    system = sys.platform
    if system.startswith("win"):
        return WindowsWatcher()
    if system.startswith("linux"):
        return LinuxWatcher()
    # macOS: GenericWatcher for now (AppKit support can be plugged in later)
    return GenericWatcher()