#!/bin/bash
#
# actualizador.sh - Script para actualizar el sistema (Nemás OS)
#

echo "======================================="
echo "  Actualizador del Sistema Nemás OS"
echo "======================================="
echo
echo "Iniciando la actualización de la lista de paquetes..."
sudo apt update
echo
echo "Lista de paquetes actualizada."
echo "Iniciando la actualización de los paquetes instalados..."
sudo apt upgrade -y
echo
echo "======================================="
echo "  ¡Sistema actualizado con éxito!"
echo "======================================="
