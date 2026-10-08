# computeruse-watcher
Lightweight, OS-agnostic background agent that reports computer usage (boot, login, app focus, idle) to MQTT with a local SQLite offline cache.

## Quick start

```bash
# Create venv (Windows PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -e .[dev]

# Edit config
cp src/cuw/config.yaml.example src/cuw/config.yaml
# set broker, username/password, hostname

# Run once
cuw run --config src/cuw/config.yaml --dry-run
```

### Environment variables (override config)
```
CUW_BROKER=192.168.1.10
CUW_PORT=1883
CUW_USERNAME=
CUW_PASSWORD=
CUW_HOSTNAME=  # optional, auto-detected
```
## Design basics
- **Event-first pipeline**: every event goes to SQLite first, then MQTT. If the broker is down, events accumulate and are flushed later.
- **Platform abstraction**: `PlatformWatcher` interface with minimal OS-specific adapters. Windows uses ctypes for foreground window and idle detection (stdlib-only). Linux uses python-xlib, macOS uses AppKit (optional).
- **Standard advanced**: Pydantic-validated config, typed events, strict mypy, ruff lint, pytest suite, structured logging, JSON lines.

## Project layout
```
src/cuw/
  core/        event schema, db, config, logging
  platform_abstraction/  windows.py, linux.py, macos.py, base.py
  network/     mqtt_client.py
  daemon/      loop.py, state_machine.py
  service/     win_service.py, systemd etc.
tests/
```
