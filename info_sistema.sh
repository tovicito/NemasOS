#!/bin/bash
#
# info_sistema.sh - Muestra información relevante del sistema (Nemás OS)
#

echo "======================================="
echo "  Información del Sistema Nemás OS"
echo "======================================="
echo

echo "--- Sistema Operativo ---"
lsb_release -a
echo

echo "--- Kernel ---"
uname -r
echo

echo "--- Arquitectura ---"
uname -m
echo

echo "--- Información de la CPU ---"
lscpu | grep "Nombre del modelo"
lscpu | grep "CPU(s)" | head -n1
echo

echo "--- Memoria RAM ---"
free -h
echo

echo "--- Uso del Disco ---"
df -h /
echo

echo "======================================="
echo "  Fin del informe del sistema"
echo "======================================="
