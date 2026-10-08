# RUNNING.md

## Cómo ejecutar computeruse-watcher

Instrucciones detalladas para Windows, Linux y macOS.

---

## Requisitos previos

- Python 3.10+
- `git` (para clonar el repositorio)
- Acceso a un broker MQTT (opcional, pero recomendado)

---

## Instalación

### Windows PowerShell

```powershell
# Clonar el repositorio
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher

# Crear entorno virtual
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -e .[dev]
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
```

### macOS

```bash
brew install python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,macos]
```

---

## Configuración

### 1. Configurar broker MQTT

Copia el archivo de ejemplo y edítalo:

```powershell
# Windows
cp config.example.yaml config.yaml
```

```bash
# Linux/macOS
cp config.example.yaml config.yaml
```

Edita `config.yaml` con tus credenciales:

```yaml
broker:
  host: 192.168.1.10  # IP de tu broker MQTT
  port: 1883
  username: ""
  password: ""
  tls: false
```

### 2. Variables de entorno (opcional)

Si prefieres usar variables de entorno en lugar de `config.yaml`, configúralas:

```powershell
# Windows PowerShell
$env:CUW_BROKER = "192.168.1.10"
$env:CUW_USERNAME = ""
$env:CUW_PASSWORD = ""
```

```bash
# Linux/macOS
export CUW_BROKER=192.168.1.10
export CUW_USERNAME=""
export CUW_PASSWORD=""
```

---

## Ejecutar el daemon

### Dry-run (verificar que funciona)

```powershell
# Windows
python -m cuw.cli --dry-run
```

```bash
# Linux/macOS
python -m cuw.cli --dry-run
```

**Salida esperada:**

```
2026-10-08 16:30:00,000 INFO cuw.daemon Daemon started on DESKTOP-ABC
2026-10-08 16:30:02,000 INFO cuw.daemon Focus change: chrome.exe - Gmail
2026-10-08 16:30:30,000 INFO cuw.daemon Idle detected: 300 seconds
```

### Ejecución normal

```powershell
# Windows
python -m cuw.cli --config config.yaml
```

```bash
# Linux/macOS
python -m cuw.cli --config config.yaml
```

---

## Verificar que funciona

### 1. Revisar logs

```powershell
# Windows (PowerShell)
Get-Content .data\*.log -Tail 10
```

```bash
# Linux/macOS
tail -n 10 .data/*.log
```

### 2. Verificar eventos en MQTT

Usa un cliente MQTT como `mosquitto_sub`:

```bash
mosquitto_sub -h 192.168.1.10 -t "client/os_watcher/+/events" -v
```

**Eventos esperados:**

```
client/os_watcher/DESKTOP-ABC/events {"event_type":"focus_change","process_name":"chrome.exe","window_title":"Gmail","duration_seconds":120.5}
client/os_watcher/DESKTOP-ABC/events {"event_type":"idle","idle_seconds":300}
```

### 3. Verificar SQLite

```bash
sqlite3 .data/cache.db "SELECT * FROM event_cache ORDER BY id DESC LIMIT 5;"
```

---

## Instalar como servicio

### Windows Service

```powershell
pip install pywin32
python src/cuw/service/win_service.py install
python src/cuw/service/win_service.py start
```

Verificar estado:

```powershell
sc query ComputerUseWatcher
```

### systemd (Linux)

```bash
sudo cp SERVICE_SCRIPTS.md /etc/systemd/system/computeruse-watcher.service
sudo systemctl daemon-reload
sudo systemctl enable computeruse-watcher
sudo systemctl start computeruse-watcher
```

Ver logs:

```bash
sudo journalctl -u computeruse-watcher -f
```

### launchd (macOS)

```bash
cp SERVICE_SCRIPTS.md ~/Library/LaunchAgents/computeruse.watcher.plist
launchctl load ~/Library/LaunchAgents/computeruse.watcher.plist
launchctl start computeruse.watcher
```

---

## Solución de problemas

### 1. El daemon no se inicia

- Verifica que Python 3.10+ está instalado
- Revisa los logs en `.data/*.log`
- Ejecuta en modo dry-run para ver errores: `python -m cuw.cli --dry-run`

### 2. No se detectan ventanas en Linux

- Asegúrate de estar en X11 (no Wayland)
- Instala `xscreensaver` para idle detection
- Revisa que `python3-xlib` esté instalado

### 3. Eventos no llegan al broker MQTT

- Verifica que el broker MQTT esté en línea
- Revisa las credenciales en `config.yaml`
- Usa `mosquitto_sub` para verificar conectividad

### 4. El servicio no se reinicia tras reiniciar

- Windows: `sc config ComputerUseWatcher start= auto`
- Linux: `sudo systemctl enable computeruse-watcher`
- macOS: `launchctl load ~/Library/LaunchAgents/computeruse.watcher.plist`

---

## Apagar el daemon

```powershell
# Windows (PowerShell)
Stop-Process -Name python -Force
```

```bash
# Linux/macOS
pkill -f "python -m cuw.cli"
```

### Windows Service

```powershell
python src/cuw/service/win_service.py stop
python src/cuw/service/win_service.py remove
```

### systemd (Linux)

```bash
sudo systemctl stop computeruse-watcher
sudo systemctl disable computeruse-watcher
```

### launchd (macOS)

```bash
launchctl stop computeruse.watcher
launchctl unload ~/Library/LaunchAgents/computeruse.watcher.plist
```

---

**Repositorio oficial:** https://github.com/gmolina75/computeruse-watcher
