# Paquetes nativos — Instalación sin línea de comandos

Los usuarios finales pueden instalar el agente como cualquier otra aplicación, sin tocar la terminal.

---

## .deb (Debian / Ubuntu)

### Construir

```bash
bash build_deb.sh
```

### Instalar

```bash
sudo dpkg -i dist/computeruse-watcher_0.1.0_amd64.deb
```

### Gestionar

```bash
# Iniciar servicio
sudo systemctl start computeruse-watcher

# Ver estado
sudo systemctl status computeruse-watcher

# Ver logs
sudo journalctl -u computeruse-watcher -f

# Parar
sudo systemctl stop computeruse-watcher

# Desinstalar
sudo dpkg -r computeruse-watcher
```

---

## .rpm (RHEL / Fedora / openSUSE / CentOS)

### Construir

```bash
bash build_rpm.sh
```

### Instalar

```bash
sudo rpm -i dist/computeruse-watcher-0.1.0-x86_64.rpm
```

### Gestionar

```bash
# Iniciar servicio
sudo systemctl start computeruse-watcher

# Ver estado
sudo systemctl status computeruse-watcher

# Ver logs
sudo journalctl -u computeruse-watcher -f

# Parar
sudo systemctl stop computeruse-watcher

# Desinstalar
sudo rpm -e computeruse-watcher
```

---

## .msi (Windows)

### Construir

Requiere WiX Toolset (https://wixtoolset.org/).

```powershell
# Instalar WiX Toolset (si no está)
choco install wixtoolset

# Construir MSI
cd build
candle computeruse-watcher.wxs
light computeruse-watcher.wixobj
```

### Instalar

Doble clic en el `.msi` y sigue el asistente.

### Gestionar

```powershell
# Iniciar servicio
Start-Service ComputerUseWatcher

# Ver estado
Get-Service ComputerUseWatcher

# Parar
Stop-Service ComputerUseWatcher

# Desinstalar
msiexec /x {GUID}
```

---

## Notas

- **Dependencias Python**: Los paquetes asumen que `python3` y `pip3` están disponibles en el sistema.
- **systemd**: Requiere un sistema que use systemd (casi todos los Linux modernos).
- **Windows Service**: Requiere `pywin32` instalado en el entorno del servicio.
- **Configuración**: Copia `config.example.yaml` a `config.yaml` y edítalo con tus credenciales del broker MQTT.
- **Logs**: En Linux/macOS: `/var/log/computeruse-watcher.log` (systemd) o `.data/computeruse-watcher.log` (manual).
- **Logs en Windows**: Event Viewer → Windows Logs → Application.