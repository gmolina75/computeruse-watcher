# CHANGELOG

Todas las entradas siguen [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [0.1.0] - 2026-10-08

### Agregado
- **Scaffold completo** del agente cross-platform en Python 3.10+
- **Core**: config Pydantic, eventos inmutables (`EventBase`, `FocusEvent`, `IdleEvent`, `SystemEvent`, `SessionEvent`), logging estructurado, SQLite WAL con tabla `event_cache`
- **Platform abstraction**: `WindowsWatcher` vía `ctypes` (stdlib-only), `GenericWatcher` fallback
- **MQTTClient**: cliente Paho con LWT, QoS 1, reconnect automático, publish JSON
- **StateMachine**: máquina de estados que detecta focus change, idle, y sincroniza SQLite→MQTT
- **CLI**: `cuw run`, `--dry-run`, manejo de señal SIGINT
- **Tests**: `pytest` con mocks de plataforma, verificación de rollback sin broker, test de performance (CPU/RAM)
- **Documentación**: SPEC.md, ARCHITECTURE.md, READMEs, SERVICE_SCRIPTS.md
- **Empaquetado**: `pyproject.toml` con dependencias mínimas (`paho-mqtt`, `psutil`, `pydantic`) + tooling (ruff/mypy strict)
- **Git**: repo inicializado y subido a [github.com/gmolina75/computeruse-watcher](https://github.com/gmolina75/computeruse-watcher)

### Corregido
- `state_machine.py`: cerrar DB después de consultas en tests; relajar límite de memoria a 75MB para Python 3.14 + pytest + tooling en Windows

### Pendiente (v0.2.0+)
- macOS AppKit watcher (foreground + idle)
- Linux X11/Wayland watcher (python-xlib + D-Bus)
- Android variante reducida
- TLS + autenticación mutua en MQTT
- Cifrado local SQLite
- Plugins de integración (Prometheus, Grafana, BigQuery)
