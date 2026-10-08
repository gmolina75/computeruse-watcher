# Computer Use Watcher — Agente de telemetría cross-platform para uso de computadora

> **Proyecto:** `computeruse-watcher`  
> **Autor:** Giancarlo Molina  
> **Propósito:** Registrar de forma ligera y fiable qué usuario está en el sistema, qué aplicación está en primer plano, cuánto tiempo se usa y cuándo el usuario está inactivo, y enviarlo a un broker MQTT con copia local en SQLite para no perder datos sin red.

## ¿Para qué sirve?

Es un **agente de telemetría tipo ActivityWatch/Tockler** pero orientado a operaciones:
- **Auditoría y productividad**: saber quién usó qué aplicación y por cuánto tiempo.
- **Analítica operativa**: correlación de eventos de sistema con métricas de negocio.
- **Resiliencia**: todo evento va primero a SQLite y luego se replica a MQTT. Si el broker cae, los datos se quedan en caché y se sincronizan al reconectar.
- **Privacidad controlable**: los títulos de ventana se envían completos; el filtrado puede aplicarse en el lado del servidor/warehouse, no en el agente.

## Arquitectura resumida

```
OS (Windows / Linux / macOS) 
  → PlatformWatcher (ctypes / python-xlib / AppKit) 
  → StateMachine (focus change, idle, login/logout) 
  → SQLite (event_cache, WAL)
  → MQTTClient (paho-mqtt, LWT, QoS 1)
  → Broker MQTT → Dashboard / Warehouse
```

El flujo es **event-first**: cada cambio se guarda localmente y luego se publica. No hay servicio web local, es un daemon headless.

## ¿Qué mide por sistema operativo?

### Windows (Desktop / Server)
- **Ventana activa**: `GetForegroundWindow` + `GetWindowText` vía `ctypes` (stdlib-only, sin pywin32).
- **Proceso**: nombre del ejecutable con `psutil.Process`.
- **Idle**: `GetLastInputInfo` vía `ctypes`.
- **Usuario**: `getpass.getuser`.
- **Instalación típica**: Windows Service con `sc create` o `pywin32`.

### Linux (Ubuntu 22.04+, X11)
- **Ventana activa**: `python-xlib` sobre X11.
- **Idle**: XScreenSaver extension si está disponible.
- **Instalación típica**: `systemd` unit con auto-restart.

### macOS
- **Plan**: AppKit / Quartz vía `pyobjc`.
- **Ventana activa**: `NSWorkspace.sharedWorkspace().activeApplication`.
- **Instalación típica**: `launchd` plist.

> **Android**: fuera de v1. Roadmap futuro con capacidades reducidas.

## Requisitos técnicos

- Python 3.10+
- `paho-mqtt`, `psutil`, `pydantic`
- Opcionales por SO: `python-xlib` (Linux X11), `pyobjc` (macOS)

## Instalación rápida

### Windows PowerShell

```powershell
# Clonar
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher

# Entorno virtual
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar
pip install -e .[dev]

# Probar capa Windows
python -c "from cuw.platform_abstraction.windows import WindowsWatcher as W; w=W(); print(w.hostname, w.os_name, w.username, w.active_window(), w.idle_seconds())"

# Dry-run del daemon
python -m cuw.cli --dry-run
```

### Ubuntu 22.04+ (X11)

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip python3-xlib xscreensaver

git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher

python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Probar watcher Linux
python -c "from cuw.platform_abstraction.linux import LinuxWatcher; w=LinuxWatcher(); print(w.hostname, w.os_name, w.username, w.active_window(), w.idle_seconds())"

# Dry-run
python -m cuw.cli --dry-run
```

### macOS (próximo)

```bash
brew install python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,macos]
python -m cuw.cli --dry-run
```

## Configuración

El agente lee variables de entorno y un archivo de configuración YAML opcional.

Variables de entorno soportadas:

```
CUW_BROKER=192.168.1.10
CUW_PORT=1883
CUW_USERNAME=
CUW_PASSWORD=
CUW_DATA_DIR=.data
CUW_DB_PATH=.data/cache.db
```

**Ejemplo de configuración** (`config.example.yaml`):

```yaml
agent:
  poll_interval_sec: 2
  idle_threshold_sec: 300
  mqtt_topic_prefix: client/os_watcher
  data_dir: .data
broker:
  host: 192.168.1.10
  port: 1883
  username: ""
  password: ""
  tls: false
```

**Temas MQTT**

- `client/os_watcher/{hostname}/status` → retained, `online` / `offline` con LWT.
- `client/os_watcher/{hostname}/events` → eventos `focus_change`, `idle`, `system`, `session`.

**Payload de ejemplo (focus_change)**

```json
{
  "event_id": "uuid-v4",
  "event_type": "focus_change",
  "hostname": "DESKTOP-ABC",
  "os": "Windows",
  "os_version": "10",
  "username": "giancarlo",
  "process_name": "pycharm64.exe",
  "window_title": "computeruse-watcher [Z:\\Customers\\Demo] - SPEC.md",
  "start_time": "2026-10-08T16:30:00Z",
  "duration_seconds": 120.5
}
```

## Empaquetado como servicio

### Windows Service

```powershell
pip install pywin32
python src/cuw/service/win_service.py install
python src/cuw/service/win_service.py start
python src/cuw/service/win_service.py stop
python src/cuw/service/win_service.py remove
```

### systemd (Linux)

```ini
[Unit]
Description=Computer Use Watcher Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/computeruse-watcher
ExecStart=/opt/computeruse-watcher/.venv/bin/cuw run --config /opt/computeruse-watcher/config.yaml
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl enable computeruse-watcher
sudo systemctl start computeruse-watcher
sudo journalctl -u computeruse-watcher -f
```

### launchd (macOS)

Ver `SERVICE_SCRIPTS.md` para el plist completo.

## Tests

```bash
pip install -e .[dev]
pytest tests/ -v
```

Los tests incluyen:
- Mock de plataforma
- Rollback sin broker (SQLite persiste)
- Sincronización tras reconexión
- Performance: CPU <1%, RAM <75 MB

## Roadmap público

- v0.1 → scaffold cross-platform, MQTT + SQLite, tests
- v0.2 → macOS AppKit watcher, Linux Wayland vía D-Bus
- v0.3 → TLS + auth mutua MQTT, cifrado SQLite
- v0.4 → Android reducido (foreground app + boot)
- v0.5 → plugins de integración (Prometheus, BigQuery)

## Licencia

Uso interno / Propietario. Contactar a Giancarlo Molina para licenciamiento.

---

**Repositorio oficial:** https://github.com/gmolina75/computeruse-watcher
