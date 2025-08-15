#!/bin/bash

# build_deb.sh - Un script para empaquetar aplicaciones de Python en un .deb
# Uso: ./build_deb.sh <nombre-paquete> <version> <arquitectura> <archivo-lista-apps>

set -e

# --- Validación de Argumentos ---
if [ "$#" -ne 4 ]; then
    echo "Uso: $0 <nombre-paquete> <version> <arquitectura> <archivo-lista-apps>"
    exit 1
fi

PACKAGE_NAME=$1
VERSION=$2
ARCH=$3
APP_LIST_FILE=$4

if [ ! -f "$APP_LIST_FILE" ]; then
    echo "Error: El archivo de lista de aplicaciones '$APP_LIST_FILE' no fue encontrado."
    exit 1
fi

# --- Configuración de Directorios ---
PACKAGE_DIR="${PACKAGE_NAME}-${VERSION}"
DEBIAN_DIR="$PACKAGE_DIR/DEBIAN"
BIN_DIR="$PACKAGE_DIR/usr/bin"
DESKTOP_DIR="$PACKAGE_DIR/usr/share/applications"

# --- Limpieza y Creación de la Estructura ---
echo "--- [Info] Creando estructura para el paquete: $PACKAGE_NAME ---"
rm -rf "$PACKAGE_DIR"
mkdir -p "$DEBIAN_DIR" "$BIN_DIR" "$DESKTOP_DIR"

# --- Creación del archivo de control ---
# Extraer el grupo del nombre del paquete (p.ej. 'writer' de 'nemas-writer-core')
GROUP=$(echo $PACKAGE_NAME | cut -d'-' -f2)

cat > "$DEBIAN_DIR/control" << EOL
Package: $PACKAGE_NAME
Version: $VERSION
Architecture: $ARCH
Maintainer: Jules <jules@nemas.os>
Description: Un conjunto de aplicaciones de $GROUP para Nemas OS.
 Este paquete contiene una selección de herramientas de la categoría '$GROUP'.
Depends: python3, python3-pyqt5
EOL

# --- Procesamiento de Aplicaciones ---
echo "[Info] Empaquetando aplicaciones desde $APP_LIST_FILE..."
while IFS= read -r app_file; do
    if [ -z "$app_file" ]; then continue; fi

    basename=$(echo "$app_file" | sed 's/_gui.py//')
    cmdname="nemas-${basename//_/-}"

    echo "  -> Procesando: $app_file como $cmdname"

    # Copiar y hacer ejecutable
    cp "$app_file" "$BIN_DIR/$cmdname"
    chmod +x "$BIN_DIR/$cmdname"

    # Crear archivo .desktop
    name_human_readable=$(echo "$basename" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')
    desktop_file="$DESKTOP_DIR/$cmdname.desktop"

    cat > "$desktop_file" << EOL
[Desktop Entry]
Version=1.0
Name=$name_human_readable
Comment=Herramienta de $GROUP para Nemas OS
Exec=$cmdname
Icon=applications-utilities
Terminal=false
Type=Application
Categories=Utility;$GROUP;
EOL

done < "$APP_LIST_FILE"

# --- Construcción del Paquete ---
echo "[Info] Construyendo el paquete .deb..."
dpkg-deb --build "$PACKAGE_DIR"

echo "--- [Éxito] Paquete ${PACKAGE_DIR}.deb creado. ---"

# --- Limpieza ---
rm -rf "$PACKAGE_DIR"
echo "[Info] Directorio de construcción temporal eliminado."
