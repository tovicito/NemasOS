#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import argparse
import requests
import hashlib
import json
import re
from datetime import datetime
from threading import Thread
from queue import Queue
import traceback # Importar traceback para manejar exc_info

# --- EXCEPCIONES PERSONALIZADAS PARA UN CONTROL DE ERRORES ROBUSTO ---
class TPTError(Exception):
    """Excepción base para errores de TPT."""
    pass

class TPTCriticalError(TPTError):
    """Excepción para errores críticos que impiden la continuación."""
    pass

class TPTUserCancelled(TPTError):
    """Excepción para cuando el usuario cancela una operación."""
    pass

# Intentar importar PyGObject para GTK
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib, Gdk
    import gi.repository.Gio as Gio # Importar Gio para ApplicationFlags
    HAS_GTK = True
except ImportError:
    HAS_GTK = False
    print("Advertencia: PyGObject (GTK) no encontrado. La GUI de TPT no estará disponible.")

# --- METADATOS Y CRÉDITOS ---
# GESTOR DE PAQUETES CREADO POR EL EQUIPO DE DESARROLLO DE NEMÁS OS
# EL PAQUETE NO ES REDISTRIBUIBLE LEGALMENTE
# CREDITOS A EL EQUIPO DE NEMÁS OS: Tomás y Neizan (NeMás OS)
# Uso: tpt (viene integrado en /.local/bin/tpt/tpt.py)
# Versión: TPT BETA (La Revolución Dinámica - Sin Índice Central)
# Usable en cualquier DISTRO BASADA EN DEBIAN o con dpkg/apt (aunque se puede usar sin eso)
# Esto viene incluido en casi todas las versiones de Nemás OS
# HECHO PARA NEMÁS OS

# --- CONSTANTES DE CONFIGURACIÓN ---
PAQUETES_COMPATIBLES = [".py", ".sh", ".deb", ".AppImage", ".tar.gz", ".flatpak", ".snap", ".nemas_pkg", ".flatpakref"]
RUTA_DESTINO_EJECUTABLES = "/usr/local/bin"
TPT_STATE_DIR = "/var/lib/tpt"
TPT_INSTALLED_PACKAGES_FILE = os.path.join(TPT_STATE_DIR, "installed_packages.json")
TPT_REPOS_LIST = 'tpt-repos.list'
ACTUAL_BRANCH_TXT = 'actual-branch.txt'
MIN_ESPACIO_LIBRE_MB = 1
DESKTOP_ENTRY_DIR = "/usr/local/share/applications"
TPT_LOG_FILE = "/var/log/tpt.log"
TPT_CACHE_DIR = "/var/cache/tpt"
TPT_URL_CACHE_DIR = os.path.join(TPT_CACHE_DIR, "url_cache") # Directorio para la caché de URLs

# --- REPOSITORIOS POR DEFECTO (para la primera ejecución) ---
DEFAULT_REPOS = [
    "tovicito/NemasOS", # Tu repositorio oficial (ej: https://github.com/tovicito/NemasOS/raw/regular/)
    "github.com/sindresorhus/awesome-cli-apps/raw/main/cli-apps/",
    "github.com/soimort/you-get/raw/master/src/",
    "github.com/Pylogmon/py_cli_tools/raw/main/",
    "github.com/sharkdp/fd/raw/master/contrib/completion/",
    "github.com/dylanaraps/neofetch/raw/master/",
    "github.com/jarun/nnn/raw/master/plugins/",
    "github.com/jesseduffield/lazygit/releases/download/v0.40.2/",
    "github.com/sharkdp/bat/releases/download/v0.24.0/",
    "github.com/ogham/exa/releases/download/v0.10.1/",
    "github.com/NemasOS-Community/Nemas-Packages/raw/main/"
]

# --- VARIABLES GLOBALES PARA LA GUI Y COMUNICACIÓN ENTRE HILOS ---
# Esta cola ahora es para la ventana de progreso, no para la principal
global_progress_output_queue = Queue()
global_app_instance = None # Referencia a la instancia de Gtk.Application

# --- CLASE PARA LOGGING Y DEBUGGING EXTREMO ---
class TPTLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.console_output = sys.stdout
        self.log_levels = {
            "DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4
        }
        self.current_log_level = self.log_levels["INFO"] # Nivel por defecto

        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'a') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Logger initialized.\n")
        except IOError as e:
            self.console_output.write(f"WARNING: No se pudo inicializar el log {self.log_file}: {e}. Los logs solo se mostrarán en consola/GUI.\n")
            self.log_file = None

    def set_log_level(self, level_name):
        if level_name.upper() in self.log_levels:
            self.current_log_level = self.log_levels[level_name.upper()]
            self.info(f"Nivel de log cambiado a: {level_name.upper()}")
        else:
            self.warning(f"Nivel de log desconocido: {level_name}. Manteniendo el nivel actual.")

    def _log(self, message, level_name="INFO", exc_info=False): # Añadir exc_info
        level_value = self.log_levels.get(level_name.upper(), 1)
        if level_value < self.current_log_level:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level_name.upper()}] {message}"

        if exc_info: # Si se pide información de excepción, añadirla
            log_entry += "\n" + traceback.format_exc()

        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry + "\n")
            except IOError as e:
                self.console_output.write(f"ERROR: No se pudo escribir en el log {self.log_file}: {e}\n")
                self.log_file = None

        # Ahora los logs van a la cola de la ventana de progreso
        if global_progress_output_queue:
            global_progress_output_queue.put(log_entry)

        # Siempre imprimir en consola si no hay GUI activa o si es un error crítico
        if not HAS_GTK or level_name.upper() in ["ERROR", "CRITICAL"]:
            self.console_output.write(log_entry + "\n")

    def debug(self, message, exc_info=False): self._log(message, "DEBUG", exc_info)
    def info(self, message, exc_info=False): self._log(message, "INFO", exc_info)
    def warning(self, message, exc_info=False): self._log(message, "WARNING", exc_info)
    def error(self, message, exc_info=False): self._log(message, "ERROR", exc_info)
    def critical(self, message, exc_info=False): self._log(message, "CRITICAL", exc_info)

logger = TPTLogger(TPT_LOG_FILE)

# --- FUNCIONES AUXILIARES ---

def es_root():
    """Verifica si el script se está ejecutando con privilegios de root."""
    return os.geteuid() == 0

def elevar_privilegios_con_pkexec():
    """Intenta elevar privilegios usando pkexec si no se está ejecutando como root."""
    if not es_root():
        logger.info("TPT necesita privilegios de root para operar. Intentando elevar con pkexec...")
        try:
            subprocess.run(['pkexec', sys.executable] + sys.argv, check=True)
            sys.exit(0) # Salir si la elevación fue exitosa y se relanzó el script
        except FileNotFoundError:
            raise TPTCriticalError("pkexec no encontrado. Asegúrate de que esté instalado y configurado. No se pueden elevar privilegios.")
        except subprocess.CalledProcessError as e:
            raise TPTCriticalError(f"Fallo al elevar privilegios con pkexec. Es posible que necesites configurar Polkit o ejecutar con 'sudo'. Error: {e.stderr}")
        except Exception as e:
            raise TPTCriticalError(f"Error inesperado al intentar elevar privilegios: {e}")

def mostrar_mensaje(mensaje, tipo="info", gui_output=None):
    """Muestra un mensaje al usuario, utilizando el logger."""
    # gui_output ya no se usa directamente aquí, los logs van a la cola global
    if tipo == "error":
        logger.error(mensaje)
    elif tipo == "advertencia":
        logger.warning(mensaje)
    elif tipo == "debug":
        logger.debug(mensaje)
    else:
        logger.info(mensaje)

def obtener_entrada_usuario(mensaje, gui_input_func=None):
    """Obtiene una entrada de usuario, desde consola o GUI."""
    if gui_input_func and HAS_GTK:
        # Esto se ejecuta en el hilo principal de GTK
        dialog_result_queue = Queue()
        GLib.idle_add(lambda: dialog_result_queue.put(gui_input_func("Entrada de TPT", mensaje)))
        result = dialog_result_queue.get() # Espera a que el diálogo devuelva un resultado
        if result is None:
            raise TPTUserCancelled("Operación cancelada por el usuario.")
        return result
    return input(f"{mensaje}: ").strip()

def verificar_espacio_libre(gui_output=None):
    """Verifica si hay suficiente espacio libre en el disco."""
    try:
        statvfs = os.statvfs('/')
        espacio_libre_bytes = statvfs.f_bfree * statvfs.f_frsize
        espacio_libre_mb = espacio_libre_bytes / (1024 * 1024)
        if espacio_libre_mb < MIN_ESPACIO_LIBRE_MB:
            raise TPTCriticalError(f"Espacio en disco insuficiente. Se requieren {MIN_ESPACIO_LIBRE_MB} MB. Disponible: {espacio_libre_mb:.2f} MB.")
        mostrar_mensaje(f"Espacio en disco disponible: {espacio_libre_mb:.2f} MB.")
    except Exception as e:
        mostrar_mensaje(f"No se pudo verificar el espacio en disco: {e}", tipo="advertencia")

def calcular_md5(ruta_archivo):
    """Calcula el hash MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    try:
        with open(ruta_archivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        logger.warning(f"Archivo no encontrado para MD5: {ruta_archivo}")
        return None

def crear_archivos_config_iniciales(gui_output=None):
    """Crea los archivos de configuración iniciales si no existen. Se asume que se ejecuta como root."""
    for d in [TPT_STATE_DIR, TPT_CACHE_DIR, TPT_URL_CACHE_DIR, os.path.dirname(TPT_LOG_FILE), DESKTOP_ENTRY_DIR]:
        try:
            os.makedirs(d, exist_ok=True)
            mostrar_mensaje(f"Directorio creado/verificado: {d}")
        except OSError as e:
            raise TPTCriticalError(f"Error al crear el directorio {d}: {e}. Asegúrate de tener permisos de root.")

    if not os.path.exists(TPT_REPOS_LIST):
        mostrar_mensaje(f"Creando '{TPT_REPOS_LIST}' con repositorios por defecto...")
        try:
            with open(TPT_REPOS_LIST, 'w') as f:
                for repo_url in DEFAULT_REPOS:
                    f.write(f"{repo_url}\n")
            mostrar_mensaje(f"'{TPT_REPOS_LIST}' creado con éxito.")
        except IOError as e:
            raise TPTCriticalError(f"Error al crear {TPT_REPOS_LIST}: {e}")

    if not os.path.exists(ACTUAL_BRANCH_TXT):
        mostrar_mensaje(f"Creando '{ACTUAL_BRANCH_TXT}' con rama 'regular' por defecto...")
        try:
            with open(ACTUAL_BRANCH_TXT, 'w') as f:
                f.write("regular\n")
            mostrar_mensaje(f"'{ACTUAL_BRANCH_TXT}' creado con éxito.")
        except IOError as e:
            raise TPTCriticalError(f"Error al crear {ACTUAL_BRANCH_TXT}: {e}")

def load_installed_packages():
    """Carga la lista de paquetes instalados desde el archivo JSON."""
    if not os.path.exists(TPT_INSTALLED_PACKAGES_FILE):
        return {}
    try:
        with open(TPT_INSTALLED_PACKAGES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        mostrar_mensaje(f"Advertencia: Archivo de paquetes instalados '{TPT_INSTALLED_PACKAGES_FILE}' corrupto. Se creará uno nuevo.", tipo="advertencia")
        return {}
    except IOError as e:
        mostrar_mensaje(f"Advertencia: No se pudo leer el archivo de paquetes instalados: {e}", tipo="advertencia")
        return {}

def save_installed_packages(installed_packages):
    """Guarda la lista de paquetes instalados en el archivo JSON."""
    try:
        with open(TPT_INSTALLED_PACKAGES_FILE, 'w') as f:
            json.dump(installed_packages, f, indent=4)
    except IOError as e:
        mostrar_mensaje(f"Error: No se pudo guardar la lista de paquetes instalados: {e}", tipo="error")

def crear_desktop_file(app_name, executable_path, icon_path=None, terminal=True, categories="Utility;Application;", comment="Aplicación instalada por TPT"):
    """
    Crea un archivo .desktop para la aplicación.
    """
    if not icon_path:
        icon_path = "utilities-terminal"

    desktop_file_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Exec={executable_path}
Icon={icon_path}
Terminal={'true' if terminal else 'false'}
Categories={categories}
Comment={comment}
StartupNotify=true
"""
    desktop_filename = f"{app_name}.desktop"
    desktop_filepath = os.path.join(DESKTOP_ENTRY_DIR, desktop_filename)

    try:
        with open(desktop_filepath, 'w') as f:
            f.write(desktop_file_content)
        subprocess.run(["chmod", "644", desktop_filepath], check=True, text=True)
        mostrar_mensaje(f"Archivo .desktop creado para '{app_name}' en '{desktop_filepath}'.")
        return desktop_filepath
    except Exception as e:
        mostrar_mensaje(f"Error al crear el archivo .desktop para '{app_name}': {e}", tipo="error")
        return None

def send_desktop_notification(title, message, icon="info"):
    """Envía una notificación de escritorio usando notify-send."""
    try:
        subprocess.run(["notify-send", "-i", icon, title, message], check=True)
    except FileNotFoundError:
        logger.warning("Comando 'notify-send' no encontrado. No se pueden enviar notificaciones de escritorio.")
    except Exception as e:
        logger.error(f"Error al enviar notificación de escritorio: {e}")

def comprobacion_extension(extension):
    """Verifica si la extensión es compatible."""
    if extension not in PAQUETES_COMPATIBLES:
        raise TPTError(f"ERROR: La extensión '{extension}' no es compatible con TPT. Extensiones soportadas: {', '.join(PAQUETES_COMPATIBLES)}")
    return extension

def preguntar_nombre_ejecutable(extension, gui_input_func=None):
    """Pregunta por el nombre del ejecutable y la ruta de destino para scripts."""
    nombre_ejecutable = obtener_entrada_usuario("Elija un nombre para el ejecutable (SIN ESPACIOS)", gui_input_func)
    if not nombre_ejecutable:
        raise TPTError("Nombre de ejecutable no puede estar vacío.")
    ruta_destino_ejecutable = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_ejecutable + extension)
    return nombre_ejecutable, ruta_destino_ejecutable

# --- FUNCIONES DE INSTALACIÓN ---

def instalar_paquete(nombre_app, extension, ruta_origen, nombre_ejecutable=None, ruta_destino=None, verificar_md5_oficial=False, metadata=None):
    """
    Instala un paquete en el sistema.
    :param metadata: Diccionario con metadatos del paquete (ej. de los archivos -des.txt, -dep.list, -vm.txt).
    """
    installed_packages = load_installed_packages()
    desktop_file_path = None

    pkg_metadata = metadata if metadata else {}
    icon_path = pkg_metadata.get('icon', None)
    terminal_app = pkg_metadata.get('terminal', True)
    categories = pkg_metadata.get('categories', "Utility;Application;")
    comment = pkg_metadata.get('comment', pkg_metadata.get('description', "Aplicación instalada por TPT"))
    dependencies = pkg_metadata.get('dependencies', [])

    if verificar_md5_oficial:
        md5_url = ruta_origen + ".md5"
        try:
            mostrar_mensaje(f"Descargando MD5 para verificación desde: {md5_url}")
            r = requests.get(md5_url, stream=True, timeout=10)
            r.raise_for_status()
            md5_remoto = r.text.strip()
            md5_local = calcular_md5(ruta_origen)

            if md5_local == md5_remoto:
                mostrar_mensaje("Verificación MD5 exitosa: El paquete es oficial y no ha sido alterado.")
            else:
                raise TPTError(f"Fallo en la verificación MD5. El paquete puede estar corrupto o no es oficial. MD5 local: {md5_local}, MD5 remoto: {md5_remoto}")
        except requests.exceptions.RequestException as e:
            mostrar_mensaje(f"No se pudo descargar el archivo MD5 o hubo un error de red: {e}. Procediendo sin verificación.", tipo="advertencia")
        except Exception as e:
            mostrar_mensaje(f"Error inesperado al verificar MD5: {e}. Procediendo sin verificación.", tipo="advertencia")

    if extension == ".deb":
        mostrar_mensaje(f"Instalando paquete .deb: {ruta_origen}")
        try:
            subprocess.run(["dpkg", "-i", ruta_origen], check=True, text=True)
            mostrar_mensaje("Intentando resolver dependencias con apt...")
            subprocess.run(["apt", "install", "-f"], check=True, text=True)
            mostrar_mensaje("Paquete .deb instalado y dependencias resueltas correctamente.")
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar el paquete .deb o sus dependencias: {e.stderr}")
        except FileNotFoundError:
            raise TPTError("Comandos 'dpkg' o 'apt' no encontrados. Asegúrate de que apt esté instalado.")

        if dependencies:
            mostrar_mensaje(f"Instalando dependencias adicionales: {', '.join(dependencies)}")
            try:
            # Add -y for non-interactive install
                subprocess.run(["apt", "install", "-y"] + dependencies, check=True, text=True)
                mostrar_mensaje("Dependencias adicionales instaladas correctamente.")
            except subprocess.CalledProcessError as e:
                mostrar_mensaje(f"Error al instalar dependencias adicionales: {e.stderr}", tipo="error")
        else:
            mostrar_mensaje("No se encontraron dependencias adicionales para este paquete.", tipo="advertencia")

        installed_packages[nombre_app] = {'extension': extension, 'ruta_origen': ruta_origen, 'instalado_a': 'dpkg'}

    elif extension in [".sh", ".py"]:
        if not nombre_ejecutable or not ruta_destino:
            raise TPTError("Faltan parámetros para instalar scripts (.sh/.py).")
        mostrar_mensaje(f"El paquete se moverá a: {ruta_destino}")
        time.sleep(1)

        try:
            subprocess.run(["chmod", "+x", ruta_origen], check=True, text=True)
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al dar permisos de ejecución al script: {e.stderr}")

        try:
            subprocess.run(["mv", ruta_origen, ruta_destino], check=True, text=True)
            mostrar_mensaje(f"Paquete '{nombre_ejecutable}{extension}' instalado como ejecutable.")

            desktop_file_path = crear_desktop_file(nombre_app, ruta_destino, icon_path=icon_path, terminal=terminal_app, categories=categories, comment=comment)

            installed_packages[nombre_app] = {
                'extension': extension,
                'ruta_origen': ruta_origen,
                'instalado_a': ruta_destino,
                'desktop_file': desktop_file_path
            }
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al mover el archivo al destino: {e.stderr}")
        except FileNotFoundError:
            raise TPTError("Comando 'mv' no encontrado. Algo anda mal en el sistema.")

    elif extension == ".AppImage":
        mostrar_mensaje(f"Instalando AppImage: {ruta_origen}")
        appimage_target_dir = "/opt/AppImages"
        os.makedirs(appimage_target_dir, exist_ok=True)
        appimage_name = os.path.basename(ruta_origen)
        final_appimage_path = os.path.join(appimage_target_dir, appimage_name)
        try:
            subprocess.run(["mv", ruta_origen, final_appimage_path], check=True, text=True)
            subprocess.run(["chmod", "+x", final_appimage_path], check=True, text=True)
            symlink_path = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_app)
            if os.path.exists(symlink_path):
                os.remove(symlink_path)
            os.symlink(final_appimage_path, symlink_path)
            mostrar_mensaje(f"AppImage '{appimage_name}' instalada en '{final_appimage_path}' y enlazada como '{nombre_app}'.")

            desktop_file_path = crear_desktop_file(nombre_app, symlink_path, icon_path=icon_path if icon_path else final_appimage_path, terminal=terminal_app, categories=categories, comment=comment)

            installed_packages[nombre_app] = {
                'extension': extension,
                'ruta_origen': ruta_origen,
                'instalado_a': final_appimage_path,
                'symlink': symlink_path,
                'desktop_file': desktop_file_path
            }
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar AppImage: {e.stderr}")
        except Exception as e:
            raise TPTError(f"Error inesperado al instalar AppImage: {e}")

    elif extension == ".tar.gz":
        mostrar_mensaje(f"Instalando desde tar.gz: {ruta_origen}")
        extract_dir = os.path.join("/opt", nombre_app)
        os.makedirs(extract_dir, exist_ok=True)
        try:
            subprocess.run(["tar", "-xzf", ruta_origen, "-C", extract_dir], check=True, text=True)
            mostrar_mensaje(f"Paquete tar.gz descomprimido en '{extract_dir}'.")

            ejecutable_path = os.path.join(extract_dir, nombre_app)
            if not os.path.exists(ejecutable_path):
                ejecutable_path = os.path.join(extract_dir, 'bin', nombre_app)

            if ejecutable_path and os.path.isfile(ejecutable_path):
                subprocess.run(["chmod", "+x", ejecutable_path], check=True, text=True)
                symlink_path = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_app)
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                os.symlink(ejecutable_path, symlink_path)
                mostrar_mensaje(f"Ejecutable '{ejecutable_path}' enlazado como '{nombre_app}'.")

                desktop_file_path = crear_desktop_file(nombre_app, symlink_path, icon_path=icon_path, terminal=terminal_app, categories=categories, comment=comment)

                installed_packages[nombre_app] = {
                    'extension': extension,
                    'ruta_origen': ruta_origen,
                    'instalado_a': extract_dir,
                    'ejecutable': ejecutable_path,
                    'symlink': symlink_path,
                    'desktop_file': desktop_file_path
                }
            else:
                mostrar_mensaje(f"No se pudo encontrar un ejecutable principal para '{nombre_app}' en '{extract_dir}'. Instalación incompleta.", tipo="advertencia")
                installed_packages[nombre_app] = {'extension': extension, 'ruta_origen': ruta_origen, 'instalado_a': extract_dir, 'ejecutable': None}

        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al descomprimir o instalar tar.gz: {e.stderr}")
        except Exception as e:
            raise TPTError(f"Error inesperado al instalar tar.gz: {e}")

    elif extension == ".nemas_pkg":
        mostrar_mensaje(f"Instalando paquete Nemas OS (.nemas_pkg): {ruta_origen}")
        extract_dir = os.path.join("/opt", nombre_app)
        os.makedirs(extract_dir, exist_ok=True)
        try:
            subprocess.run(["tar", "-xzf", ruta_origen, "-C", extract_dir], check=True, text=True)
            mostrar_mensaje(f"Paquete .nemas_pkg descomprimido en '{extract_dir}'.")

            install_script_path = os.path.join(extract_dir, "install.sh")
            main_executable_path = None
            if os.path.exists(os.path.join(extract_dir, nombre_app)):
                main_executable_path = os.path.join(extract_dir, nombre_app)
            elif os.path.exists(os.path.join(extract_dir, 'bin', nombre_app)):
                main_executable_path = os.path.join(extract_dir, 'bin', nombre_app)

            if os.path.exists(install_script_path):
                mostrar_mensaje(f"Ejecutando script de instalación: {install_script_path}")
                subprocess.run(["chmod", "+x", install_script_path], check=True, text=True)
                subprocess.run([install_script_path], check=True, text=True)
                mostrar_mensaje("Script de instalación .nemas_pkg ejecutado.")
                symlink_path = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_app)
                if main_executable_path and os.path.exists(main_executable_path) and not os.path.exists(symlink_path):
                     os.symlink(main_executable_path, symlink_path)
                     mostrar_mensaje(f"Symlink creado para '{nombre_app}' desde '{main_executable_path}'.")
                if main_executable_path:
                    desktop_file_path = crear_desktop_file(nombre_app, symlink_path if os.path.exists(symlink_path) else main_executable_path, icon_path=icon_path, terminal=terminal_app, categories=categories, comment=comment)
            elif main_executable_path and os.path.isfile(main_executable_path):
                subprocess.run(["chmod", "+x", main_executable_path], check=True, text=True)
                symlink_path = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_app)
                if os.path.exists(symlink_path):
                    os.remove(symlink_path)
                os.symlink(main_executable_path, symlink_path)
                mostrar_mensaje(f"Ejecutable '{main_executable_path}' enlazado como '{nombre_app}'.")
                desktop_file_path = crear_desktop_file(nombre_app, symlink_path, icon_path=icon_path, terminal=terminal_app, categories=categories, comment=comment)
            else:
                mostrar_mensaje(f"No se encontró script de instalación ni ejecutable principal para '{nombre_app}'. Instalación incompleta.", tipo="advertencia")

            installed_packages[nombre_app] = {
                'extension': extension,
                'ruta_origen': ruta_origen,
                'instalado_a': extract_dir,
                'desktop_file': desktop_file_path,
                'main_executable': main_executable_path,
                'symlink': symlink_path
            }

        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar .nemas_pkg: {e.stderr}")
        except Exception as e:
            raise TPTError(f"Error inesperado al instalar .nemas_pkg: {e}")


    elif extension == ".flatpak":
        mostrar_mensaje(f"Instalando Flatpak: {ruta_origen}")
        try:
            subprocess.run(["flatpak", "install", "-y", ruta_origen], check=True, text=True)
            mostrar_mensaje(f"Flatpak '{nombre_app}' instalado correctamente. Puede que necesites reiniciar la sesión.")
            installed_packages[nombre_app] = {'extension': extension, 'ruta_origen': ruta_origen, 'instalado_a': 'flatpak'}
        except FileNotFoundError:
            raise TPTError("Comando 'flatpak' no encontrado. Instala Flatpak en tu sistema.")
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar Flatpak: {e.stderr}")

    elif extension == ".flatpakref":
        mostrar_mensaje(f"Instalando Flatpak desde ref: {ruta_origen}")
        try:
            subprocess.run(["flatpak", "install", "--user", "--or-remote", ruta_origen], check=True, text=True)
            mostrar_mensaje(f"Flatpak ref '{nombre_app}' instalado correctamente. Puede que necesites reiniciar la sesión.")
            installed_packages[nombre_app] = {'extension': extension, 'ruta_origen': ruta_origen, 'instalado_a': 'flatpak_ref'}
        except FileNotFoundError:
            raise TPTError("Comando 'flatpak' no encontrado. Instala Flatpak en tu sistema.")
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar Flatpak ref: {e.stderr}")

    elif extension == ".snap":
        mostrar_mensaje(f"Instalando Snap: {ruta_origen}")
        try:
            subprocess.run(["snap", "install", ruta_origen, "--classic"], check=True, text=True)
            mostrar_mensaje(f"Snap '{nombre_app}' instalado correctamente. Puede que necesites reiniciar la sesión.")
            installed_packages[nombre_app] = {'extension': extension, 'ruta_origen': ruta_origen, 'instalado_a': 'snap'}
        except FileNotFoundError:
            raise TPTError("Comando 'snap' no encontrado. Instala snapd en tu sistema.")
        except subprocess.CalledProcessError as e:
            raise TPTError(f"Error al instalar Snap: {e.stderr}")

    else:
        raise TPTError("Tipo de paquete no manejado.")

    if ruta_origen and os.path.exists(ruta_origen) and ruta_origen.startswith('/tmp/'):
         try:
             os.remove(ruta_origen)
             mostrar_mensaje(f"Archivo temporal '{ruta_origen}' eliminado.")
         except OSError as e:
             mostrar_mensaje(f"No se pudo eliminar el archivo temporal '{ruta_origen}': {e}", tipo="advertencia")

    save_installed_packages(installed_packages)
    send_desktop_notification(f"TPT: {nombre_app} Instalado", f"El paquete '{nombre_app}' ha sido instalado con éxito.", icon="software-update-available")


def leer_urls_repositorio(archivo_repos):
    """Lee las URLs de repositorios desde el archivo tpt-repos.list."""
    if not os.path.exists(archivo_repos):
        raise TPTCriticalError(f"EL ARCHIVO DE REPOS {archivo_repos} NO EXISTE. No se pueden buscar paquetes remotos.")
    try:
        with open(archivo_repos, 'r') as f:
            return [linea.strip() for linea in f if linea.strip() and not linea.strip().startswith('#')]
    except IOError:
        raise TPTCriticalError(f"No se pudo leer el archivo de repositorios: {archivo_repos}.")

def leer_rama_actual(archivo_branch):
    """Lee la rama actual (regular/lss/dev/beta/med-regular) desde el archivo actual-branch.txt."""
    if not os.path.exists(archivo_branch):
        raise TPTCriticalError(f"El archivo de branch actual {archivo_branch} no existe. Asegúrate de que Nemas OS esté configurado.")
    try:
        with open(archivo_branch, 'r') as f:
            return f.read().strip()
    except IOError:
        raise TPTCriticalError(f"No se pudo leer el archivo de la rama actual: {archivo_branch}.")

def descargar_remoto(url, nombre_destino_temp):
    """Descarga un archivo desde una URL y lo guarda localmente."""
    mostrar_mensaje(f"Intentando descargar desde: {url}")
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()

        with open(nombre_destino_temp, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        mostrar_mensaje(f"Archivo '{nombre_destino_temp}' descargado con éxito.")
        return True
    except requests.exceptions.Timeout:
        mostrar_mensaje(f"Tiempo de espera agotado al descargar de {url}.", tipo="error")
        return False
    except requests.exceptions.ConnectionError as e:
        mostrar_mensaje(f"Error de conexión al descargar de {url}: {e}", tipo="error")
        return False
    except requests.exceptions.RequestException as e:
        mostrar_mensaje(f"Error al descargar de {url}: {e}", tipo="error")
        return False
    except Exception as e:
        mostrar_mensaje(f"Ocurrió un error inesperado durante la descarga: {e}", tipo="error")
        return False

def parse_vm_metadata(content):
    """Parsea el contenido de -vm.txt."""
    lines = content.strip().split('\n')
    isolated_install = False
    vm_type = None
    vm_image = None

    if lines:
        isolated_install = lines[0].strip().lower() == 'true'
        if isolated_install and len(lines) > 1:
            vm_type = lines[1].strip().lower()
            if len(lines) > 2:
                vm_image = lines[2].strip()
    return isolated_install, vm_type, vm_image

def save_url_cache(app_name, extension, urls_info):
    """Guarda las URLs exitosas en un archivo de caché local."""
    cache_file = os.path.join(TPT_URL_CACHE_DIR, f"url_{app_name}_{extension.replace('.', '')}.txt")
    try:
        os.makedirs(TPT_URL_CACHE_DIR, exist_ok=True)
        with open(cache_file, 'w') as f:
            for url_type, url in urls_info.items():
                f.write(f"{url_type}={url}\n")
        logger.info(f"URLs de '{app_name}{extension}' guardadas en caché: {cache_file}")
    except IOError as e:
        logger.warning(f"No se pudo guardar la caché de URLs para '{app_name}{extension}': {e}")

def load_url_cache(app_name, extension):
    """Carga las URLs de la caché local."""
    cache_file = os.path.join(TPT_URL_CACHE_DIR, f"url_{app_name}_{extension.replace('.', '')}.txt")
    urls_info = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                for line in f:
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        urls_info[parts[0]] = parts[1]
            logger.info(f"URLs de '{app_name}{extension}' cargadas de caché: {cache_file}")
            return urls_info
        except IOError as e:
            logger.warning(f"No se pudo cargar la caché de URLs para '{app_name}{extension}': {e}")
    return None

def check_url_exists(url):
    """Verifica si una URL existe y es accesible (sin descargar el contenido)."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def obtener_paquetes_disponibles_remoto(search_term):
    """
    Busca un paquete remoto por su nombre, probando URLs y descargando metadatos.
    Devuelve un diccionario de posibles coincidencias con sus metadatos (nombre_paquete: metadata).
    """
    mostrar_mensaje(f"Buscando '{search_term}' en repositorios remotos...")
    found_packages_dict = {} # Usamos un diccionario para asegurar la unicidad por nombre
    repos = leer_urls_repositorio(TPT_REPOS_LIST)
    rama = leer_rama_actual(ACTUAL_BRANCH_TXT)

    for repo_base_url_raw in repos:
        # Normalizar URL base para GitHub raw content
        if 'github.com' in repo_base_url_raw:
            repo_path_parts = repo_base_url_raw.split('github.com/')
            if len(repo_path_parts) > 1:
                repo_path = repo_path_parts[1].split('/raw/')[0].strip('/')
                repo_base_url = f"https://raw.githubusercontent.com/{repo_path}/"
            else:
                repo_base_url = repo_base_url_raw
        else:
            repo_base_url = repo_base_url_raw

        for ext in PAQUETES_COMPATIBLES:
            package_full_name = f"{search_term}{ext}"
            package_url = f"{repo_base_url}{rama}/{package_full_name}"

            # Si ya hemos encontrado este paquete, podemos saltar esta extensión para evitar duplicados.
            # Podríamos añadir lógica para priorizar extensiones si es necesario.
            if search_term in found_packages_dict:
                continue

            try:
                response = requests.head(package_url, timeout=5)
                if response.status_code == 200:
                    mostrar_mensaje(f"Encontrado '{package_full_name}' en {repo_base_url}")

                    metadata = {
                        'name': search_term,
                        'file_name': package_full_name,
                        'extension': ext,
                        'download_url': package_url,
                        'source_repo_base': repo_base_url,
                        'description': 'Sin descripción',
                        'dependencies': [],
                        'isolated_install': False,
                        'vm_type': None,
                        'vm_image': None,
                        'terminal': True
                    }

                    # Descargar y parsear -des.txt
                    des_url = f"{repo_base_url}{rama}/{search_term}-des.txt"
                    try:
                        des_content = requests.get(des_url, timeout=3).text
                        metadata['description'] = des_content.strip()
                    except requests.exceptions.RequestException:
                        logger.debug(f"No se encontró descripción en {des_url}")

                    # Descargar y parsear -dep.list
                    dep_url = f"{repo_base_url}{rama}/{search_term}-dep.list"
                    try:
                        dep_content = requests.get(dep_url, timeout=3).text
                        metadata['dependencies'] = [d.strip() for d in dep_content.strip().split('\n') if d.strip()]
                    except requests.exceptions.RequestException:
                        logger.debug(f"No se encontraron dependencias en {dep_url}")

                    # Descargar y parsear -vm.txt
                    vm_url = f"{repo_base_url}{rama}/{search_term}-vm.txt"
                    try:
                        vm_content = requests.get(vm_url, timeout=3).text
                        isolated, vm_type, vm_image = parse_vm_metadata(vm_content)
                        metadata['isolated_install'] = isolated
                        metadata['vm_type'] = vm_type
                        metadata['vm_image'] = vm_image
                    except requests.exceptions.RequestException:
                        logger.debug(f"No se encontró info de VM en {vm_url}")

                    found_packages_dict[search_term] = metadata # Añadir al diccionario

            except requests.exceptions.RequestException:
                logger.debug(f"URL no accesible o no existe: {package_url}")
                pass

    if not found_packages_dict:
        mostrar_mensaje(f"No se encontraron paquetes remotos para '{search_term}'.", tipo="advertencia")
    return found_packages_dict


def instalar_desde_remoto(nombre_app, progress_callback=None):
    """
    Busca el paquete, descarga e instala. Prioriza la caché de URLs.
    progress_callback es una función para actualizar la barra de progreso.
    """
    mostrar_mensaje(f"\n🚀 Buscando e instalando '{nombre_app}' desde repositorios remotos...")

    # Intentar cargar de la caché de URLs
    cached_urls_info = None
    best_cached_ext = None
    for ext in PAQUETES_COMPATIBLES:
        info = load_url_cache(nombre_app, ext)
        if info and check_url_exists(info.get('package_url', '')):
            cached_urls_info = info
            best_cached_ext = ext
            mostrar_mensaje(f"Usando URLs cacheadas para '{nombre_app}{ext}'.")
            break

    download_url = None
    extension_encontrada = None
    repo_base_url = None

    if cached_urls_info:
        download_url = cached_urls_info.get('package_url')
        extension_encontrada = best_cached_ext
        if 'raw.githubusercontent.com' in download_url:
            parts = download_url.split('/raw.githubusercontent.com/')
            if len(parts) > 1:
                repo_path_and_branch = parts[1].split('/', 2)
                if len(repo_path_and_branch) > 2:
                    repo_base_url = f"https://raw.githubusercontent.com/{repo_path_and_branch[0]}/{repo_path_and_branch[1]}/"
        elif 'github.com' in download_url:
            parts = download_url.split('github.com/')
            if len(parts) > 1:
                repo_path_and_branch = parts[1].split('/', 2)
                if len(repo_path_and_branch) > 2:
                    repo_base_url = f"https://raw.githubusercontent.com/{repo_path_and_branch[0]}/{repo_path_and_branch[1]}/"
        else:
            repo_base_url = '/'.join(download_url.split('/')[:-2]) + '/'

    else: # No caché o caché inválida, buscar en remoto
        repos = leer_urls_repositorio(TPT_REPOS_LIST)
        rama = leer_rama_actual(ACTUAL_BRANCH_TXT)

        for repo_base_url_raw in repos:
            if 'github.com' in repo_base_url_raw:
                repo_path_parts = repo_base_url_raw.split('github.com/')
                if len(repo_path_parts) > 1:
                    repo_path = repo_path_parts[1].split('/raw/')[0].strip('/')
                    repo_base_url = f"https://raw.githubusercontent.com/{repo_path}/"
                else:
                    repo_base_url = repo_base_url_raw
            else:
                repo_base_url = repo_base_url_raw

            for ext in PAQUETES_COMPATIBLES:
                package_full_name = f"{nombre_app}{ext}"
                current_download_url = f"{repo_base_url}{rama}/{package_full_name}"

                if check_url_exists(current_download_url):
                    download_url = current_download_url
                    extension_encontrada = ext
                    mostrar_mensaje(f"Encontrado '{package_full_name}' en {repo_base_url}")
                    break
            if download_url:
                break

    if not download_url:
        raise TPTError(f"No se pudo encontrar el paquete '{nombre_app}' en ningún repositorio compatible.")

    package_metadata = {
        'name': nombre_app,
        'description': 'Sin descripción',
        'dependencies': [],
        'isolated_install': False,
        'vm_type': None,
        'vm_image': None,
        'terminal': True
    }

    if cached_urls_info:
        if 'des_url' in cached_urls_info:
            try:
                package_metadata['description'] = requests.get(cached_urls_info['des_url'], timeout=3).text.strip()
            except requests.exceptions.RequestException: pass
        if 'dep_url' in cached_urls_info:
            try:
                dep_content = requests.get(cached_urls_info['dep_url'], timeout=3).text
                package_metadata['dependencies'] = [d.strip() for d in dep_content.strip().split('\n') if d.strip()]
            except requests.exceptions.RequestException: pass
        if 'vm_url' in cached_urls_info:
            try:
                vm_content = requests.get(cached_urls_info['vm_url'], timeout=3).text
                isolated, vm_type, vm_image = parse_vm_metadata(vm_content)
                package_metadata['isolated_install'] = isolated
                package_metadata['vm_type'] = vm_type
                package_metadata['vm_image'] = vm_image
            except requests.exceptions.RequestException: pass
    else:
        rama = leer_rama_actual(ACTUAL_BRANCH_TXT)
        des_url = f"{repo_base_url}{rama}/{nombre_app}-des.txt"
        dep_url = f"{repo_base_url}{rama}/{nombre_app}-dep.list"
        vm_url = f"{repo_base_url}{rama}/{nombre_app}-vm.txt"

        urls_to_cache = {
            'package_url': download_url,
            'des_url': des_url,
            'dep_url': dep_url,
            'vm_url': vm_url
        }

        try:
            des_content = requests.get(des_url, timeout=3).text
            package_metadata['description'] = des_content.strip()
        except requests.exceptions.RequestException:
            logger.debug(f"No se encontró descripción en {des_url}")

        try:
            dep_content = requests.get(dep_url, timeout=3).text
            package_metadata['dependencies'] = [d.strip() for d in dep_content.strip().split('\n') if d.strip()]
        except requests.exceptions.RequestException:
            logger.debug(f"No se encontraron dependencias en {dep_url}")

        try:
            vm_content = requests.get(vm_url, timeout=3).text
            isolated, vm_type, vm_image = parse_vm_metadata(vm_content)
            package_metadata['isolated_install'] = isolated
            package_metadata['vm_type'] = vm_type
            package_metadata['vm_image'] = vm_image
        except requests.exceptions.RequestException:
            logger.debug(f"No se encontró info de VM en {vm_url}")

        save_url_cache(nombre_app, extension_encontrada, urls_to_cache)

    # --- Lógica para VM/Aislamiento ---
    if package_metadata.get('isolated_install', False):
        mostrar_mensaje(f"'{nombre_app}' requiere instalación aislada. Orquestando VM/Contenedor...")
        temp_package_path = f"/tmp/{nombre_app}{extension_encontrada}"
        if not descargar_remoto(download_url, temp_package_path):
            raise TPTError(f"Fallo al descargar el paquete '{nombre_app}' para la instalación aislada.")

        instalar_en_ambiente_aislado(nombre_app, temp_package_path, package_metadata)
        if os.path.exists(temp_package_path):
            try:
                os.remove(temp_package_path)
                mostrar_mensaje(f"Archivo temporal '{temp_package_path}' eliminado.")
            except OSError as e:
                mostrar_mensaje(f"No se pudo eliminar el archivo temporal '{temp_package_path}': {e}", tipo="advertencia")
        return

    temp_package_path = f"/tmp/{nombre_app}{extension_encontrada}"
    if not descargar_remoto(download_url, temp_package_path):
        raise TPTError(f"No se pudo descargar el paquete '{nombre_app}'.")

    mostrar_mensaje(f"\nPaquete '{nombre_app}' descargado. Procediendo a la instalación...")

    if extension_encontrada in [".sh", ".py"]:
        nombre_ejecutable = nombre_app # Default to app name
        ruta_destino_script = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_ejecutable + extension_encontrada)
        instalar_paquete(nombre_app, extension_encontrada, temp_package_path, nombre_ejecutable, ruta_destino_script, verificar_md5_oficial=True, metadata=package_metadata)
    else:
        instalar_paquete(nombre_app, extension_encontrada, temp_package_path, verificar_md5_oficial=True, metadata=package_metadata)

def tpt_upgrade_all():
    """
    Actualiza todos los paquetes instalados por TPT.
    Re-descarga y re-instala para asegurar la última versión.
    """
    mostrar_mensaje("\n✨ Iniciando actualización de todos los paquetes instalados por TPT...")
    installed_packages = load_installed_packages()
    if not installed_packages:
        mostrar_mensaje("  No hay paquetes instalados por TPT para actualizar.")
        return

    for app_name, details in list(installed_packages.items()):
        mostrar_mensaje(f"\n🔄 Actualizando paquete: {app_name} ({details.get('extension', 'desconocido')})...")
        try:
            instalar_desde_remoto(app_name)
            mostrar_mensaje(f"✅ '{app_name}' actualizado correctamente.")
        except TPTError as e:
            mostrar_mensaje(f"❌ Fallo al actualizar '{app_name}': {e}. Continuando con el siguiente paquete.", tipo="error")
        except Exception as e:
            mostrar_mensaje(f"❌ Error inesperado al actualizar '{app_name}': {e}. Continuando.", tipo="error")

    mostrar_mensaje("\n✨ Proceso de actualización de TPT finalizado.")
    send_desktop_notification("TPT: Actualización Completada", "Todos los paquetes de TPT han sido actualizados.", icon="software-update-available")


def tpt_uninstall(nombre_app):
    """
    Desinstala un paquete instalado por TPT.
    """
    logger.debug(f"DEBUG: Iniciando desinstalación de '{nombre_app}'")
    mostrar_mensaje(f"\n🗑️ Intentando desinstalar '{nombre_app}'...")
    installed_packages = load_installed_packages()
    logger.debug(f"DEBUG: Paquetes instalados cargados: {list(installed_packages.keys())}")

    if nombre_app not in installed_packages:
        mostrar_mensaje(f"El paquete '{nombre_app}' no está registrado como instalado por TPT.", tipo="advertencia")
        logger.debug(f"DEBUG: '{nombre_app}' no encontrado en installed_packages.")
        return

    details = installed_packages[nombre_app]
    extension = details.get('extension')
    instalado_a = details.get('instalado_a')
    symlink = details.get('symlink')
    desktop_file = details.get('desktop_file')
    vm_id = details.get('vm_id')

    logger.debug(f"DEBUG: Detalles de '{nombre_app}': Extension={extension}, Instalado_a={instalado_a}, Symlink={symlink}, Desktop_file={desktop_file}, VM_ID={vm_id}")

    try:
        if vm_id:
            mostrar_mensaje(f"Desinstalando '{nombre_app}' de la VM/Contenedor '{vm_id}'...")
            desinstalar_de_ambiente_aislado(nombre_app, vm_id)
            mostrar_mensaje(f"✅ '{nombre_app}' desinstalado de la VM.")
        elif extension == ".deb":
            mostrar_mensaje(f"Desinstalando paquete .deb: {nombre_app}")
            subprocess.run(["dpkg", "-r", nombre_app], check=True, text=True)
            mostrar_mensaje(f"✅ Paquete .deb '{nombre_app}' desinstalado correctamente.")
        elif extension in [".sh", ".py"]:
            if instalado_a and os.path.exists(instalado_a):
                mostrar_mensaje(f"Eliminando ejecutable: {instalado_a}")
                os.remove(instalado_a)
                mostrar_mensaje(f"✅ Ejecutable '{nombre_app}{extension}' eliminado.")
            else:
                mostrar_mensaje(f"Advertencia: No se encontró el ejecutable para '{nombre_app}{extension}' en '{instalado_a}'.", tipo="advertencia")
        elif extension == ".AppImage":
            if instalado_a and os.path.exists(instalado_a):
                mostrar_mensaje(f"Eliminando AppImage: {instalado_a}")
                os.remove(instalado_a)
                if symlink and os.path.exists(symlink):
                    os.remove(symlink)
                    mostrar_mensaje(f"Symlink '{symlink}' eliminado.")
                mostrar_mensaje(f"✅ AppImage '{nombre_app}' desinstalada.")
            else:
                mostrar_mensaje(f"Advertencia: No se encontró la AppImage para '{nombre_app}' en '{instalado_a}'.", tipo="advertencia")
        elif extension == ".tar.gz" or extension == ".nemas_pkg":
            if instalado_a and os.path.exists(instalado_a):
                mostrar_mensaje(f"Eliminando directorio de instalación: {instalado_a}")
                subprocess.run(["rm", "-rf", instalado_a], check=True, text=True)
                if symlink and os.path.exists(symlink):
                    os.remove(symlink)
                    mostrar_mensaje(f"Symlink '{symlink}' eliminado.")
                mostrar_mensaje(f"✅ Paquete '{nombre_app}' desinstalado.")
            else:
                mostrar_mensaje(f"Advertencia: No se encontró el directorio de instalación para '{nombre_app}' en '{instalado_a}'.", tipo="advertencia")
        elif extension == ".flatpak" or extension == ".flatpakref":
            mostrar_mensaje(f"Desinstalando Flatpak: {nombre_app}")
            try:
                subprocess.run(["flatpak", "uninstall", "-y", nombre_app], check=True, text=True)
                mostrar_mensaje(f"✅ Flatpak '{nombre_app}' desinstalado correctamente.")
            except subprocess.CalledProcessError as e:
                raise TPTError(f"Error al desinstalar Flatpak: {e.stderr}")
        elif extension == ".snap":
            mostrar_mensaje(f"Desinstalando Snap: {nombre_app}")
            try:
                subprocess.run(["snap", "remove", nombre_app], check=True, text=True)
                mostrar_mensaje(f"✅ Snap '{nombre_app}' desinstalado correctamente.")
            except subprocess.CalledProcessError as e:
                raise TPTError(f"Error al desinstalar Snap: {e.stderr}")
        else:
            mostrar_mensaje(f"Tipo de paquete '{extension}' no manejado para desinstalación automática. Por favor, desinstale manualmente.", tipo="advertencia")
            return

        if desktop_file and os.path.exists(desktop_file):
            try:
                os.remove(desktop_file)
                mostrar_mensaje(f"Archivo .desktop '{desktop_file}' eliminado.")
            except OSError as e:
                mostrar_mensaje(f"No se pudo eliminar el archivo .desktop '{desktop_file}': {e}", tipo="advertencia")

        del installed_packages[nombre_app]
        save_installed_packages(installed_packages)
        mostrar_mensaje(f"✅ '{nombre_app}' desinstalado y eliminado del registro de TPT.")
        send_desktop_notification(f"TPT: {nombre_app} Desinstalado", f"El paquete '{nombre_app}' ha sido desinstalado con éxito.", icon="software-remove")

    except subprocess.CalledProcessError as e:
        logger.error(f"DEBUG: Error en subprocess al desinstalar '{nombre_app}': {e.stderr}", exc_info=True)
        raise TPTError(f"Error al desinstalar '{nombre_app}': {e.stderr}")
    except Exception as e:
        logger.critical(f"DEBUG: Error inesperado al desinstalar '{nombre_app}': {e}", exc_info=True)
        raise TPTError(f"Error inesperado al desinstalar '{nombre_app}': {e}")

def tpt_list_installed():
    """Muestra la lista de paquetes instalados por TPT."""
    mostrar_mensaje("\n📦 Paquetes instalados por TPT:")
    installed_packages = load_installed_packages()
    if not installed_packages:
        mostrar_mensaje("  No hay paquetes instalados por TPT.")
        return installed_packages # Return empty dict for GUI

    for app_name, details in installed_packages.items():
        ext = details.get('extension', 'N/A')
        instalado_a = details.get('instalado_a', 'N/A')
        desktop_file = details.get('desktop_file', 'No')
        vm_info = details.get('vm_id', 'No')
        mostrar_mensaje(f"  - {app_name} (Tipo: {ext}, Instalado en: {instalado_a}, .desktop: {'Sí' if desktop_file else 'No'}, VM: {vm_info})")
    return installed_packages

def tpt_fix_broken():
    """Intenta reparar paquetes .deb rotos o dependencias faltantes."""
    mostrar_mensaje("\n🔧 Intentando reparar paquetes rotos y dependencias...")
    try:
        subprocess.run(["apt", "install", "-f", "-y"], check=True, text=True)
        mostrar_mensaje("✅ Proceso de reparación finalizado.")
        send_desktop_notification("TPT: Reparación Completada", "Se intentó reparar paquetes rotos.", icon="dialog-information")
    except FileNotFoundError:
        raise TPTError("Comando 'apt' no encontrado. Asegúrate de que apt esté instalado.")
    except subprocess.CalledProcessError as e:
        raise TPTError(f"Error durante el proceso de reparación: {e.stderr}")
    except Exception as e:
        raise TPTError(f"Error inesperado al intentar reparar: {e}")

# --- FUNCIONES DE VIRTUALIZACIÓN (CONCEPTUAL/BÁSICO) ---

def _run_command_in_vm(vm_name, command, capture_output=False):
    """Ejecuta un comando dentro de una VM/Contenedor LXC."""
    logger.debug(f"Ejecutando comando en VM '{vm_name}': {command}")
    try:
        result = subprocess.run(["lxc", "exec", vm_name, "--"] + command.split(), check=True, text=True, capture_output=capture_output)
        if capture_output:
            return result.stdout.strip()
        return True
    except FileNotFoundError:
        raise TPTError("Comando 'lxc' no encontrado. Instala LXC para usar la virtualización.")
    except subprocess.CalledProcessError as e:
        raise TPTError(f"Error al ejecutar comando en VM '{vm_name}': {e.stderr}")
    except Exception as e:
        raise TPTError(f"Error inesperado al interactuar con VM '{vm_name}': {e}")

def _create_lxc_container(vm_name, image="ubuntu:22.04"):
    """Crea un nuevo contenedor LXC."""
    mostrar_mensaje(f"Creando contenedor LXC '{vm_name}' con imagen '{image}'...")
    try:
        subprocess.run(["lxc", "launch", image, vm_name], check=True, text=True)
        mostrar_mensaje(f"Contenedor '{vm_name}' creado y lanzado.")
        time.sleep(5)
        return True
    except subprocess.CalledProcessError as e:
        raise TPTError(f"Error al crear/lanzar contenedor LXC: {e.stderr}")

def _delete_lxc_container(vm_name):
    """Elimina un contenedor LXC."""
    mostrar_mensaje(f"Deteniendo y eliminando contenedor LXC '{vm_name}'...")
    try:
        subprocess.run(["lxc", "stop", vm_name], check=True, text=True)
        subprocess.run(["lxc", "delete", vm_name], check=True, text=True)
        mostrar_mensaje(f"Contenedor '{vm_name}' eliminado.")
        return True
    except subprocess.CalledProcessError as e:
        raise TPTError(f"Error al detener/eliminar contenedor LXC: {e.stderr}")

def instalar_en_ambiente_aislado(nombre_app, temp_package_path, package_metadata):
    """
    Orquesta la instalación de un paquete en un ambiente aislado (LXC por ahora).
    """
    vm_name = f"tpt-vm-{nombre_app}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    vm_type = package_metadata.get('vm_type', 'lxc')
    vm_image = package_metadata.get('vm_image', 'ubuntu:22.04')

    if vm_type == 'lxc':
        if not _create_lxc_container(vm_name, vm_image):
            raise TPTError(f"Fallo al crear el contenedor LXC para '{nombre_app}'.")

        mostrar_mensaje(f"Copiando '{temp_package_path}' a '{vm_name}:/tmp/'...")
        try:
            subprocess.run(["lxc", "file", "push", temp_package_path, f"{vm_name}/tmp/{os.path.basename(temp_package_path)}"], check=True, text=True)
            mostrar_mensaje("Paquete copiado al contenedor.")
        except subprocess.CalledProcessError as e:
            _delete_lxc_container(vm_name) # Clean up
            raise TPTError(f"Error al copiar paquete al contenedor: {e.stderr}")

        mostrar_mensaje(f"Instalando '{nombre_app}' dentro del contenedor '{vm_name}'...")
        pkg_in_vm_path = f"/tmp/{os.path.basename(temp_package_path)}"

        extension = os.path.splitext(temp_package_path)[1]

        if extension == ".deb":
            if not _run_command_in_vm(vm_name, f"apt update && dpkg -i {pkg_in_vm_path}") or \
               not _run_command_in_vm(vm_name, "apt install -f -y"):
                _delete_lxc_container(vm_name)
                raise TPTError(f"Fallo al instalar .deb en VM.")
        elif extension in [".sh", ".py"]:
            executable_name_in_vm = nombre_app
            if not _run_command_in_vm(vm_name, f"chmod +x {pkg_in_vm_path}") or \
               not _run_command_in_vm(vm_name, f"mv {pkg_in_vm_path} /usr/local/bin/{executable_name_in_vm}"):
                _delete_lxc_container(vm_name)
                raise TPTError(f"Fallo al instalar script en VM.")
        elif extension == ".AppImage":
            appimage_path_in_vm = f"/opt/AppImages/{os.path.basename(temp_package_path)}"
            if not _run_command_in_vm(vm_name, f"mkdir -p /opt/AppImages && mv {pkg_in_vm_path} {appimage_path_in_vm}") or \
               not _run_command_in_vm(vm_name, f"chmod +x {appimage_path_in_vm}"):
                _delete_lxc_container(vm_name)
                raise TPTError(f"Fallo al instalar AppImage en VM.")
            package_metadata['executable_path'] = appimage_path_in_vm
        else:
            _delete_lxc_container(vm_name)
            raise TPTError(f"Tipo de paquete '{extension}' no soportado para instalación en VM (solo .deb/.sh/.py/.AppImage por ahora).")

        mostrar_mensaje(f"'{nombre_app}' instalado con éxito en el contenedor '{vm_name}'.")

        wrapper_script_path = os.path.join(RUTA_DESTINO_EJECUTABLES, f"run-{nombre_app}-vm")
        executable_in_vm = package_metadata.get('executable_path', nombre_app)

        with open(wrapper_script_path, 'w') as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"lxc exec {vm_name} -- {executable_in_vm} \"$@\"\n")
        subprocess.run(["chmod", "+x", wrapper_script_path], check=True)

        desktop_file_path = crear_desktop_file(
            nombre_app,
            wrapper_script_path,
            icon_path=package_metadata.get('icon', None),
            terminal=package_metadata.get('terminal', True),
            categories=package_metadata.get('categories', "Utility;Application;"),
            comment=package_metadata.get('description', f"Aplicación '{nombre_app}' (aislada en VM {vm_name})")
        )

        installed_packages = load_installed_packages()
        installed_packages[nombre_app] = {
            'extension': extension,
            'ruta_origen': temp_package_path,
            'instalado_a': 'isolated_vm',
            'vm_id': vm_name,
            'desktop_file': desktop_file_path,
            'wrapper_script': wrapper_script_path,
            'vm_type': vm_type,
            'vm_image': vm_image
        }
        save_installed_packages(installed_packages)
        send_desktop_notification(f"TPT: {nombre_app} Instalado (VM)", f"'{nombre_app}' ha sido instalado en un entorno aislado.", icon="software-update-available")

    elif vm_type == 'qemu':
        mostrar_mensaje(f"Instalación en VM QEMU para '{nombre_app}' (Lógica pendiente, muy compleja).", tipo="advertencia")
        send_desktop_notification(f"TPT: {nombre_app} Instalado (QEMU)", f"'{nombre_app}' ha sido instalado en una VM QEMU (simulado).", icon="dialog-information")
        installed_packages = load_installed_packages()
        installed_packages[nombre_app] = {
            'extension': os.path.splitext(temp_package_path)[1],
            'ruta_origen': temp_package_path,
            'instalado_a': 'isolated_qemu',
            'vm_id': 'qemu_simulated_vm',
            'desktop_file': None,
            'wrapper_script': None,
            'vm_type': vm_type,
            'vm_image': vm_image
        }
        save_installed_packages(installed_packages)

    else:
        raise TPTError(f"Tipo de VM desconocido: {vm_type}")

def desinstalar_de_ambiente_aislado(nombre_app, vm_id):
    """Desinstala un paquete de un ambiente aislado (LXC por ahora)."""
    installed_packages = load_installed_packages()
    details = installed_packages.get(nombre_app, {})
    wrapper_script = details.get('wrapper_script')
    desktop_file = details.get('desktop_file')
    vm_type = details.get('vm_type')

    if vm_type == 'lxc':
        if wrapper_script and os.path.exists(wrapper_script):
            os.remove(wrapper_script)
            mostrar_mensaje(f"Wrapper script '{wrapper_script}' eliminado.")

        if desktop_file and os.path.exists(desktop_file):
            os.remove(desktop_file)
            mostrar_mensaje(f"Archivo .desktop '{desktop_file}' eliminado.")

        apps_in_this_vm = [k for k, v in installed_packages.items() if v.get('vm_id') == vm_id and k != nombre_app]
        if not apps_in_this_vm:
            _delete_lxc_container(vm_id)
        else:
            mostrar_mensaje(f"Contenedor '{vm_id}' no eliminado, aún contiene otras aplicaciones: {', '.join(apps_in_this_vm)}", tipo="advertencia")

    elif vm_type == 'qemu':
        mostrar_mensaje(f"Desinstalación de VM QEMU para '{nombre_app}' (Lógica pendiente).", tipo="advertencia")
        if wrapper_script and os.path.exists(wrapper_script):
            os.remove(wrapper_script)
            mostrar_mensaje(f"Wrapper script '{wrapper_script}' eliminado.")

        if desktop_file and os.path.exists(desktop_file):
            os.remove(desktop_file)
            mostrar_mensaje(f"Archivo .desktop '{desktop_file}' eliminado.")
    else:
        raise TPTError(f"Tipo de VM desconocido para desinstalación: {vm_type}")


# --- CLASE PARA LA VENTANA DE PROGRESO DE INSTALACIÓN ---
if HAS_GTK:
    class InstallationProgressWindow(Gtk.Window):
        def __init__(self, parent_window, operation_name="Operación", app_name=""):
            # Título dinámico
            title_text = f"TPT - {operation_name}"
            if app_name:
                title_text += f": {app_name}"

            Gtk.Window.__init__(self, title=title_text)
            self.set_transient_for(parent_window)
            self.set_modal(True)
            self.set_default_size(500, 400)
            self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
            self.set_resizable(True)
            self.set_decorated(True) # Show title bar and close button

            # CSS Styling for the progress window
            css_provider = Gtk.CssProvider()
            css = b"""
            window {
                background-color: #282c34; /* Fondo oscuro */
                border-radius: 10px;
            }
            label {
                color: #abb2bf; /* Texto claro */
                font-family: "Inter", sans-serif;
            }
            progressbar {
                background-color: #4b5263;
                border-radius: 5px;
            }
            progressbar trough {
                background-color: #4b5263;
                border-radius: 5px;
            }
            progressbar progress {
                background-color: #98c379; /* Verde para progreso */
                border-radius: 5px;
            }
            spinner {
                color: #61afef; /* Color del spinner */
            }
            textview {
                background-color: #3e4451;
                color: #abb2bf;
                border-radius: 8px;
                padding: 5px;
                border: 1px solid #4b5263;
            }
            .progress-label {
                font-weight: bold;
                font-size: 1.1em;
                margin-bottom: 10px;
            }
            """
            css_provider.load_from_data(css)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            vbox.set_margin_top(20)
            vbox.set_margin_bottom(20)
            vbox.set_margin_start(20)
            vbox.set_margin_end(20)
            self.add(vbox)

            self.status_label = Gtk.Label(label="Iniciando operación...")
            self.status_label.get_style_context().add_class("progress-label")
            vbox.pack_start(self.status_label, False, False, 0)

            self.progress_bar = Gtk.ProgressBar()
            self.progress_bar.set_fraction(0.0)
            self.progress_bar.set_text("0%")
            self.progress_bar.set_show_text(True)
            vbox.pack_start(self.progress_bar, False, False, 0)

            self.spinner = Gtk.Spinner()
            self.spinner.set_size_request(32, 32)
            self.spinner.start()
            vbox.pack_start(self.spinner, False, False, 0)

            self.output_text_buffer = Gtk.TextBuffer()
            self.output_text_view = Gtk.TextView(buffer=self.output_text_buffer)
            self.output_text_view.set_editable(False)
            self.output_text_view.set_cursor_visible(False)
            self.output_text_view.set_wrap_mode(Gtk.WrapMode.WORD)

            self.output_text_buffer.create_tag("info", foreground="#abb2bf")
            self.output_text_buffer.create_tag("success", foreground="#98c379")
            self.output_text_buffer.create_tag("warning", foreground="#e5c07b")
            self.output_text_buffer.create_tag("error", foreground="#e06c75")
            self.output_text_buffer.create_tag("debug", foreground="#62b6b7")

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.add(self.output_text_view)
            vbox.pack_start(scrolled_window, True, True, 0)

            self.connect("delete-event", self._on_delete_event)
            GLib.idle_add(self._process_queue) # Start processing queue for logs

        def _on_delete_event(self, widget, event):
            # Prevent closing the window manually during an operation
            # The window should only close when the operation finishes or errors out.
            # We can add a confirmation dialog here if needed, but for now, just prevent close.
            # If the operation is still running, return True to prevent closing.
            # If the operation is finished, return False to allow closing.
            # For simplicity, we assume the window is destroyed by the main thread after operation.
            return True # Prevent closing by user action

        def _process_queue(self):
            """Procesa mensajes de la cola y los muestra en el TextView."""
            while not global_progress_output_queue.empty():
                message = global_progress_output_queue.get()
                iter_end = self.output_text_buffer.get_end_iter()

                if "[ERROR]" in message or "[CRITICAL]" in message:
                    self.output_text_buffer.insert(iter_end, message + "\n", 'error')
                elif "[WARNING]" in message:
                    self.output_text_buffer.insert(iter_end, message + "\n", 'warning')
                elif "[INFO]" in message:
                    self.output_text_buffer.insert(iter_end, message + "\n", 'info')
                elif "[DEBUG]" in message:
                    self.output_text_buffer.insert(iter_end, message + "\n", 'debug')
                else:
                    self.output_text_buffer.insert(iter_end, message + "\n")

                self.output_text_view.scroll_to_iter(self.output_text_buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
            return True # Keep calling this function

        def update_progress(self, fraction, text):
            GLib.idle_add(self.progress_bar.set_fraction, fraction)
            GLib.idle_add(self.progress_bar.set_text, text)
            GLib.idle_add(self.status_label.set_text, f"Estado: {text}")

        def set_finished(self, success=True, message="Operación Finalizada."):
            GLib.idle_add(self.spinner.stop)
            if success:
                GLib.idle_add(self.status_label.set_text, f"✅ {message}")
                GLib.idle_add(self.progress_bar.set_fraction, 1.0)
                GLib.idle_add(self.progress_bar.set_text, "100% - Completado")
            else:
                GLib.idle_add(self.status_label.set_text, f"❌ {message}")
                GLib.idle_add(self.progress_bar.set_fraction, 0.0) # Or keep last state
                GLib.idle_add(self.progress_bar.set_text, "Fallo")
            # We don't hide/destroy immediately, let the main thread handle it for user to see final message
            # For now, we allow the window to be closed by the main thread after a short delay or user action.
            # For "auto-close", the main thread will call self.destroy() after some delay.

# --- CLASE PRINCIPAL DE LA GUI (GTK) ---

if HAS_GTK:
    class TPTGUI(Gtk.Application):
        def __init__(self):
            # Usar Gio.ApplicationFlags.FLAGS_NONE
            Gtk.Application.__init__(self, application_id="org.nemasos.tpt",
                                     flags=Gio.ApplicationFlags.FLAGS_NONE)
            self.connect("activate", self.on_activate)
            self.available_packages_data = {} # Almacena los resultados de la búsqueda
            self.installed_packages_data = {}
            self.selected_package_details = {} # Detalles del paquete seleccionado para mostrar en el panel

        @staticmethod
        def show_message_dialog(parent, title, message, message_type):
            dialog = Gtk.MessageDialog(
                parent=parent,
                flags=0,
                message_type=message_type,
                buttons=Gtk.ButtonsType.OK,
                text=title,
                secondary_text=message
            )
            dialog.run()
            dialog.destroy()

        def _show_input_dialog(self, title, prompt):
            """Muestra un diálogo de entrada de texto y devuelve la cadena introducida."""
            dialog = Gtk.Dialog(title, self.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

            box = dialog.get_content_area()
            label = Gtk.Label(label=prompt)
            box.pack_start(label, True, True, 0)

            entry = Gtk.Entry()
            entry.set_hexpand(True)
            box.pack_start(entry, True, True, 0)
            box.show_all()

            response = dialog.run()
            text = entry.get_text().strip()
            dialog.destroy()

            if response == Gtk.ResponseType.OK and text:
                return text
            return None


        def on_activate(self, app):
            self.window = Gtk.ApplicationWindow(application=app, title="TPT - Gestor de Paquetes de Nemas OS (La Revolución)")
            self.window.set_default_size(1000, 750) # Increased size for details panel
            self.window.set_position(Gtk.WindowPosition.CENTER)
            self.window.connect("destroy", self.on_window_destroy)

            css_provider = Gtk.CssProvider()
            css = b"""
            window { background-color: #282c34; }
            headerbar { background-color: #3e4451; }
            label { color: #abb2bf; font-family: "Inter", sans-serif; }
            button {
                background-color: #61afef; color: white; border-radius: 8px; padding: 8px 15px;
                font-weight: bold; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: background-color 0.5s ease; /* Smooth transition for color change */
            }
            button:hover { background-color: #528bff; }
            button:active { background-color: #467bd8; box-shadow: inset 0 1px 3px rgba(0,0,0,0.3); }

            .install-button-progress {
                background-color: #98c379; /* Green for progress */
            }
            .install-button-finished {
                background-color: #28a745; /* Darker green for finished */
            }
            .install-button-error {
                background-color: #dc3545; /* Red for error */
            }

            entry, textview {
                background-color: #3e4451; color: #abb2bf; border-radius: 8px; padding: 5px;
                border: 1px solid #4b5263;
            }
            notebook { background-color: #282c34; }
            notebook tab {
                background-color: #3e4451; color: #abb2bf; border-radius: 8px 8px 0 0;
                padding: 8px 15px; font-weight: bold;
            }
            notebook tab:checked { background-color: #61afef; color: white; }
            listbox, treeview {
                background-color: #3e4451; color: #abb2bf; border-radius: 8px;
                border: 1px solid #4b5263;
            }
            treeview row:selected {
                background-color: #61afef; color: white; border-radius: 8px;
            }
            .details-frame {
                background-color: #3e4451;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #4b5263;
            }
            .details-label {
                font-weight: bold;
                color: #61afef; /* Highlight labels */
            }
            .details-value {
                color: #abb2bf;
            }
            """
            css_provider.load_from_data(css)
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_vbox.set_margin_top(10)
            main_vbox.set_margin_bottom(10)
            main_vbox.set_margin_start(10)
            main_vbox.set_margin_end(10)
            self.window.add(main_vbox)

            self.notebook = Gtk.Notebook()
            self.notebook.set_scrollable(True)
            self.notebook.set_tab_pos(Gtk.PositionType.TOP)
            main_vbox.pack_start(self.notebook, True, True, 0)

            install_tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            install_tab_content.set_margin_top(10)
            install_tab_content.set_margin_bottom(10)
            install_tab_content.set_margin_start(10)
            install_tab_content.set_margin_end(10)
            self.notebook.append_page(install_tab_content, Gtk.Label(label="Instalar"))
            self._setup_install_tab(install_tab_content)

            list_tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            list_tab_content.set_margin_top(10)
            list_tab_content.set_margin_bottom(10)
            list_tab_content.set_margin_start(10)
            list_tab_content.set_margin_end(10)
            self.notebook.append_page(list_tab_content, Gtk.Label(label="Listar Paquetes"))
            self._setup_list_tab(list_tab_content)

            config_tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            config_tab_content.set_margin_top(10)
            config_tab_content.set_margin_bottom(10)
            config_tab_content.set_margin_start(10)
            config_tab_content.set_margin_end(10)
            self.notebook.append_page(config_tab_content, Gtk.Label(label="Configuración"))
            self._setup_config_tab(config_tab_content)

            vm_tab_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            vm_tab_content.set_margin_top(10)
            vm_tab_content.set_margin_bottom(10)
            vm_tab_content.set_margin_start(10)
            vm_tab_content.set_margin_end(10)
            self.notebook.append_page(vm_tab_content, Gtk.Label(label="Gestión de VMs"))
            self._setup_vm_tab(vm_tab_content)

            self.window.show_all()
            # No hay output_text_view en la ventana principal, así que no hay _process_queue aquí.
            self._run_operation_in_thread(self._load_installed_packages_for_gui, operation_name="Cargando Paquetes Instalados")


        def on_window_destroy(self, widget):
            self.quit()

        def _setup_install_tab(self, tab):
            search_controls_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            tab.pack_start(search_controls_frame, False, False, 0)

            search_controls_frame.pack_start(Gtk.Label(label="Nombre del Paquete:"), False, False, 0)
            self.entry_app_name = Gtk.Entry()
            self.entry_app_name.set_hexpand(True)
            search_controls_frame.pack_start(self.entry_app_name, True, True, 0)

            self.search_button = Gtk.Button(label="Buscar")
            self.search_button.connect("clicked", self._run_search_remote_packages_from_gui)
            search_controls_frame.pack_start(self.search_button, False, False, 0)

            # Horizontal box for package list and details panel
            content_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            content_hbox.set_hexpand(True)
            content_hbox.set_vexpand(True)
            tab.pack_start(content_hbox, True, True, 0)

            # Left side: Available packages list
            self.available_packages_liststore = Gtk.ListStore(str, str) # Name, File Name
            self.available_packages_treeview = Gtk.TreeView(model=self.available_packages_liststore)

            renderer_text = Gtk.CellRendererText()
            self.available_packages_treeview.append_column(Gtk.TreeViewColumn("Paquete", renderer_text, text=0))
            self.available_packages_treeview.append_column(Gtk.TreeViewColumn("Archivo", renderer_text, text=1))

            self.available_packages_treeview.get_selection().connect("changed", self._on_package_select)

            scrolled_window_list = Gtk.ScrolledWindow()
            scrolled_window_list.set_hexpand(True)
            scrolled_window_list.set_vexpand(True)
            scrolled_window_list.add(self.available_packages_treeview)
            content_hbox.pack_start(scrolled_window_list, True, True, 0)

            # Right side: Package details panel
            self.details_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.details_panel.set_size_request(350, -1) # Fixed width for details panel
            self.details_panel.get_style_context().add_class("details-frame")
            content_hbox.pack_start(self.details_panel, False, False, 0)
            self.details_panel.set_visible(False) # Hidden by default

            # Populate details panel
            self.details_name_label = Gtk.Label(label="", xalign=0)
            self.details_name_label.get_style_context().add_class("details-label")
            self.details_panel.pack_start(self.details_name_label, False, False, 0)

            self.details_description_label = Gtk.Label(label="", xalign=0, wrap=True)
            self.details_description_label.get_style_context().add_class("details-value")
            self.details_panel.pack_start(self.details_description_label, False, False, 0)

            self.details_deps_label = Gtk.Label(label="", xalign=0, wrap=True)
            self.details_deps_label.get_style_context().add_class("details-value")
            self.details_panel.pack_start(self.details_deps_label, False, False, 0)

            self.details_vm_label = Gtk.Label(label="", xalign=0)
            self.details_vm_label.get_style_context().add_class("details-value")
            self.details_panel.pack_start(self.details_vm_label, False, False, 0)

            self.details_ext_label = Gtk.Label(label="", xalign=0)
            self.details_ext_label.get_style_context().add_class("details-value")
            self.details_panel.pack_start(self.details_ext_label, False, False, 0)

            self.install_selected_button = Gtk.Button(label="Instalar")
            self.install_selected_button.connect("clicked", self._run_install_from_gui)
            self.details_panel.pack_end(self.install_selected_button, False, False, 0)


            # Global actions frame (moved to the bottom for consistency)
            global_actions_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            tab.pack_end(global_actions_frame, False, False, 0) # Pack at the very bottom

            self.upgrade_button = Gtk.Button(label="Actualizar Todo")
            self.upgrade_button.connect("clicked", self._run_upgrade_all_from_gui)
            global_actions_frame.pack_start(self.upgrade_button, False, False, 0)

            self.fix_button = Gtk.Button(label="Reparar Paquetes")
            self.fix_button.connect("clicked", self._run_fix_broken_from_gui)
            global_actions_frame.pack_start(self.fix_button, False, False, 0)

            self.uninstall_button = Gtk.Button(label="Desinstalar")
            self.uninstall_button.connect("clicked", self._run_uninstall_from_gui)
            global_actions_frame.pack_start(self.uninstall_button, False, False, 0)

            self.local_install_button = Gtk.Button(label="Instalar Local")
            self.local_install_button.connect("clicked", self._run_local_install_from_gui)
            global_actions_frame.pack_start(self.local_install_button, False, False, 0)


        def _setup_list_tab(self, tab):
            list_controls_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            tab.pack_start(list_controls_frame, False, False, 0)

            self.list_button = Gtk.Button(label="Recargar Lista")
            self.list_button.connect("clicked", self._run_list_installed_from_gui)
            list_controls_frame.pack_start(self.list_button, False, False, 0)

            self.installed_packages_liststore = Gtk.ListStore(str, str, str, str) # Nombre, Tipo, Instalado en, Desktop
            self.installed_packages_treeview = Gtk.TreeView(model=self.installed_packages_liststore)

            renderer_text = Gtk.CellRendererText()
            self.installed_packages_treeview.append_column(Gtk.TreeViewColumn("Nombre", renderer_text, text=0))
            self.installed_packages_treeview.append_column(Gtk.TreeViewColumn("Tipo", renderer_text, text=1))
            self.installed_packages_treeview.append_column(Gtk.TreeViewColumn("Instalado en", renderer_text, text=2))
            self.installed_packages_treeview.append_column(Gtk.TreeViewColumn(".desktop", renderer_text, text=3))

            self.installed_packages_treeview.get_selection().connect("changed", self._on_installed_package_select)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.add(self.installed_packages_treeview)
            tab.pack_start(scrolled_window, True, True, 0)

        def _setup_config_tab(self, tab):
            config_grid = Gtk.Grid()
            config_grid.set_column_spacing(10)
            config_grid.set_row_spacing(10)
            config_grid.set_margin_top(10)
            config_grid.set_margin_bottom(10)
            config_grid.set_margin_start(10)
            config_grid.set_margin_end(10)
            tab.pack_start(config_grid, True, True, 0)

            config_grid.attach(Gtk.Label(label="Rama Actual:"), 0, 0, 1, 1)
            self.current_branch_label = Gtk.Label(label="Cargando...")
            config_grid.attach(self.current_branch_label, 1, 0, 1, 1)

            config_grid.attach(Gtk.Label(label="Cambiar Rama a:"), 0, 1, 1, 1)
            self.branch_options = ["regular", "lss", "dev", "beta", "med-regular"]
            self.selected_branch = Gtk.ComboBoxText()
            for option in self.branch_options:
                self.selected_branch.append_text(option)
            config_grid.attach(self.selected_branch, 1, 1, 1, 1)
            self.apply_branch_button = Gtk.Button(label="Aplicar Rama")
            self.apply_branch_button.connect("clicked", self._set_branch)
            config_grid.attach(self.apply_branch_button, 2, 1, 1, 1)

            config_grid.attach(Gtk.Label(label="Repositorios Configurados:"), 0, 2, 3, 1)
            self.repos_liststore = Gtk.ListStore(str)
            self.repos_treeview = Gtk.TreeView(model=self.repos_liststore)
            renderer_text = Gtk.CellRendererText()
            self.repos_treeview.append_column(Gtk.TreeViewColumn("URL del Repositorio", renderer_text, text=0))

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.add(self.repos_treeview)
            config_grid.attach(scrolled_window, 0, 3, 3, 1)

            repo_entry_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            config_grid.attach(repo_entry_frame, 0, 4, 3, 1)
            self.new_repo_entry = Gtk.Entry()
            self.new_repo_entry.set_hexpand(True)
            repo_entry_frame.pack_start(self.new_repo_entry, True, True, 0)
            self.add_repo_button = Gtk.Button(label="Añadir Repo")
            self.add_repo_button.connect("clicked", self._add_repo)
            repo_entry_frame.pack_start(self.add_repo_button, False, False, 0)
            self.remove_repo_button = Gtk.Button(label="Eliminar Repo Seleccionado")
            self.remove_repo_button.connect("clicked", self._remove_repo)
            repo_entry_frame.pack_start(self.remove_repo_button, False, False, 0)

            config_grid.attach(Gtk.Label(label="Nivel de Log:"), 0, 5, 1, 1)
            self.log_level_options = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            self.selected_log_level = Gtk.ComboBoxText()
            for option in self.log_level_options:
                self.selected_log_level.append_text(option)
            self.selected_log_level.set_active_id(list(logger.log_levels.keys())[logger.current_log_level])
            self.selected_log_level.connect("changed", self._set_log_level)
            config_grid.attach(self.selected_log_level, 1, 5, 1, 1)


            self._load_config_values()

        def _setup_vm_tab(self, tab):
            vm_grid = Gtk.Grid()
            vm_grid.set_column_spacing(10)
            vm_grid.set_row_spacing(10)
            vm_grid.set_margin_top(10)
            vm_grid.set_margin_bottom(10)
            vm_grid.set_margin_start(10)
            vm_grid.set_margin_end(10)
            tab.pack_start(vm_grid, True, True, 0)

            vm_grid.attach(Gtk.Label(label="Gestión de Máquinas Virtuales (LXC/QEMU)"), 0, 0, 3, 1)
            vm_grid.attach(Gtk.Label(label="Esta sección es para la orquestación avanzada de VMs."), 0, 1, 3, 1)
            vm_grid.attach(Gtk.Label(label="Permitirá instalar software en entornos aislados o incluso de otros sistemas operativos."), 0, 2, 3, 1)
            vm_grid.attach(Gtk.Label(label="Funcionalidad en desarrollo activo."), 0, 3, 3, 1)

            self.create_vm_button = Gtk.Button(label="Crear VM (LXC)")
            self.create_vm_button.connect("clicked", self._run_create_vm)
            vm_grid.attach(self.create_vm_button, 0, 4, 1, 1)

            self.delete_vm_button = Gtk.Button(label="Eliminar VM (LXC)")
            self.delete_vm_button.connect("clicked", self._run_delete_vm)
            vm_grid.attach(self.delete_vm_button, 1, 4, 1, 1)

            vm_grid.attach(Gtk.Label(label="VMs Existentes:"), 0, 5, 3, 1)
            self.vm_liststore = Gtk.ListStore(str)
            self.vm_treeview = Gtk.TreeView(model=self.vm_liststore)
            renderer_text = Gtk.CellRendererText()
            self.vm_treeview.append_column(Gtk.TreeViewColumn("Nombre de VM", renderer_text, text=0))

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            scrolled_window.add(self.vm_treeview)
            vm_grid.attach(scrolled_window, 0, 6, 3, 1)

            self._load_vm_list()

        def _load_vm_list(self):
            self.vm_liststore.clear()
            try:
                result = subprocess.run(["lxc", "list", "--format", "json"], capture_output=True, text=True, check=True)
                vms_json = json.loads(result.stdout)
                for vm in vms_json:
                    self.vm_liststore.append([vm['name']])
                mostrar_mensaje(f"Cargadas {len(vms_json)} VMs/Contenedores LXC.")
            except FileNotFoundError:
                mostrar_mensaje("Comando 'lxc' no encontrado. No se pueden listar VMs.", tipo="warning")
            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                mostrar_mensaje(f"Error al listar VMs LXC: {e}", tipo="error")


        def _load_config_values(self):
            try:
                current_branch = leer_rama_actual(ACTUAL_BRANCH_TXT)
                self.current_branch_label.set_text(current_branch)
                self.selected_branch.set_active_id(current_branch)
            except TPTCriticalError:
                self.current_branch_label.set_text("No configurado")
                self.selected_branch.set_active_id("regular")

            self.repos_liststore.clear()
            try:
                repos = leer_urls_repositorio(TPT_REPOS_LIST)
                for repo in repos:
                    self.repos_liststore.append([repo])
            except TPTCriticalError:
                pass

        def _set_branch(self, button):
            new_branch = self.selected_branch.get_active_text()
            if not new_branch:
                TPTGUI.show_message_dialog(self.window, "Rama Vacía", "Por favor, seleccione una rama.", Gtk.MessageType.WARNING)
                return
            try:
                with open(ACTUAL_BRANCH_TXT, 'w') as f:
                    f.write(new_branch + "\n")
                self.current_branch_label.set_text(new_branch)
                TPTGUI.show_message_dialog(self.window, "Rama Cambiada", f"La rama actual se ha cambiado a '{new_branch}'.", Gtk.MessageType.INFO)
            except IOError as e:
                TPTGUI.show_message_dialog(self.window, "Error", f"No se pudo escribir en el archivo de rama: {e}", Gtk.MessageType.ERROR)

        def _add_repo(self, button):
            new_repo = self.new_repo_entry.get_text().strip()
            if not new_repo:
                TPTGUI.show_message_dialog(self.window, "Entrada Vacía", "Por favor, ingrese una URL de repositorio.", Gtk.MessageType.WARNING)
                return
            try:
                with open(TPT_REPOS_LIST, 'a') as f:
                    f.write(new_repo + "\n")
                self.repos_liststore.append([new_repo])
                self.new_repo_entry.set_text("")
                TPTGUI.show_message_dialog(self.window, "Repositorio Añadido", f"Repositorio '{new_repo}' añadido.", Gtk.MessageType.INFO)
            except IOError as e:
                TPTGUI.show_message_dialog(self.window, "Error", f"No se pudo añadir el repositorio: {e}", Gtk.MessageType.ERROR)

        def _remove_repo(self, button):
            selection = self.repos_treeview.get_selection()
            model, treeiter = selection.get_selected()
            if not treeiter:
                TPTGUI.show_message_dialog(self.window, "Ningún Repo Seleccionado", "Por favor, seleccione un repositorio para eliminar.", Gtk.MessageType.WARNING)
                return

            repo_to_remove = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"¿Está seguro de que desea eliminar el repositorio '{repo_to_remove}'?"
            )
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                current_repos = []
                try:
                    with open(TPT_REPOS_LIST, 'r') as f:
                        current_repos = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                except IOError:
                    TPTGUI.show_message_dialog(self.window, "Error", "No se pudo leer el archivo de repositorios.", Gtk.MessageType.ERROR)
                    return

                if repo_to_remove in current_repos:
                    current_repos.remove(repo_to_remove)

                try:
                    with open(TPT_REPOS_LIST, 'w') as f:
                        for repo in current_repos:
                            f.write(repo + "\n")
                    model.remove(treeiter)
                    TPTGUI.show_message_dialog(self.window, "Repositorio Eliminado", "Repositorio(s) eliminado(s) con éxito.", Gtk.MessageType.INFO)
                except IOError as e:
                    TPTGUI.show_message_dialog(self.window, "Error", f"No se pudo guardar los cambios en el archivo de repositorios: {e}", Gtk.MessageType.ERROR)

        def _set_log_level(self, combobox):
            level_name = combobox.get_active_text()
            if level_name:
                logger.set_log_level(level_name)
                TPTGUI.show_message_dialog(self.window, "Nivel de Log Cambiado", f"El nivel de log se ha establecido a '{level_name}'.", Gtk.MessageType.INFO)

        def _run_operation_in_thread(self, target_func, *args, operation_name="Operación", app_name="", **kwargs):
            # Create and show the progress window
            progress_window = InstallationProgressWindow(self.window, operation_name=operation_name, app_name=app_name)
            progress_window.show_all()

            # Pass the progress window's update method to the target function
            kwargs['progress_callback'] = progress_window.update_progress
            # Pass the GUI input function for local installs/uninstalls
            kwargs['gui_input_func'] = self._show_input_dialog

            # Disable main window buttons
            self._set_buttons_state(False)

            # Reset the install button state visually
            if hasattr(self, 'install_selected_button'):
                self.install_selected_button.set_label("Instalar")
                self.install_selected_button.get_style_context().remove_class("install-button-progress")
                self.install_selected_button.get_style_context().remove_class("install-button-finished")
                self.install_selected_button.get_style_context().remove_class("install-button-error")

            # Start the thread
            thread = Thread(target=self._operation_wrapper, args=(target_func, progress_window) + args, kwargs=kwargs)
            thread.start()

            def check_thread():
                if thread.is_alive():
                    GLib.timeout_add(100, check_thread)
                else:
                    self._set_buttons_state(True) # Re-enable main window buttons
                    progress_window.destroy() # Close progress window automatically

                    # Update lists after operation
                    GLib.idle_add(self._load_installed_packages_for_gui)
                    GLib.idle_add(self._load_vm_list)

            GLib.timeout_add(100, check_thread)

        def _operation_wrapper(self, target_func, progress_window, *args, **kwargs):
            """Wrapper to catch exceptions from the thread and update GUI."""
            try:
                # Simulate progress for the main button (0% to 100%)
                # This is a simple linear progress, actual progress would be more complex
                for i in range(1, 101):
                    # Only update if the button exists (it might not for other operations)
                    if hasattr(self, 'install_selected_button'):
                        GLib.idle_add(self.install_selected_button.get_style_context().add_class, "install-button-progress")
                        GLib.idle_add(self.install_selected_button.set_label, f"Progreso... {i}%")
                    progress_window.update_progress(i / 100.0, f"Progreso: {i}%")
                    time.sleep(0.05) # Simulate work

                target_func(*args, **kwargs)
                GLib.idle_add(progress_window.set_finished, True, "Operación Completada.")
                if hasattr(self, 'install_selected_button'):
                    GLib.idle_add(self.install_selected_button.set_label, "Completado")
                    GLib.idle_add(self.install_selected_button.get_style_context().remove_class, "install-button-progress")
                    GLib.idle_add(self.install_selected_button.get_style_context().add_class, "install-button-finished")
                send_desktop_notification("TPT: Operación Exitosa", "La operación se completó con éxito.", icon="software-update-available")

            except TPTUserCancelled as e:
                GLib.idle_add(progress_window.set_finished, False, f"Operación Cancelada: {e}")
                if hasattr(self, 'install_selected_button'):
                    GLib.idle_add(self.install_selected_button.set_label, "Cancelado")
                    GLib.idle_add(self.install_selected_button.get_style_context().remove_class, "install-button-progress")
                    GLib.idle_add(self.install_selected_button.get_style_context().add_class, "install-button-error")
                TPTGUI.show_message_dialog(self.window, "Operación Cancelada", str(e), Gtk.MessageType.WARNING)
                send_desktop_notification("TPT: Operación Cancelada", str(e), icon="dialog-warning")
            except TPTError as e:
                GLib.idle_add(progress_window.set_finished, False, f"Fallo: {e}")
                if hasattr(self, 'install_selected_button'):
                    GLib.idle_add(self.install_selected_button.set_label, "Fallo")
                    GLib.idle_add(self.install_selected_button.get_style_context().remove_class, "install-button-progress")
                    GLib.idle_add(self.install_selected_button.get_style_context().add_class, "install-button-error")
                TPTGUI.show_message_dialog(self.window, "Error de TPT", str(e), Gtk.MessageType.ERROR)
                send_desktop_notification("TPT: Error", str(e), icon="dialog-error")
            except Exception as e:
                GLib.idle_add(progress_window.set_finished, False, f"Error Inesperado: {e}")
                if hasattr(self, 'install_selected_button'):
                    GLib.idle_add(self.install_selected_button.set_label, "Error")
                    GLib.idle_add(self.install_selected_button.get_style_context().remove_class, "install-button-progress")
                    GLib.idle_add(self.install_selected_button.get_style_context().add_class, "install-button-error")
                TPTGUI.show_message_dialog(self.window, "Error Inesperado", f"Ocurrió un error inesperado: {e}", Gtk.MessageType.ERROR)
                logger.critical(f"Error inesperado en _operation_wrapper: {e}", exc_info=True) # Log full traceback
                send_desktop_notification("TPT: Error Crítico", f"Ocurrió un error inesperado: {e}", icon="dialog-error")

        def _set_buttons_state(self, sensitive):
            buttons_and_widgets = [
                self.search_button, self.install_selected_button, self.uninstall_button, self.upgrade_button,
                self.list_button, self.local_install_button, self.fix_button,
                self.apply_branch_button, self.add_repo_button, self.remove_repo_button,
                self.selected_branch, self.new_repo_entry, self.entry_app_name,
                self.available_packages_treeview, self.installed_packages_treeview,
                self.create_vm_button, self.delete_vm_button, self.vm_treeview,
                self.selected_log_level
            ]
            for widget in buttons_and_widgets:
                try:
                    widget.set_sensitive(sensitive)
                except AttributeError:
                    logger.warning(f"No se pudo establecer el estado '{sensitive}' para el widget '{widget}'.")
                    pass

        def _run_search_remote_packages_from_gui(self, button):
            search_term = self.entry_app_name.get_text().strip()
            if not search_term:
                TPTGUI.show_message_dialog(self.window, "Entrada Vacía", "Por favor, ingrese un nombre de paquete para buscar.", Gtk.MessageType.WARNING)
                return
            # Clear previous details
            self.details_panel.set_visible(False)
            self.selected_package_details = {}
            self._run_operation_in_thread(self._perform_remote_search_and_update_gui, search_term, operation_name="Buscando Paquetes", app_name=search_term)

        def _perform_remote_search_and_update_gui(self, search_term, progress_callback, **kwargs):
            """Ejecuta la búsqueda remota y actualiza la GUI con los resultados."""
            GLib.idle_add(self.available_packages_liststore.clear)
            self.available_packages_data = {}

            progress_callback(0.1, f"Buscando '{search_term}'...")
            packages_dict = obtener_paquetes_disponibles_remoto(search_term) # Ahora devuelve un diccionario
            progress_callback(0.7, "Procesando resultados...")

            if packages_dict:
                for pkg_name, pkg_data in packages_dict.items():
                    self.available_packages_data[pkg_name] = pkg_data
                    GLib.idle_add(self.available_packages_liststore.append, [
                        pkg_data['name'],
                        pkg_data['file_name']
                    ])
                mostrar_mensaje(f"Encontrados {len(packages_dict)} resultados únicos para '{search_term}'.")
            else:
                mostrar_mensaje(f"No se encontraron resultados para '{search_term}'.", tipo="advertencia")
            progress_callback(1.0, "Búsqueda completada.")


        def _run_install_from_gui(self, button):
            if not self.selected_package_details:
                TPTGUI.show_message_dialog(self.window, "Ningún Paquete Seleccionado", "Por favor, seleccione un paquete de la lista de resultados para instalar.", Gtk.MessageType.WARNING)
                return

            app_name = self.selected_package_details['name']
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"¿Está seguro de que desea instalar '{app_name}'?"
            )
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self._run_operation_in_thread(instalar_desde_remoto, app_name, operation_name="Instalando", app_name=app_name)


        def _run_uninstall_from_gui(self, button):
            app_name = self.entry_app_name.get_text().strip()

            # Si el campo de texto está vacío, intenta obtener de la selección de la lista de instalados
            if not app_name:
                selection = self.installed_packages_treeview.get_selection()
                model, treeiter = selection.get_selected()
                if treeiter:
                    app_name = model[treeiter][0]

            # Si aún está vacío, pide al usuario
            if not app_name:
                app_name = self._show_input_dialog("Desinstalar Paquete", "Ingrese el nombre del paquete a desinstalar:")
                if not app_name: # Si el usuario cancela el diálogo
                    raise TPTUserCancelled("Operación de desinstalación cancelada por el usuario.")

            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"¿Está seguro de que desea desinstalar '{app_name}'?"
            )
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self._run_operation_in_thread(tpt_uninstall, app_name, operation_name="Desinstalando", app_name=app_name)

        def _run_upgrade_all_from_gui(self, button):
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="¿Está seguro de que desea actualizar todos los paquetes instalados por TPT? Esto puede llevar tiempo."
            )
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self._run_operation_in_thread(tpt_upgrade_all, operation_name="Actualizando Todos los Paquetes")

        def _run_list_installed_from_gui(self, button):
            self._run_operation_in_thread(self._load_installed_packages_for_gui, operation_name="Cargando Paquetes Instalados")

        def _run_fix_broken_from_gui(self, button):
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="¿Está seguro de que desea intentar reparar paquetes rotos?"
            )
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self._run_operation_in_thread(tpt_fix_broken, operation_name="Reparando Paquetes")

        def _run_local_install_from_gui(self, button):
            self._run_operation_in_thread(self._handle_local_install_gui, operation_name="Instalación Local")

        def _handle_local_install_gui(self, progress_callback, gui_input_func):
            try:
                verificar_espacio_libre()

                extension_elegida = gui_input_func("Extensión del Paquete", "Diga la extensión de su paquete (ej: .deb, .sh, .py, .AppImage, .tar.gz, .nemas_pkg, .flatpakref)")
                if not extension_elegida: raise TPTUserCancelled("Extensión no proporcionada.")
                extension_validada = comprobacion_extension(extension_elegida)

                ruta_paquete_local = gui_input_func("Ruta del Paquete", "Díganos la ruta exacta del paquete (ej: /home/usuario/paquete.deb)")
                if not ruta_paquete_local: raise TPTUserCancelled("Ruta de paquete local no proporcionada.")
                if not os.path.exists(ruta_paquete_local):
                    raise TPTError("Esa ruta no existe.")

                nombre_app_local = os.path.splitext(os.path.basename(ruta_paquete_local))[0]

                if extension_validada in [".py", ".sh"]:
                    nombre_ejecutable = gui_input_func("Nombre del Ejecutable", "Elija un nombre para el ejecutable (SIN ESPACIOS)")
                    if not nombre_ejecutable: raise TPTUserCancelled("Nombre de ejecutable no proporcionado.")

                    ruta_destino_ejecutable = os.path.join(RUTA_DESTINO_EJECUTABLES, nombre_ejecutable + extension_validada)

                    if os.path.exists(ruta_destino_ejecutable):
                        dialog = Gtk.MessageDialog(
                            parent=self.window,
                            flags=0,
                            message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO,
                            text=f"Ya existe '{nombre_ejecutable}{extension_validada}'. ¿Desea sobrescribirlo?"
                        )
                        response = dialog.run()
                        dialog.destroy()
                        if response != Gtk.ResponseType.YES:
                            raise TPTUserCancelled("Instalación cancelada por el usuario.")

                    instalar_paquete(nombre_app_local, extension_validada, ruta_paquete_local, nombre_ejecutable, ruta_destino_ejecutable, verificar_md5_oficial=False)
                else:
                    instalar_paquete(nombre_app_local, extension_validada, ruta_paquete_local, verificar_md5_oficial=False)

                TPTGUI.show_message_dialog(self.window, "Instalación Local Completada", f"Paquete '{nombre_app_local}' instalado localmente con éxito.", Gtk.MessageType.INFO)

            except TPTError as e:
                raise e # Re-raise for wrapper to catch
            except TPTUserCancelled as e:
                raise e
            except Exception as e:
                logger.error(f"Error inesperado en _handle_local_install_gui: {e}", exc_info=True)
                raise TPTError(f"Ocurrió un error inesperado durante la instalación local: {e}")

        def _on_package_select(self, selection):
            model, treeiter = selection.get_selected()
            if treeiter:
                app_name = model[treeiter][0]
                self.entry_app_name.set_text(app_name)

                pkg_details = self.available_packages_data.get(app_name, {})
                self.selected_package_details = pkg_details # Store for install button
                self.details_panel.set_visible(True)

                self.details_name_label.set_text(f"Nombre: {pkg_details.get('name', 'N/A')}")
                self.details_description_label.set_text(f"Descripción: {pkg_details.get('description', 'No disponible')}")
                self.details_deps_label.set_text(f"Dependencias: {', '.join(pkg_details.get('dependencies', ['Ninguna']))}")

                vm_info_text = f"Requiere VM: {'Sí' if pkg_details.get('isolated_install', False) else 'No'}"
                if pkg_details.get('isolated_install', False):
                    vm_info_text += f" (Tipo: {pkg_details.get('vm_type', 'N/A')}, Imagen: {pkg_details.get('vm_image', 'N/A')})"
                self.details_vm_label.set_text(vm_info_text)

                self.details_ext_label.set_text(f"Extensión: {pkg_details.get('extension', 'N/A')}")

                self.install_selected_button.set_label("Instalar")
                self.install_selected_button.get_style_context().remove_class("install-button-progress")
                self.install_selected_button.get_style_context().remove_class("install-button-finished")
                self.install_selected_button.get_style_context().remove_class("install-button-error")

            else:
                self.details_panel.set_visible(False)
                self.selected_package_details = {}


        def _load_installed_packages_for_gui(self, progress_callback=None, **kwargs):
            GLib.idle_add(self.installed_packages_liststore.clear)
            self.installed_packages_data = {}

            mostrar_mensaje("Cargando paquetes instalados...")
            installed_packages = tpt_list_installed() # This now returns the dict
            self.installed_packages_data = installed_packages

            if installed_packages:
                for app_name, details in installed_packages.items():
                    ext = details.get('extension', 'N/A')
                    instalado_a = details.get('instalado_a', 'N/A')
                    desktop_file_status = 'Sí' if details.get('desktop_file') else 'No'
                    GLib.idle_add(self.installed_packages_liststore.append, [app_name, ext, instalado_a, desktop_file_status])
                mostrar_mensaje(f"Cargados {len(installed_packages)} paquetes instalados.")
            else:
                mostrar_mensaje("No hay paquetes instalados por TPT.")


        def _on_installed_package_select(self, selection):
            model, treeiter = selection.get_selected()
            if treeiter:
                app_name = model[treeiter][0]
                self.entry_app_name.set_text(app_name)

                pkg_details = self.installed_packages_data.get(app_name, {})
                # No mostramos en el panel de detalles de instalación, solo rellenamos el entry
                # Si queremos mostrar detalles de instalados, necesitaríamos otro panel o un diálogo.
                mostrar_mensaje(f"Detalles del paquete instalado '{app_name}':")
                mostrar_mensaje(f"  Tipo: {pkg_details.get('extension', 'N/A')}")
                mostrar_mensaje(f"  Instalado en: {pkg_details.get('instalado_a', 'N/A')}")
                mostrar_mensaje(f"  Archivo .desktop: {pkg_details.get('desktop_file', 'No')}")
                mostrar_mensaje(f"  Instalado en VM: {pkg_details.get('vm_id', 'No')}")
                if pkg_details.get('vm_id') != 'No':
                    mostrar_mensaje(f"    Tipo VM: {pkg_details.get('vm_type', 'N/A')}")
                    mostrar_mensaje(f"    Imagen VM: {pkg_details.get('vm_image', 'N/A')}")

        def _run_create_vm(self, button):
            vm_name = self._show_input_dialog("Crear VM", "Ingrese un nombre para la nueva VM/Contenedor LXC:")
            if not vm_name: return
            vm_image = self._show_input_dialog("Crear VM", "Ingrese la imagen base (ej. ubuntu:22.04):")
            if not vm_image: return
            self._run_operation_in_thread(_create_lxc_container, vm_name, vm_image, operation_name="Creando VM", app_name=vm_name)

        def _run_delete_vm(self, button):
            selection = self.vm_treeview.get_selection()
            model, treeiter = selection.get_selected()
            if not treeiter:
                TPTGUI.show_message_dialog(self.window, "Ninguna VM Seleccionada", "Por favor, seleccione una VM/Contenedor para eliminar.", Gtk.MessageType.WARNING)
                return

            vm_name = model[treeiter][0]
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"¿Está seguro de que desea eliminar la VM/Contenedor '{vm_name}'? Esto es irreversible."
            )
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self._run_operation_in_thread(_delete_lxc_container, vm_name, operation_name="Eliminando VM", app_name=vm_name)


# --- PROGRAMA PRINCIPAL ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestor de paquetes TPT para Nemas OS. ¡Revolucionario!")
    parser.add_argument('--install', help='Instala una aplicación específica desde los repositorios remotos de Nemas OS.')
    parser.add_argument('--uninstall', help='Desinstala una aplicación específica instalada por TPT.')
    parser.add_argument('--upgrade', action='store_true', help='Actualiza todos los paquetes instalados por TPT.')
    parser.add_argument('--list', action='store_true', help='Muestra la lista de paquetes instalados por TPT.')
    parser.add_argument('--local', action='store_true', help='Activa el modo de instalación local (pregunta la ruta del paquete).')
    parser.add_argument('--gui', action='store_true', help='Inicia la interfaz gráfica de TPT.')
    parser.add_argument('--fix', action='store_true', help='Intenta reparar paquetes .deb rotos o dependencias faltantes.')
    parser.add_argument('--log-level', default='INFO', help='Establece el nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).')

    args = parser.parse_args()
    # print(f"DEBUG: Argumentos parseados: {args}") # Desactivado el debug de argumentos

    logger.set_log_level(args.log_level)

    try:
        if not es_root() and not (len(sys.argv) == 2 and sys.argv[1] == '--help'):
            elevar_privilegios_con_pkexec()

        crear_archivos_config_iniciales()
        verificar_espacio_libre()

        if args.gui:
            if not HAS_GTK:
                raise TPTCriticalError("La GUI de TPT requiere PyGObject (GTK) pero no está instalada. Ejecute 'sudo apt install python3-gi gir1.2-gtk-3.0'.")
            global_app_instance = TPTGUI()
            global_app_instance.run([]) # Pasamos una lista vacía para que GTK no intente parsear argumentos
            sys.exit(0)

        if args.install:
            instalar_desde_remoto(args.install)
        elif args.uninstall:
            tpt_uninstall(args.uninstall)
        elif args.upgrade:
            tpt_upgrade_all()
        elif args.list:
            tpt_list_installed()
        elif args.local:
            extension_elegida = obtener_entrada_usuario("Diga la extensión de su paquete (ej: .deb, .sh, .py, .AppImage, .tar.gz, .nemas_pkg, .flatpakref)")
            extension_validada = comprobacion_extension(extension_elegida)
            ruta_paquete_local = obtener_entrada_usuario("Díganos la ruta exacta del paquete (ej: /home/usuario/paquete.deb)")

            nombre_app_local = os.path.splitext(os.path.basename(ruta_paquete_local))[0]

            if extension_validada in [".py", ".sh"]:
                nombre_ejecutable, ruta_destino_ejecutable = preguntar_nombre_ejecutable(extension_validada)
                instalar_paquete(nombre_app_local, extension_validada, ruta_paquete_local, nombre_ejecutable, ruta_destino_ejecutable, verificar_md5_oficial=False)
            else:
                instalar_paquete(nombre_app_local, extension_validada, ruta_paquete_local, verificar_md5_oficial=False)
        elif args.fix:
            tpt_fix_broken()
        else:
            print("\nModo de uso de TPT:")
            print("  Para instalar desde repositorios remotos: sudo tpt --install <nombre_aplicacion>")
            print("  Para desinstalar un paquete:             sudo tpt --uninstall <nombre_aplicacion>")
            print("  Para actualizar todos los paquetes:      sudo tpt --upgrade")
            print("  Para listar paquetes instalados:         sudo tpt --list")
            print("  Para instalar un paquete localmente:     sudo tpt --local")
            print("  Para reparar paquetes rotos:             sudo tpt --fix")
            print("  Para iniciar la GUI:                     sudo tpt --gui")
            print("  Para establecer el nivel de log:         tpt --log-level <nivel> (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
            print("  Para más ayuda:                          tpt --help")
            print("\nPara el equipo de Nemas OS: ¡Gracias por usar TPT!")

    except TPTUserCancelled as e:
        logger.info(f"Operación cancelada por el usuario: {e}")
        sys.exit(1)
    except TPTCriticalError as e:
        logger.critical(f"ERROR CRÍTICO: {e}", exc_info=True) # Asegurarse de que se pasa exc_info
        print(f"❌ ERROR CRÍTICO: {e}")
        sys.exit(1)
    except TPTError as e:
        logger.error(f"Error de TPT: {e}", exc_info=True) # Asegurarse de que se pasa exc_info
        print(f"❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Error inesperado y no manejado: {e}", exc_info=True)
        print(f"❌ ERROR INESPERADO: {e}")
        sys.exit(1)
