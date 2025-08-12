#!/bin/bash
#
# limpiador.sh - Script para limpiar el sistema de archivos innecesarios (Nemás OS)
#

echo "======================================="
echo "    Limpiador del Sistema Nemás OS"
echo "======================================="
echo
echo "Iniciando la limpieza de paquetes obsoletos y dependencias no utilizadas..."
sudo apt autoremove -y
echo
echo "Paquetes obsoletos eliminados."
echo "Iniciando la limpieza de la caché de paquetes..."
sudo apt clean
echo
echo "Caché de paquetes eliminada."
echo "======================================="
echo "  ¡Sistema limpiado con éxito!"
echo "======================================="
