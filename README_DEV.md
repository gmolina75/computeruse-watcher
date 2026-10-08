## computeruse-watcher

Daemon ligero y agnóstico a SO que reporta uso de computadora a MQTT.

### Estructura
```
src/cuw/
  core/          config, logging, events, db
  platform_abstraction/  windows, generic, base
  network/       mqtt_client
  daemon/        state_machine, loop
  service/       servicios Windows/systemd/launchd
```

### Instalación
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

### Ejecutar
```bash
cuw --config src/cuw/config.example.yaml --dry-run
```

### Config
Archivo YAML opcional. Variables de entorno sobrescriben:
`CUW_BROKER`, `CUW_PORT`, `CUW_USERNAME`, `CUW_PASSWORD`, `CUW_DATA_DIR`, etc.

### Paquetes
Python 3.10+. Dependencias mínimas: paho-mqtt, psutil, pydantic.
Herramientas de calidad: ruff, mypy strict, pytest.

### Seguridad
- Comunicación MQTT sin TLS en v1 (red local/VPN confiable). TLS disponible como flag.
- Datos sensibles: los títulos de ventana se reportan completos; el filtrado es responsabilidad del servidor.
- Caché local SQLite con WAL, sin PII extra.
