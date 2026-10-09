# Binarios pre-compilados — Instalación sin Python ni pip

Los binarios pre-compilados incluyen el intérprete de Python y todas las dependencias. Solo necesitas el archivo ejecutable; doble clic y listo.

---

## Construir binario pre-compilado

### Linux / macOS (PyInstaller)

```bash
bash build_binary.sh
```

### Windows (PyInstaller)

```powershell
build_binary.bat
```

---

## Ejecutar el binario

### Linux / macOS

```bash
# Ejecutar directamente
./dist/computeruse-watcher-0.1.0

# Con configuración personalizada
./dist/computeruse-watcher-0.1.0 --config config.yaml

# Dry-run (verificar que funciona)
./dist/computeruse-watcher-0.1.0 --dry-run
```

### Windows

```powershell
# Ejecutar directamente
.\dist\computeruse-watcher-0.1.0.exe

# Con configuración personalizada
.\dist\computeruse-watcher-0.1.0.exe --config config.yaml

# Dry-run (verificar que funciona)
.\dist\computeruse-watcher-0.1.0.exe --dry-run
```

---

## Notas

- **Dependencias**: El binario incluye `paho-mqtt`, `psutil`, `pydantic` y el código del agente.
- **Configuración**: El binario busca `config.yaml` en el directorio actual. Si no lo encuentra, usa valores por defecto (broker `localhost:1883`).
- **Logs**: Los logs se escriben en `.data/computeruse-watcher.log` (relativo al directorio de ejecución).
- **Datos**: La base de datos SQLite se crea en `.data/cache.db` (relativo al directorio de ejecución).
- **Tamaño**: El binario suele ser ~15-25 MB (dependiendo de la plataforma).
- **Actualizaciones**: Para obtener la última versión, descarga el binario nuevo del repositorio.

---

## Alternativas

Si PyInstaller no funciona en tu sistema, puedes usar:

- **cx_Freeze**: `pip install cx-Freeze` y sigue la documentación.
- **Nuitka**: `pip install nuitka` y compila a binario nativo.
- **Docker**: Usa el `Dockerfile` proporcionado para contenedores.

---

## Solución de problemas

### El binario no se ejecuta (Linux/macOS)

```bash
# Dar permisos de ejecución
chmod +x dist/computeruse-watcher-0.1.0

# Ejecutar con straddle para ver errores
strace ./dist/computeruse-watcher-0.1.0 --dry-run
```

### El binario no se ejecuta (Windows)

- Asegúrate de tener Windows 10 o superior.
- Los binarios de PyInstaller pueden requerir Visual C++ Redistributable 2015-2019.
- Ejecuta como Administrador si hay problemas de permisos.

### El binario falla al buscar dependencias

- Asegúrate de que el directorio `.data` es escribible.
- En Linux/macOS, usa `ldd` para ver las dependencias del binario:
  ```bash
  ldd dist/computeruse-watcher-0.1.0
  ```