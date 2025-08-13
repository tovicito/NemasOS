#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# generador_informe_archivos.py - Analiza un directorio y genera un informe (Nemás OS)
#

import os
import argparse
from pathlib import Path
from collections import Counter

def human_readable_size(size, decimal_places=2):
    """Convierte un tamaño en bytes a un formato legible."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def generar_informe(directorio):
    """
    Analiza un directorio y genera un informe sobre su contenido.
    """
    print("=============================================")
    print("  Generador de Informes de Nemás OS")
    print("=============================================")
    print(f"Analizando el directorio: '{directorio}'\\n")

    if not directorio.is_dir():
        print(f"Error: El directorio '{directorio}' no existe.")
        return

    total_size = 0
    total_files = 0
    total_dirs = 0
    extension_counts = Counter()
    extension_sizes = Counter()

    for dirpath, dirnames, filenames in os.walk(directorio):
        total_dirs += len(dirnames)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Ignorar enlaces simbólicos rotos o archivos inaccesibles
            if not os.path.exists(fp) or not os.access(fp, os.R_OK):
                continue

            try:
                size = os.path.getsize(fp)
                total_files += 1
                total_size += size

                # Agrupar por extensión
                extension = Path(f).suffix.lower() if Path(f).suffix else ".sin_extension"
                extension_counts[extension] += 1
                extension_sizes[extension] += size
            except FileNotFoundError:
                continue

    print("--- Resumen General ---")
    print(f"Número total de archivos:    {total_files}")
    print(f"Número total de directorios: {total_dirs}")
    print(f"Tamaño total del directorio: {human_readable_size(total_size)}\\n")

    print("--- Desglose por Tipo de Archivo (Top 15 por tamaño) ---")
    print(f"{'Extensión':<15} {'Número':>10} {'Tamaño Total':>18} {'% del Total':>12}")
    print("-" * 60)

    # Ordenar extensiones por el tamaño total que ocupan
    sorted_extensions = sorted(extension_sizes.items(), key=lambda item: item[1], reverse=True)

    for i, (ext, size) in enumerate(sorted_extensions):
        if i >= 15:
            break # Mostrar solo el top 15
        count = extension_counts[ext]
        percentage = (size / total_size * 100) if total_size > 0 else 0
        print(f"{ext:<15} {count:>10} {human_readable_size(size):>18} {percentage:>10.2f}%")

    print("\\n=============================================")
    print("  Informe completado.")
    print("=============================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analiza un directorio y genera un informe de su contenido.",
        epilog="Ejemplo: python3 generador_informe_archivos.py /home/usuario/documentos"
    )
    parser.add_argument(
        "directorio",
        nargs='?', # El argumento es opcional
        default='.', # Valor por defecto si no se proporciona
        type=str,
        help="El directorio a analizar. Por defecto, es el directorio actual ('.')."
    )

    args = parser.parse_args()
    # resolve() convierte a ruta absoluta y limpia '..' etc.
    directorio_a_analizar = Path(args.directorio).resolve()

    generar_informe(directorio_a_analizar)
