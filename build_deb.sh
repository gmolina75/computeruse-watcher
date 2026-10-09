#!/usr/bin/env bash
# computeruse-watcher — Empaquetador .deb (Debian/Ubuntu)
# Uso: bash build_deb.sh
set -euo pipefail

VERSION="0.1.0"
ARCH="amd64"
PKG="computeruse-watcher_${VERSION}_${ARCH}"
BUILD_DIR="/tmp/${PKG}"
DIST_DIR="./dist"
DEB_FILE="${DIST_DIR}/${PKG}.deb"

echo "📦 Construyendo paquete .deb v${VERSION}"

# Limpiar y crear directorios
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}/DEBIAN" "${BUILD_DIR}/usr/local/bin" "${BUILD_DIR}/usr/local/lib/computeruse-watcher" "${BUILD_DIR}/etc/systemd/system" "${BUILD_DIR}/var/lib/computeruse-watcher"

# Copiar archivos
cp -r src "${BUILD_DIR}/usr/local/lib/computeruse-watcher/"
cp pyproject.toml "${BUILD_DIR}/usr/local/lib/computeruse-watcher/"
cp README.md "${BUILD_DIR}/usr/local/lib/computeruse-watcher/"
cp config.example.yaml "${BUILD_DIR}/usr/local/lib/computeruse-watcher/config.yaml"

# Crear script de entrada
cat > "${BUILD_DIR}/usr/local/bin/cuw" <<'EOF'
#!/usr/bin/env bash
exec python3 -m cuw.cli --config /usr/local/lib/computeruse-watcher/config.yaml "$@"
EOF
chmod +x "${BUILD_DIR}/usr/local/bin/cuw"

# Control file
cat > "${BUILD_DIR}/DEBIAN/control" <<EOF
Package: computeruse-watcher
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: Giancarlo Molina <giancarlo@example.com>
Description: Lightweight OS-agnostic computer usage telemetry agent
 Cross-platform agent that tracks user logins, active applications,
 and idle time, reporting to MQTT with a local SQLite cache.
EOF

# Postinst script
cat > "${BUILD_DIR}/DEBIAN/postinst" <<'EOF'
#!/usr/bin/env bash
set -e
# Instalar dependencias Python
pip3 install --quiet -e /usr/local/lib/computeruse-watcher
# Habilitar servicio systemd
systemctl daemon-reload
systemctl enable computeruse-watcher
echo "computeruse-watcher installed. Use 'systemctl start computeruse-watcher' to run."
EOF
chmod +x "${BUILD_DIR}/DEBIAN/postinst"

# Prerm script
cat > "${BUILD_DIR}/DEBIAN/prerm" <<'EOF'
#!/usr/bin/env bash
set -e
if [ -f /run/systemd/system ]; then
    systemctl stop computeruse-watcher || true
fi
EOF
chmod +x "${BUILD_DIR}/DEBIAN/prerm"

# Postrm script
cat > "${BUILD_DIR}/DEBIAN/postrm" <<'EOF'
#!/usr/bin/env bash
set -e
if [ -f /run/systemd/system ]; then
    systemctl disable computeruse-watcher || true
fi
EOF
chmod +x "${BUILD_DIR}/DEBIAN/postrm"

# systemd service
cat > "${BUILD_DIR}/etc/systemd/system/computeruse-watcher.service" <<'EOF'
[Unit]
Description=Computer Use Watcher Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cuw
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Construir paquete
mkdir -p "${DIST_DIR}"
dpkg-deb --build "${BUILD_DIR}" "${DEB_FILE}"

echo "✅ Paquete construido: ${DEB_FILE}"
echo "Instalar con: sudo dpkg -i ${DEB_FILE}"