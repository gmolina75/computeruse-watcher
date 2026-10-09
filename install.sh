#!/usr/bin/env bash
# computeruse-watcher — Instalador único para Linux/macOS
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/gmolina75/computeruse-watcher/main/install.sh | bash
#   o
#   bash install.sh

set -euo pipefail

REPO_URL="https://github.com/gmolina75/computeruse-watcher.git"
INSTALL_DIR="${HOME}/computeruse-watcher"
BROKER_HOST="localhost"
BROKER_PORT="1883"
BROKER_USER=""
BROKER_PASS=""

echo "🚀 computeruse-watcher — Instalador automático"
echo "================================================"

# Detectar Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "❌ Python 3 no encontrado. Instálalo manualmente."
    exit 1
fi

$PYTHON --version
echo "✅ Python encontrado"

# Clonar o actualizar
if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Directorio existente encontrado, actualizando..."
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    echo "📁 Clonando repositorio en $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Crear entorno virtual
if [ ! -d ".venv" ]; then
    echo "🔧 Creando entorno virtual..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -e .[dev]

# Configuración interactiva
echo ""
echo "⚙️  Configuración del broker MQTT"
echo "   (Enter para usar valores por defecto)"
read -p "Broker host [localhost]: " input
BROKER_HOST="${input:-localhost}"
read -p "Broker port [1883]: " input
BROKER_PORT="${input:-1883}"
read -p "Username (Enter para omitir): " input
BROKER_USER="${input:-}"
read -p "Password (Enter para omitir): " input
BROKER_PASS="${input:-}"

# Escribir config.yaml
cat > config.yaml <<EOF
broker:
  host: ${BROKER_HOST}
  port: ${BROKER_PORT}
  username: "${BROKER_USER}"
  password: "${BROKER_PASS}"
  tls: false
EOF

echo ""
echo "✅ Configuración guardada en config.yaml"
echo ""

# Preguntar si quiere ejecutar ahora
read -p "¿Ejecutar el agente ahora? [Y/n]: " run_now
if [ -z "${run_now:-}" ] || [ "${run_now:-}" = "Y" ] || [ "${run_now:-}" = "y" ]; then
    echo "▶️  Ejecutando computeruse-watcher..."
    echo "   (Ctrl+C para detener)"
    echo ""
    python -m cuw.cli --config config.yaml
else
    echo " Para ejecutar más tarde:"
    echo "   cd $INSTALL_DIR"
    echo "   source .venv/bin/activate"
    echo "   python -m cuw.cli --config config.yaml"
fi