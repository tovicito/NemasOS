#!/bin/bash
#
# gestor_servicios.sh - Script para gestionar servicios del sistema (Nemás OS)
#

# --- Validación de argumentos ---
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <acción> <servicio>"
    echo "Acciones disponibles: start, stop, restart, status"
    exit 1
fi

ACCION=$1
SERVICIO=$2

# --- Funciones ---
iniciar_servicio() {
    echo "Iniciando el servicio '$SERVICIO'..."
    sudo systemctl start "$SERVICIO"
    echo "Hecho."
}

detener_servicio() {
    echo "Deteniendo el servicio '$SERVICIO'..."
    sudo systemctl stop "$SERVICIO"
    echo "Hecho."
}

reiniciar_servicio() {
    echo "Reiniciando el servicio '$SERVICIO'..."
    sudo systemctl restart "$SERVICIO"
    echo "Hecho."
}

estado_servicio() {
    echo "Consultando el estado del servicio '$SERVICIO'..."
    sudo systemctl status "$SERVICIO"
}

# --- Lógica principal ---
echo "======================================="
echo "   Gestor de Servicios de Nemás OS"
echo "======================================="
echo

case "$ACCION" in
    start)
        iniciar_servicio
        ;;
    stop)
        detener_servicio
        ;;
    restart)
        reiniciar_servicio
        ;;
    status)
        estado_servicio
        ;;
    *)
        echo "Error: Acción no reconocida."
        echo "Acciones disponibles: start, stop, restart, status"
        exit 1
        ;;
esac

echo
echo "======================================="
echo "  Operación completada"
echo "======================================="
