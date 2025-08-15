#!/bin/bash

# package_real_apps.sh - Script maestro para empaquetar todas las aplicaciones reales por categoría.

set -e

# --- Configuración ---
VERSION="1.0"
ARCH="all"
APP_LIST_DIR="app_lists"

# Verificar que el script de construcción y el directorio de listas existan
if [ ! -f "build_deb.sh" ]; then
    echo "Error: El script 'build_deb.sh' no se encuentra. Asegúrate de que esté en el mismo directorio."
    exit 1
fi
if [ ! -d "$APP_LIST_DIR" ]; then
    echo "Error: El directorio '$APP_LIST_DIR' no se encuentra."
    exit 1
fi

echo "--- Iniciando el proceso de empaquetado de todas las aplicaciones reales ---"

# --- Iterar sobre cada lista de categorías y construir el paquete ---
for list_file in $(ls $APP_LIST_DIR/*.txt); do
    category=$(basename "$list_file" .txt)
    package_name="nemas-${category}-core"

    echo ""
    echo "================================================================="
    echo "Construyendo el paquete para la categoría: $category"
    echo "================================================================="

    ./build_deb.sh "$package_name" "$VERSION" "$ARCH" "$list_file"
done

echo ""
echo "--- Proceso de empaquetado finalizado con éxito. ---"
echo "Todos los paquetes .deb han sido creados."
