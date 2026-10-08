# computeruse-watcher

Lightweight, OS-agnostic background agent that reports computer usage (boot, login, app focus, idle) to MQTT with a local SQLite offline cache.

## Installation

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Run

```bash
python -m cuw.cli --dry-run
# or
cuw --config config.yaml --dry-run
```

## Project structure

```
src/cuw/
  core/          config, logging, events, db
  platform_abstraction/  windows, generic, base
  network/       mqtt_client
  daemon/        state_machine
```
