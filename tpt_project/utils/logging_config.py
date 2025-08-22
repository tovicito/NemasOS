import logging
import sys

def setup_logging(debug=False):
    """
    Configura el logging básico para TPT.
    Imprime INFO y superior en stdout, y DEBUG si está activado.
    """
    level = logging.DEBUG if debug else logging.INFO

    # Usar un formato simple
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Crear un manejador que escriba en la consola
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Obtener el logger raíz y configurarlo
    logger = logging.getLogger("tpt")
    logger.setLevel(level)

    # Limpiar manejadores antiguos y añadir el nuevo
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

    return logger
