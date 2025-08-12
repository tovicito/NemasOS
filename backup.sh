#!/bin/bash
#
# backup.sh - Script para crear copias de seguridad (Nemás OS)
#

echo "======================================="
echo "   Utilidad de Backup de Nemás OS"
echo "======================================="
echo

# --- Validación de argumentos ---
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <directorio_origen> <directorio_destino>"
    echo "Ejemplo: $0 /home/usuario/documentos /home/usuario/backups"
    exit 1
fi

ORIGEN=$1
DESTINO=$2
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
NOMBRE_ARCHIVO="backup-$FECHA.tar.gz"
ARCHIVO_DESTINO="$DESTINO/$NOMBRE_ARCHIVO"

# --- Comprobar si el directorio de origen existe ---
if [ ! -d "$ORIGEN" ]; then
    echo "Error: El directorio de origen '$ORIGEN' no existe."
    exit 1
fi

# --- Comprobar si el directorio de destino existe, si no, crearlo ---
if [ ! -d "$DESTINO" ]; then
    echo "El directorio de destino '$DESTINO' no existe. Creándolo..."
    mkdir -p "$DESTINO"
fi

# --- Crear la copia de seguridad ---
echo "Iniciando copia de seguridad de '$ORIGEN'..."
echo "Destino: $ARCHIVO_DESTINO"
echo

tar -czvf "$ARCHIVO_DESTINO" "$ORIGEN"

echo
echo "======================================="
echo "  ¡Copia de seguridad creada con éxito!"
echo "  Archivo: $NOMBRE_ARCHIVO"
echo "======================================="
