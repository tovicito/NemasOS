import requests
from pathlib import Path
from .logger import Logger
from .exceptions import DownloadError

try:
    from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def download_file(url: str, dest: Path, logger: Logger):
    """
    Descarga un archivo desde una URL a un destino, mostrando una barra de progreso.

    Args:
        url: La URL de descarga.
        dest: La ruta (Path) del archivo de destino.
        logger: La instancia del registrador.

    Raises:
        DownloadError: Si ocurre un error durante la descarga.
    """
    logger.info(f"Iniciando descarga desde [cyan]{url}[/cyan]")

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": f"TPT-Downloader/3.0"})

        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))

            # Asegurarse de que el directorio de destino existe
            dest.parent.mkdir(parents=True, exist_ok=True)

            if HAS_RICH:
                with Progress(
                    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                    BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    TransferSpeedColumn(),
                    "•",
                    TimeRemainingColumn(),
                    console=logger.user_console,
                ) as progress:
                    task = progress.add_task("Descargando...", total=total_size, filename=dest.name)
                    with open(dest, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
            else:
                # Fallback sin 'rich'
                logger.info("Rich no está instalado. Mostrando progreso simple.")
                bytes_descargados = 0
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bytes_descargados += len(chunk)
                        done = int(50 * bytes_descargados / total_size)
                        print(f"\r[{'=' * done}{' ' * (50-done)}] {bytes_descargados}/{total_size} bytes", end='')
                print() # Newline al final

        logger.success(f"Archivo guardado en [green]{dest}[/green]")

    except requests.exceptions.RequestException as e:
        logger.error(f"Fallo al descargar {url}: {e}")
        raise DownloadError(f"No se pudo descargar el archivo desde {url}.") from e
    except IOError as e:
        logger.error(f"Fallo al escribir el archivo en {dest}: {e}")
        raise DownloadError(f"No se pudo guardar el archivo en {dest}.") from e
