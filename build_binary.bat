@echo off
REM computeruse-watcher — Empaquetador de binario pre-compilado para Windows
REM Uso: build_binary.bat
setlocal

set VERSION=0.1.0
set DIST_DIR=dist
set BUILD_DIR=build_binary

echo [INFO] Construyendo binario pre-compilado v%VERSION%

REM Limpiar
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %BUILD_DIR% rmdir /s /q %BUILD_DIR%
mkdir %DIST_DIR%
mkdir %BUILD_DIR%

REM Instalar PyInstaller
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Crear spec file
echo # -*- mode: python ; coding: utf-8 -*- > %BUILD_DIR%\computeruse-watcher.spec
echo import sys >> %BUILD_DIR%\computeruse-watcher.spec
echo from PyInstaller.building.api import EXE, COLLECT, TREE >> %BUILD_DIR%\computeruse-watcher.spec
echo. >> %BUILD_DIR%\computeruse-watcher.spec
echo a = Analysis(['src\cuw\cli.py'], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     pathex=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     binaries=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     datas=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     hiddenimports=['cuw', 'cuw.core', 'cuw.platform_abstraction', 'cuw.network', 'cuw.daemon'], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     hookspath=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     runtime_hooks=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     excludes=[], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     win_no_prefer_redirects=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     win_private_assemblies=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     cipher=None, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo ) >> %BUILD_DIR%\computeruse-watcher.spec
echo. >> %BUILD_DIR%\computeruse-watcher.spec
echo pyz = PYZ(a.pure) >> %BUILD_DIR%\computeruse-watcher.spec
echo. >> %BUILD_DIR%\computeruse-watcher.spec
echo exe = EXE( ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     pyz, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     a.scripts, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     a.binaries, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     a.datas, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     [], ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     name='computeruse-watcher', ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     debug=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     bootloader_ignore_signals=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     strip=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     upx=True, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     console=True, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     disable_windowed_traceback=False, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     target_arch=None, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     codesign_identity=None, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo     entitlements_file=None, ^ >> %BUILD_DIR%\computeruse-watcher.spec
echo ) >> %BUILD_DIR%\computeruse-watcher.spec

REM Construir
cd %BUILD_DIR%
python -m PyInstaller computeruse-watcher.spec

REM Mover a dist
move dist\computeruse-watcher.exe %DIST_DIR%\computeruse-watcher-%VERSION%.exe

echo [INFO] Binario construido: %DIST_DIR%\computeruse-watcher-%VERSION%.exe
echo [INFO] Ejecutar con: %DIST_DIR%\computeruse-watcher-%VERSION%.exe