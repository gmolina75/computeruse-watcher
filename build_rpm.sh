#!/usr/bin/env bash
# computeruse-watcher — Empaquetador .rpm (RHEL/Fedora/openSUSE)
# Uso: bash build_rpm.sh
set -euo pipefail

VERSION="0.1.0"
ARCH="$(rpm --eval '%{_arch}')"
PKG="computeruse-watcher-${VERSION}-${ARCH}"
BUILD_DIR="/tmp/rpmbuild"
DIST_DIR="./dist"

echo "📦 Construyendo paquete .rpm v${VERSION}"

# Limpiar y crear estructura RPM
rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Crear fuente tarball
mkdir -p "/tmp/cuw-src"
cp -r src pyproject.toml README.md config.example.yaml "/tmp/cuw-src/"
tar -czf "${BUILD_DIR}/SOURCES/computeruse-watcher-${VERSION}.tar.gz" -C /tmp/cuw-src .

# Especificación RPM
cat > "${BUILD_DIR}/SPECS/computeruse-watcher.spec" <<EOF
Name:           computeruse-watcher
Version:        ${VERSION}
Release:        1%{?dist}
Summary:        Lightweight OS-agnostic computer usage telemetry agent

Group:          System Environment/Base
License:        Proprietary
URL:            https://github.com/gmolina75/computeruse-watcher
Source0:        %{name}-%{version}.tar.gz

Requires:       python3
Requires:       python3-pip
Requires:       systemd

%description
Cross-platform agent that tracks user logins, active applications,
and idle time, reporting to MQTT with a local SQLite cache.

%prep
%setup -q

%build
pip3 install -e .

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/computeruse-watcher
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/var/lib/computeruse-watcher

cp -r src %{buildroot}%{_libdir}/computeruse-watcher/
cp pyproject.toml %{buildroot}%{_libdir}/computeruse-watcher/
cp README.md %{buildroot}%{_libdir}/computeruse-watcher/
cp config.example.yaml %{buildroot}%{_libdir}/computeruse-watcher/config.yaml

cat > %{buildroot}%{_bindir}/cuw <<'EOFBIN'
#!/usr/bin/env bash
exec python3 -m cuw.cli --config %{_libdir}/computeruse-watcher/config.yaml "\$@"
EOFBIN
chmod +x %{buildroot}%{_bindir}/cuw

cat > %{buildroot}%{_unitdir}/computeruse-watcher.service <<'EOFSVC'
[Unit]
Description=Computer Use Watcher Agent
After=network.target

[Service]
Type=simple
ExecStart=%{_bindir}/cuw
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOFSVC

%files
%{_bindir}/cuw
%{_libdir}/computeruse-watcher
%{_unitdir}/computeruse-watcher.service
%dir /var/lib/computeruse-watcher

%post
systemctl daemon-reload
systemctl enable computeruse-watcher
echo "computeruse-watcher installed. Use 'systemctl start computeruse-watcher' to run."

%preun
if [ -f /run/systemd/system ]; then
    systemctl stop computeruse-watcher || true
fi

%postun
if [ -f /run/systemd/system ]; then
    systemctl disable computeruse-watcher || true
fi

%changelog
* Fri Oct 09 2026 Giancarlo Molina <giancarlo@example.com> - 0.1.0-1
- Initial release
EOF

# Construir RPM
cd "${BUILD_DIR}"
rpmbuild -bb SPECS/computeruse-watcher.spec

# Copiar a dist
mkdir -p "${DIST_DIR}"
cp RPMS/${ARCH}/computeruse-watcher-${VERSION}-${ARCH}.rpm "${DIST_DIR}/"

echo "✅ Paquete construido: ${DIST_DIR}/computeruse-watcher-${VERSION}-${ARCH}.rpm"
echo "Instalar con: sudo rpm -i ${DIST_DIR}/computeruse-watcher-${VERSION}-${ARCH}.rpm"