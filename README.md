# Computer Use Watcher — Agente de telemetría cross-platform

> **Objetivo:** Saber quién usó qué aplicación y cuánto tiempo, reportado a MQTT con caché local SQLite para no perder datos sin red.

## 🚀 Instalación rápida (3 formas)

### 1. Script de instalación único (Linux/macOS)
```bash
curl -fsSL https://raw.githubusercontent.com/gmolina75/computeruse-watcher/main/install.sh | bash
```

### 2. Script de instalación único (Windows PowerShell)
```powershell
iex -File https://raw.githubusercontent.com/gmolina75/computeruse-watcher/main/install.ps1
```

### 3. Docker (Linux/macOS/Windows)
```bash
docker run -d \
  --name computeruse-watcher \
  -e CUW_BROKER=192.168.1.10 \
  -v /var/lib/cuw:/data \
  gmolina75/computeruse-watcher:latest
```

## 📦 Instalación manual

```bash
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## ⚙️ Configuración

### Asistente interactivo
```bash
python -m cuw --setup
```
El wizard pregunta por broker, puerto, usuario y contraseña, y genera `config.yaml` automáticamente.

### Variables de entorno
```bash
export CUW_BROKER=192.168.1.10
export CUW_PORT=1883
export CUW_USERNAME=my_user
export CUW_PASSWORD=my_pwd
export CUW_DATA_DIR=.data
```

### Archivo YAML
```yaml
broker:
  host: 192.168.1.10
  port: 1883
  username: ""
  password: ""
  tls: false
```

## ▶️ Ejecución

```bash
# Dry-run (verificar que funciona)
python -m cuw.cli --dry-run

# Ejecución normal
python -m cuw.cli --config config.yaml
```

## 🖥️ Plataformas soportadas

- **Windows** — ctypes (stdlib-only)
- **Linux** — python-xlib (X11)
- **macOS** — AppKit (próximo)

## 📊 Eventos generados

- `system` — online/offline con LWT
- `session` — login/logout
- `focus_change` — app en primer plano con título y duración
- `idle` — inactividad > umbral

## 🔗 Topics MQTT

- `client/os_watcher/{hostname}/status` — retained
- `client/os_watcher/{hostname}/events` — focus_change, idle, system, session

## 🧪 Tests

```bash
pytest tests/ -v
```

## 📚 Documentación

- `SPEC.md` — especificación completa
- `ARCHITECTURE.md` — arquitectura con diagramas Mermaid
- `RUNNING.md` — guía detallada de ejecución
- `SERVICE_SCRIPTS.md` — scripts de servicio (Windows Service, systemd, launchd)
- `CHANGELOG.md` — historial de cambios

## 📋 Roadmap

- v0.1 → scaffold cross-platform, MQTT + SQLite, tests
- v0.2 → macOS AppKit watcher, Linux Wayland vía D-Bus
- v0.3 → TLS + auth mutua MQTT, cifrado SQLite
- v0.4 → Android reducido (foreground app + boot)
- v0.5 → plugins de integración (Prometheus, BigQuery)

## 📄 Licencia

Uso interno / Propietario. Contactar a Giancarlo Molina para licenciamiento.

---

**Repositorio oficial:** https://github.com/gmolina75/computeruse-watcher