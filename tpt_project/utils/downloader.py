import requests
from pathlib import Path
import logging
import sys
from .exceptions import DownloadError

def download_file(url: str, dest: Path, logger: logging.Logger):
    """
    Descarga un archivo desde una URL a un destino, mostrando un progreso de texto simple.
    Limpia los archivos parciales si la descarga falla.
    """
    logger.info(f"Iniciando descarga desde {url}")

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": f"TPT-Downloader/6.0"})

        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))

            dest.parent.mkdir(parents=True, exist_ok=True)

            bytes_descargados = 0
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bytes_descargados += len(chunk)
                    if total_size > 0:
                        done = int(50 * bytes_descargados / total_size)
                        # Imprimir en la misma línea para crear la barra de progreso
                        sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {bytes_descargados}/{total_size} bytes")
                        sys.stdout.flush()

            sys.stdout.write('\n') # Asegurar una nueva línea al final
            sys.stdout.flush()


        logger.info(f"Archivo guardado en {dest}")

    except (requests.exceptions.RequestException, IOError) as e:
        logger.error(f"Fallo al descargar o guardar {url}: {e}")
        if dest.exists():
            logger.warning(f"Limpiando archivo de descarga parcial: {dest}")
            try:
                dest.unlink()
            except OSError as unlink_e:
                logger.error(f"No se pudo limpiar el archivo parcial: {unlink_e}")
        raise DownloadError(f"No se pudo descargar o guardar el archivo desde {url}.") from e
