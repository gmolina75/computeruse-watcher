# computeruse-watcher — Instalador único para Windows
# Uso:
#   iex -File install.ps1
#   o
#   .\install.ps1

$ErrorActionPreference = "Stop"

$REPO_URL = "https://github.com/gmolina75/computeruse-watcher.git"
$INSTALL_DIR = "$env:USERPROFILE\computeruse-watcher"
$BROKER_HOST = "localhost"
$BROKER_PORT = "1883"
$BROKER_USER = ""
$BROKER_PASS = ""

Write-Host "🚀 computeruse-watcher — Instalador automático" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Detectar Python
$PYTHON = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PYTHON = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PYTHON = "py"
} else {
    Write-Error "❌ Python 3 no encontrado. Instálalo manualmente."
    exit 1
}

$PYTHON_VERSION = & $PYTHON --version
Write-Host "✅ Python encontrado: $PYTHON_VERSION"

# Clonar o actualizar
if (Test-Path $INSTALL_DIR) {
    Write-Host "📁 Directorio existente encontrado, actualizando..."
    Set-Location $INSTALL_DIR
    git pull origin main 2>$null
} else {
    Write-Host "📁 Clonando repositorio en $INSTALL_DIR..."
    git clone $REPO_URL $INSTALL_DIR
    Set-Location $INSTALL_DIR
}

# Crear entorno virtual
if (-not (Test-Path .venv)) {
    Write-Host "🔧 Creando entorno virtual..."
    & $PYTHON -m venv .venv
}

# Activar entorno virtual
& .\.venv\Scripts\Activate.ps1

# Instalar dependencias
Write-Host "📦 Instalando dependencias..."
& pip install --upgrade pip
& pip install -e .[dev]

# Configuración interactiva
Write-Host ""
Write-Host "⚙️  Configuración del broker MQTT"
Write-Host "   (Enter para usar valores por defecto)"
$BROKER_HOST = Read-Host "Broker host [localhost]"
if ([string]::IsNullOrEmpty($BROKER_HOST)) { $BROKER_HOST = "localhost" }

$BROKER_PORT = Read-Host "Broker port [1883]"
if ([string]::IsNullOrEmpty($BROKER_PORT)) { $BROKER_PORT = "1883" }

$BROKER_USER = Read-Host "Username (Enter para omitir)"
$BROKER_PASS = Read-Host "Password (Enter para omitir)"

# Escribir config.yaml
$configContent = @"
broker:
  host: $BROKER_HOST
  port: $BROKER_PORT
  username: "$BROKER_USER"
  password: "$BROKER_PASS"
  tls: false
"@
Set-Content -Path config.yaml -Value $configContent -Encoding UTF8

Write-Host ""
Write-Host "✅ Configuración guardada en config.yaml"

# Preguntar si quiere ejecutar ahora
$run_now = Read-Host "¿Ejecutar el agente ahora? [Y/n]"
if ([string]::IsNullOrEmpty($run_now) -or $run_now -eq "Y" -or $run_now -eq "y") {
    Write-Host "▶️  Ejecutando computeruse-watcher..."
    Write-Host "   (Ctrl+C para detener)"
    Write-Host ""
    & python -m cuw.cli --config config.yaml
} else {
    Write-Host " Para ejecutar más tarde:"
    Write-Host "   cd $INSTALL_DIR"
    Write-Host "   .\.venv\Scripts\Activate.ps1"
    Write-Host "   python -m cuw.cli --config config.yaml"
}