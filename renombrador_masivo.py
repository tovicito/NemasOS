#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# renombrador_masivo.py - Renombra archivos de forma masiva en un directorio (Nemás OS)
#

import os
import argparse
from pathlib import Path

def renombrar_masivamente(directorio, patron_busqueda, texto_reemplazo, dry_run=True):
    """
    Renombra archivos en un directorio reemplazando una parte del nombre.
    """
    print("=============================================")
    print("   Renombrador Masivo de Nemás OS")
    print("=============================================")
    if dry_run:
        print("--- MODO SIMULACIÓN (no se harán cambios reales) ---")
    else:
        print("--- MODO REAL (se aplicarán los cambios) ---")

    print(f"Directorio:     '{directorio}'")
    print(f"Buscando:       '{patron_busqueda}'")
    print(f"Reemplazar con: '{texto_reemplazo}'\\n")

    if not directorio.is_dir():
        print(f"Error: El directorio '{directorio}' no existe.")
        return

    archivos_afectados = 0
    for filename in sorted(os.listdir(directorio)):
        if patron_busqueda in filename:
            # Solo actuar sobre archivos, no directorios
            if (directorio / filename).is_file():
                nuevo_nombre = filename.replace(patron_busqueda, texto_reemplazo)
                ruta_antigua = directorio / filename
                ruta_nueva = directorio / nuevo_nombre

                print(f"'{filename}'  ->  '{nuevo_nombre}'")

                if not dry_run:
                    try:
                        # Evitar sobreescribir un archivo existente
                        if ruta_nueva.exists():
                            print(f"  AVISO: El archivo '{nuevo_nombre}' ya existe. Se omite el renombrado.")
                            continue
                        os.rename(ruta_antigua, ruta_nueva)
                    except OSError as e:
                        print(f"  ERROR: No se pudo renombrar. {e}")

                archivos_afectados += 1

    print("\\n---------------------------------------------")
    if archivos_afectados == 0:
        print("No se encontraron archivos que coincidan con el patrón de búsqueda.")
    else:
        if dry_run:
            print(f"Se encontraron {archivos_afectados} archivos para renombrar.")
            print("Para aplicar los cambios, ejecuta el script de nuevo con la opción '--real'.")
        else:
            print(f"¡Proceso completado! Se han procesado {archivos_afectados} archivos.")

    print("=============================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Renombra archivos de forma masiva en un directorio.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Ejemplos de uso:
  # Simular el cambio de 'IMG_' por 'foto_' en el directorio actual
  python3 renombrador_masivo.py . 'IMG_' 'foto_'

  # Aplicar el cambio anterior de forma real
  python3 renombrador_masivo.py . 'IMG_' 'foto_' --real

  # Renombrar .txt a .md en la carpeta /home/user/documentos
  python3 renombrador_masivo.py /home/user/documentos .txt .md --real"""
    )
    parser.add_argument(
        "directorio",
        type=str,
        help="El directorio que contiene los archivos a renombrar. Usa '.' para el actual."
    )
    parser.add_argument(
        "patron_busqueda",
        type=str,
        help="El texto a buscar en los nombres de archivo."
    )
    parser.add_argument(
        "texto_reemplazo",
        type=str,
        help="El texto con el que se reemplazará el patrón."
    )
    parser.add_argument(
        '--real',
        action='store_true',
        help="Ejecuta el renombrado real. Por defecto, solo simula los cambios."
    )

    args = parser.parse_args()

    directorio_a_procesar = Path.cwd() if args.directorio == '.' else Path(args.directorio)

    # El modo 'dry_run' es True si no se especifica '--real'
    renombrar_masivamente(directorio_a_procesar, args.patron_busqueda, args.texto_reemplazo, dry_run=not args.real)
