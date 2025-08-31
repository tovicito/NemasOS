import requests
from pathlib import Path
import logging
from .exceptions import DownloadError

try:
    from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def download_file(url: str, dest: Path, logger: logging.Logger, progress_callback=None):
    """
    Descarga un archivo desde una URL a un destino, mostrando una barra de progreso.
    Limpia los archivos parciales si la descarga falla.
    """
    logger.info(f"Iniciando descarga desde [cyan]{url}[/cyan]")

    try:
        # Usar la sesión del PackageManager si está disponible, si no, crear una nueva
        # Esto es un placeholder, en la implementación real se pasaría la sesión.
        session = requests.Session()
        session.headers.update({"User-Agent": f"TPT-Downloader/5.0"})

        with session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))

            dest.parent.mkdir(parents=True, exist_ok=True)

            console = Console() if HAS_RICH else None

            if console:
                with Progress(
                    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                    BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%", "•",
                    TransferSpeedColumn(), "•", TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Descargando...", total=total_size, filename=dest.name)
                    with open(dest, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
                            if progress_callback:
                                progress_callback(progress.tasks[0].completed, total_size, "Downloading")
            else:
                logger.info("Mostrando progreso simple.")
                bytes_descargados = 0
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bytes_descargados += len(chunk)
                        if total_size > 0:
                            done = int(50 * bytes_descargados / total_size)
                            print(f"\r[{'=' * done}{' ' * (50-done)}] {bytes_descargados}/{total_size} bytes", end='')
                print()

        logger.info(f"Archivo guardado en [green]{dest}[/green]")

    except (requests.exceptions.RequestException, IOError) as e:
        logger.error(f"Fallo al descargar o guardar {url}: {e}")
        # Limpiar el archivo parcial si existe
        if dest.exists():
            logger.warning(f"Limpiando archivo de descarga parcial: {dest}")
            try:
                dest.unlink()
            except OSError as unlink_e:
                logger.error(f"No se pudo limpiar el archivo parcial: {unlink_e}")
        raise DownloadError(f"No se pudo descargar o guardar el archivo desde {url}.") from e
