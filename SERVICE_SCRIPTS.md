# Service scripts

Scripts para empaquetar el agente como servicio auto-arrancable en cada SO.

---

## Windows Service (Python 3.10+)

`src/cuw/service/win_service.py`

```python
# Requires pywin32: pip install pywin32
# Instalar: python src/cuw/service/win_service.py install

import os
import sys
from pathlib import Path
from win32serviceutil import HandleCommandLine, ServiceCtrlHandler
from win32service import SERVICE_RUNNING, SERVICE_STOPPED
from win32event import SetEvent, CreateEvent
from servicemanager import LogInfoMsg, LogErrorMsg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from cuw.cli import main as run_main


class ComputerUseWatcherService:
    _svc_name_ = "ComputerUseWatcher"
    _svc_display_name_ = "Computer Use Watcher Agent"
    _svc_description_ = "Lightweight OS-agnostic computer usage telemetry agent"

    def __init__(self, args):
        self.args = args
        self.stop_event = CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        SetEvent(self.stop_event)

    def SvcDoRun(self):
        LogInfoMsg(f"Service {self._svc_name_} starting")
        try:
            # Ejecutar el daemon en segundo plano
            import threading
            def _run():
                try:
                    run_main()
                except Exception as e:
                    LogErrorMsg(f"Service crashed: {e}")
            t = threading.Thread(target=_run, daemon=True)
            t.start()
            # Esperar señal de stop
            import win32event
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            LogInfoMsg("Service stopped gracefully")
        except Exception as e:
            LogErrorMsg(f"Service failed: {e}")


if __name__ == "__main__":
    HandleCommandLine(ComputerUseWatcherService)
```

**Instalar/desinstalar**
```powershell
python src/cuw/service/win_service.py install
python src/cuw/service/win_service.py start
python src/cuw/service/win_service.py stop
python src/cuw/service/win_service.py remove
```

---

## systemd (Linux)

`/etc/systemd/system/computeruse-watcher.service`

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

**Instalar**
```bash
sudo cp computeruse-watcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable computeruse-watcher
sudo systemctl start computeruse-watcher
```

---

## launchd (macOS)

`~/Library/LaunchAgents/computeruse.watcher.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>computeruse.watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/computeruse-watcher/.venv/bin/cuw</string>
        <string>run</string>
        <string>--config</string>
        <string>/opt/computeruse-watcher/config.yaml</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/computeruse-watcher.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/computeruse-watcher.err</string>
</dict>
</plist>
```

**Cargar**
```bash
launchctl load ~/Library/LaunchAgents/computeruse.watcher.plist
launchctl start computeruse.watcher
```

---

## Empaquetado portable (Windows)

`build_portable.ps1`

```powershell
# Ejemplo para crear un ZIP portable listo para distribuir
$src = "Z:\Customers\Demo\4.1\python\computeruse-watcher"
$zip = "$src\dist\computeruse-watcher-portable.zip"
if (!(Test-Path "$src\dist")) { New-Item -ItemType Directory -Path "$src\dist" }
Compress-Archive -Path "$src\src", "$src\pyproject.toml", "$src\README_REPO.md", "$src\config.example.ini" -DestinationPath $zip -Force
```

---

## Notas

- **Windows**: pywin32 debe instalarse en el entorno del servicio
- **Linux/macOS**: usar `python -m venv` y rutas absolutas en los plists/services
- **Config**: usar rutas absolutas en `data_dir` y `log_path` para evitar problemas de permisos
- **Logs**: redirigir stdout/stderr a archivos o usar `journalctl` en systemd
