import gettext
import os
from pathlib import Path

# La localización de nuestros archivos de traducción
APP_NAME = "tpt"
LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"

# Configurar gettext
# Esto busca el mejor idioma disponible basado en las variables de entorno del usuario
try:
    translation = gettext.translation(APP_NAME, localedir=LOCALE_DIR, fallback=True)
    _ = translation.gettext
except FileNotFoundError:
    # Fallback a una función de traducción nula si no se encuentran los archivos .mo
    # Esto asegura que la aplicación no falle si las traducciones no están instaladas.
    _ = gettext.gettext

def set_language(lang_code: str | None = None):
    """
    Permite forzar un idioma específico.
    Si lang_code es None, usa el idioma del sistema.
    """
    global _
    try:
        translation = gettext.translation(APP_NAME, localedir=LOCALE_DIR, languages=[lang_code] if lang_code else None, fallback=True)
        _ = translation.gettext
    except FileNotFoundError:
        _ = gettext.gettext
