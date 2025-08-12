#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# buscar_archivos_grandes.py - Encuentra archivos que superan un tamaño específico (Nemás OS)
#

import os
import argparse
from pathlib import Path

def buscar_archivos_grandes(directorio, tamano_min_mb):
    """
    Busca archivos más grandes que tamano_min_mb en el directorio especificado.
    """
    print("=============================================")
    print("  Buscador de Archivos Grandes de Nemás OS")
    print("=============================================")
    print(f"Buscando en: '{directorio}'")
    print(f"Tamaño mínimo: {tamano_min_mb} MB\\n")

    tamano_min_bytes = tamano_min_mb * 1024 * 1024
    archivos_encontrados = []

    try:
        for dirpath, _, filenames in os.walk(directorio):
            for filename in filenames:
                # Ignorar enlaces simbólicos rotos
                ruta_completa = os.path.join(dirpath, filename)
                if not os.path.exists(ruta_completa):
                    continue

                try:
                    tamano_archivo_bytes = os.path.getsize(ruta_completa)
                    if tamano_archivo_bytes >= tamano_min_bytes:
                        tamano_archivo_mb = tamano_archivo_bytes / (1024 * 1024)
                        archivos_encontrados.append((ruta_completa, tamano_archivo_mb))
                except FileNotFoundError:
                    # El archivo pudo haber sido eliminado durante el escaneo
                    continue

    except FileNotFoundError:
        print(f"Error: El directorio '{directorio}' no fue encontrado.")
        return

    print("--- Archivos Encontrados ---")
    if not archivos_encontrados:
        print("No se encontraron archivos que superen el tamaño especificado.")
    else:
        # Ordenar por tamaño de mayor a menor
        archivos_encontrados.sort(key=lambda x: x[1], reverse=True)
        for ruta, tamano in archivos_encontrados:
            print(f"{tamano:>8.2f} MB - {ruta}")

    print("\\n=============================================")
    print("  Búsqueda completada.")
    print("=============================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Busca archivos más grandes que un tamaño específico en un directorio.",
        epilog="Ejemplo: python3 buscar_archivos_grandes.py /home/usuario -s 100"
    )
    parser.add_argument(
        "directorio",
        type=str,
        help="El directorio en el que se buscarán los archivos. Usa '.' para el directorio actual."
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=500,
        help="El tamaño mínimo del archivo en Megabytes (MB). Por defecto: 500 MB."
    )

    args = parser.parse_args()

    # Usar el directorio actual si el proporcionado es '.'
    directorio_a_buscar = Path.cwd() if args.directorio == '.' else Path(args.directorio)

    buscar_archivos_grandes(directorio_a_buscar, args.size)
