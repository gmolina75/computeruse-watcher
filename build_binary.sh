#!/usr/bin/env bash
# computeruse-watcher — Empaquetador de binario pre-compilado con PyInstaller
# Uso: bash build_binary.sh
set -euo pipefail

VERSION="0.1.0"
DIST_DIR="./dist"
BUILD_DIR="./build_binary"

echo "📦 Construyendo binario pre-compilado v${VERSION}"

# Limpiar
rm -rf "${DIST_DIR}" "${BUILD_DIR}"
mkdir -p "${DIST_DIR}" "${BUILD_DIR}"

# Instalar PyInstaller
pip install --upgrade pip
pip install pyinstaller

# Crear spec file
cat > "${BUILD_DIR}/computeruse-watcher.spec" <<'EOF'
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.building.api import EXE, COLLECT, TREE

a = Analysis(
    ['src/cuw/cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['cuw', 'cuw.core', 'cuw.platform_abstraction', 'cuw.network', 'cuw.daemon'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='computeruse-watcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

EOF

# Construir
cd "${BUILD_DIR}"
pyinstaller computeruse-watcher.spec

# Mover a dist
mv dist/computeruse-watcher "${DIST_DIR}/computeruse-watcher-${VERSION}"

echo "✅ Binario construido: ${DIST_DIR}/computeruse-watcher-${VERSION}"
echo "Ejecutar con: ${DIST_DIR}/computeruse-watcher-${VERSION}"