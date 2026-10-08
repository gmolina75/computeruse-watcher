# Instrucciones para probar en Ubuntu 22.04+

## 1. Instalar dependencias del sistema

```bash
# Actualizar
sudo apt update

# Instalar Python 3 (ya suele estar en Ubuntu)
python3 --version

# Instalar python-xlib para detección de ventanas X11
sudo apt install python3-xlib python3-venv python3-pip
```

## 2. Clonar el repositorio

```bash
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher
```

## 3. Crear entorno virtual e instalar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 4. Configurar broker MQTT (opcional)

```bash
# Copiar config de ejemplo
cp config.example.ini config.yaml
# Editar broker, username, password si aplica
```

## 5. Probar detección de ventanas en X11

```bash
# Verificar que python-xlib funciona
python -c "from cuw.platform_abstraction.linux import LinuxWatcher; w=LinuxWatcher(); print(w.hostname, w.os_name, w.username, w.active_window(), w.idle_seconds())"
```

## 6. Ejecutar daemon en dry-run

```bash
python -m cuw.cli --dry-run
```

## 7. Ejecutar daemon en background (systemd)

```bash
# Instalar como servicio
sudo cp /etc/systemd/system/computeruse-watcher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable computeruse-watcher
sudo systemctl start computeruse-watcher

# Verificar estado
sudo systemctl status computeruse-watcher

# Ver logs
sudo journalctl -u computeruse-watcher -f
```

## 8. Correr tests

```bash
python -m pytest tests/ -v
```

## Notas

- **X11 vs Wayland**: python-xlib solo funciona en X11. Para Wayland (GNOME/KDE), necesitas usar D-Bus o el portal de desktop. El watcher caerá gracefulmente a GenericWatcher.
- **Idle detection**: requiere XScreenSaver extension. Instala con `sudo apt install xscreensaver` si no está disponible.
- **Logs**: en systemd usa `journalctl -u computeruse-watcher -f`. En ejecución manual, salen por stderr.