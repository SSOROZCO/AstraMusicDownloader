#!/bin/bash
set -e

echo "=== Construyendo Astra Music Downloader .deb ==="

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_DIR="$ROOT_DIR/packaging/AstraMusicDownloader"

# Crear la estructura de carpetas necesaria dentro del paquete
mkdir -p "$PKG_DIR/opt/AstraMusicDownloader"

# Copiar el archivo de código fuente principal renombrado al paquete
cp "$ROOT_DIR/src/AstraMusicDownloader.py" "$PKG_DIR/opt/AstraMusicDownloader/AstraMusicDownloader.py"

# Dar permisos de ejecución al script ejecutable
chmod +x "$PKG_DIR/opt/AstraMusicDownloader/AstraMusicDownloader.py"

# Asegurar permisos correctos para los archivos de control de Debian
chmod 755 "$PKG_DIR/DEBIAN/postinst"
chmod 644 "$PKG_DIR/DEBIAN/control"

# Empaquetar todo en el instalador .deb final
dpkg-deb --build --root-owner-group "$PKG_DIR" "$ROOT_DIR/AstraMusicDownloader_2.4_all.deb"

echo ""
echo "Listo: AstraMusicDownloader_2.4_all.deb"
echo "Instálalo con: sudo apt install ./AstraMusicDownloader_2.4_all.deb"
