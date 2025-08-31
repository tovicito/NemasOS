import json
import hashlib
import requests
import threading
import os
from pathlib import Path

from packaging.version import parse as parse_version


from ..core.config import Configuracion
from ..utils import downloader, system
from ..utils.exceptions import *
from ..utils.i18n import _

# Importar todos los manejadores disponibles
from ..handlers.base_handler import BaseHandler
from ..handlers.deb_handler import DebHandler
from ..handlers.deb_xz_handler import DebXzHandler
from ..handlers.script_handler import ScriptHandler
from ..handlers.appimage_handler import AppImageHandler
from ..handlers.archive_handler import ArchiveHandler
from ..handlers.flatpak_handler import FlatpakHandler
from ..handlers.snap_handler import SnapHandler
from ..handlers.rpm_handler import RpmHandler
from ..handlers.exe_handler import ExeHandler
from ..handlers.msi_handler import MsiHandler
from ..handlers.alpine_apk_handler import AlpineApkHandler
from ..handlers.android_apk_handler import AndroidApkHandler
from ..handlers.powershell_handler import PowershellHandler
from ..handlers.nemas_patch_zip_handler import NemasPatchZipHandler
from ..handlers.meta_zip_handler import MetaZipHandler
import logging

class PackageManager:
    """
    Clase central que orquesta la búsqueda, instalación, desinstalación y actualización de paquetes.
    """
    def __init__(self, config: Configuracion, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.settings = self.config.load_settings()

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": f"TPT-PackageManager/5.4"})
        self._session.timeout = self.settings.get("network_timeout", 15)
        self._session.verify = self.settings.get("ssl_verify", True)

        self.progress_callback = None

        self.handler_map = {
            ".deb": DebHandler,
            ".deb.xz": DebXzHandler,
            ".sh": ScriptHandler,
            ".py": ScriptHandler,
            ".AppImage": AppImageHandler,
            ".tar.gz": ArchiveHandler,
            ".tgz": ArchiveHandler,
            ".tar.xz": ArchiveHandler,
            ".rpm": RpmHandler,
            ".ps1": PowershellHandler,
            ".exe": ExeHandler,
            ".msi": MsiHandler,
            ".apk": AndroidApkHandler,
            "flatpak": FlatpakHandler,
            "snap": SnapHandler,
            "alpine_apk": AlpineApkHandler,
            "android_apk": AndroidApkHandler,
            "nemas_patch_zip": NemasPatchZipHandler,
            "meta_zip": MetaZipHandler,
        }

    # ... el resto del código permanece igual, pero reemplaza:
    # self.logger.info(...) -> self.logger.info(...)
    # self.logger.error(...) -> self.logger.error(...)
    # self.logger.warning(...) -> self.logger.warning(...)
    # self.logger.success(...) -> self.logger.info(...) (o usa otro nivel si lo prefieres)
    # self.logger.debug(...) -> self.logger.debug(...)

    # Por ejemplo, donde diga:
    # self.logger.success(_("¡Paquete TPT '{}' instalado con éxito!").format(name))
    # reemplaza por:
    # self.logger.info(_("¡Paquete TPT '{}' instalado con éxito!").format(name))

    # No olvides cambiar el tipo del parámetro logger en __init__ y en todos los lugares donde se instancia PackageManager.
