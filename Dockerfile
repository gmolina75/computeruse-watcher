FROM python:3.11-slim

LABEL maintainer="Giancarlo Molina"
LABEL description="Cross-platform computer usage telemetry agent"

# Instalar dependencias del sistema para python-xlib y psutil
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python primero (cache)
COPY pyproject.toml ./
COPY src/cuw/__init__.py src/cuw/
COPY src/cuw/core/__init__.py src/cuw/core/
COPY src/cuw/core/config.py src/cuw/core/
COPY src/cuw/core/db.py src/cuw/core/
COPY src/cuw/core/events.py src/cuw/core/
COPY src/cuw/core/logging.py src/cuw/core/
COPY src/cuw/network/__init__.py src/cuw/network/
COPY src/cuw/network/mqtt_client.py src/cuw/network/
COPY src/cuw/platform_abstraction/__init__.py src/cuw/platform_abstraction/
COPY src/cuw/platform_abstraction/base.py src/cuw/platform_abstraction/
COPY src/cuw/platform_abstraction/generic.py src/cuw/platform_abstraction/
COPY src/cuw/platform_abstraction/windows.py src/cuw/platform_abstraction/
COPY src/cuw/platform_abstraction/linux.py src/cuw/platform_abstraction/
COPY src/cuw/daemon/__init__.py src/cuw/daemon/
COPY src/cuw/daemon/state_machine.py src/cuw/daemon/
COPY src/cuw/cli.py src/cuw/
COPY README.md ./

RUN pip install --no-cache-dir -e .

# Directorio de datos
RUN mkdir -p /data && chmod 777 /data
VOLUME ["/data"]

ENV CUW_DATA_DIR=/data
ENV CUW_BROKER=localhost
ENV CUW_PORT=1883

ENTRYPOINT ["python", "-m", "cuw.cli"]
CMD ["--config", "/app/config.yaml"]