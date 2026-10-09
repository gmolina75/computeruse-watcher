Para ejecutar el **computeruse-watcher** únicamente por línea de comando:

### 1. Windows (PowerShell)

```powershell
# 1. Clonar el repositorio
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher

# 2. Crear y activar entorno virtual
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -e .[dev]

# 4. Ejecutar en foreground (tequila)
python -m cuw.cli --config config.yaml  # Usa config.yaml que tenga tus credenciales
```

**O bien con parámetros de línea de comando**
```powershell
python -m cuw.cli \
   --broker-host 192.168.1.10 \
   --broker-port 1883 \
   --broker-username my_user \
   --broker-password my_pwd \
   --data-dir .data
```

### 2. Linux / macOS (Bash)

```bash
# 1. Clonar
git clone https://github.com/gmolina75/computeruse-watcher.git
cd computeruse-watcher

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -e .[dev]

# 4. Ejecutar
python -m cuw.cli --config config.yaml
```

**O con variables de entorno** (permanentes para la sesión):
```bash
export CUW_BROKER=192.168.1.10
export CUW_PORT=1883
export CUW_USERNAME=my_user
export CUW_PASSWORD=my_pwd
export CUW_DATA_DIR=.data

python -m cuw.cli
```

#### Notas rápidas
- El comando `--dry-run` solo emite los eventos a stdout sin conectarse a MQTT.
- Si quieres que el proceso quede en segundo plano, simplemente añade `&` al final en Bash o usa el `nohup`/`screen`/`tmux`.
- Los parámetros por línea de comando sobrescribirán cualquier valor en `config.yaml`.

### Quick Reference Table

| SO | Bypass de dominio | Línea de comando recomendada |
|----|-------------------|------------------------------|
| Windows | PowerShell | `python -m cuw.cli --config config.yaml` |
| Linux | Bash | `python -m cuw.cli --config config.yaml` |
| macOS | Bash | `python -m cuw.cli --config config.yaml` |

Con esto ya puedes lanzar el agente sin necesidad de scripts externos ni servicios, directamente desde tu terminal.
