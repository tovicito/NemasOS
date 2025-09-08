import os
import subprocess
from pathlib import Path
from deep_translator import GoogleTranslator
import polib # Usaremos polib para parsear archivos .po de forma segura

def run_command(command):
    """Ejecuta un comando y muestra su salida."""
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error ejecutando {' '.join(command)}:")
        print(result.stderr)
    return result

def main():
    """
    Script para crear, traducir automáticamente y compilar los archivos de idioma.
    """
    locale_dir = Path("tpt_project/locale")
    pot_file = locale_dir / "tpt.pot"

    if not pot_file.exists():
        print(f"No se encontró el archivo de plantilla {pot_file}. Ejecuta pygettext primero.")
        return

    target_languages = {
        'es': 'spanish', 'fr': 'french', 'de': 'german', 'it': 'italian',
        'pt': 'portuguese', 'ru': 'russian', 'ja': 'japanese',
        'zh-CN': 'chinese (simplified)', 'ar': 'arabic', 'hi': 'hindi'
    }

    for lang, lang_name in target_languages.items():
        print(f"\n--- Procesando idioma: {lang_name} ({lang}) ---")

        # 1. Crear directorios y archivo .po
        lang_dir = locale_dir / lang / "LC_MESSAGES"
        lang_dir.mkdir(parents=True, exist_ok=True)
        po_file = lang_dir / "tpt.po"

        if not po_file.exists():
            run_command(["msginit", "--no-translator", "-l", lang, "-i", str(pot_file), "-o", str(po_file)])

        # 2. Traducir automáticamente con polib y deep_translator
        print(f"Traduciendo {po_file}...")
        try:
            po = polib.pofile(str(po_file))

            entries_to_translate = [entry for entry in po if not entry.msgstr and entry.msgid]
            if not entries_to_translate:
                print("No hay nuevas entradas para traducir. Saltando.")
            else:
                print(f"Encontradas {len(entries_to_translate)} entradas para traducir.")
                # El traductor soporta listas de strings para traducciones en lote
                source_texts = [entry.msgid for entry in entries_to_translate]

                # 'zh-CN' es un alias no estándar para gettext, el traductor usa 'zh-cn'
                translator_lang_code = lang.lower()

                translated_texts = GoogleTranslator(source='en', target=translator_lang_code).translate_batch(source_texts)

                for entry, translation in zip(entries_to_translate, translated_texts):
                    if translation:
                        entry.msgstr = translation

                po.save()
                print("Traducción completada y guardada.")

        except Exception as e:
            print(f"Ocurrió un error durante la traducción para {lang}: {e}")
            continue

        # El paso de compilación a .mo se hará bajo demanda por el asistente de configuración.
        # # 3. Compilar a .mo
        # mo_file = lang_dir / "tpt.mo"
        # print(f"Compilando {po_file} a {mo_file}...")
        # run_command(["msgfmt", str(po_file), "-o", str(mo_file)])

    print("\n¡Proceso de generación de archivos .po completado para todos los idiomas!")

if __name__ == "__main__":
    main()
