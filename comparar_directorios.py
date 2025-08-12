#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# comparar_directorios.py - Compara dos directorios y muestra sus diferencias (Nemás OS)
#

import os
import filecmp
import argparse
from pathlib import Path

def comparar_directorios(dir1, dir2, recursivo=False):
    """
    Compara dos directorios e informa sobre las diferencias.
    """
    print(f"Comparando '{dir1}' y '{dir2}'...")
    print("-" * 40)

    if not dir1.is_dir():
        print(f"Error: El directorio '{dir1}' no existe.")
        return
    if not dir2.is_dir():
        print(f"Error: El directorio '{dir2}' no existe.")
        return

    comparador = filecmp.dircmp(dir1, dir2)

    # --- Archivos solo en el Directorio 1 ---
    if comparador.left_only:
        print(f"Archivos solo en '{dir1.name}':")
        for name in sorted(comparador.left_only):
            print(f"  + {name}")
        print()

    # --- Archivos solo en el Directorio 2 ---
    if comparador.right_only:
        print(f"Archivos solo en '{dir2.name}':")
        for name in sorted(comparador.right_only):
            print(f"  + {name}")
        print()

    # --- Archivos que no coinciden ---
    if comparador.diff_files:
        print("Archivos con contenido diferente:")
        for name in sorted(comparador.diff_files):
            print(f"  ! {name}")
        print()

    # --- Archivos que coinciden ---
    if comparador.same_files:
        # Descomentar si se quiere un listado de archivos iguales
        # print("Archivos idénticos:")
        # for name in sorted(comparador.same_files):
        #     print(f"  = {name}")
        # print()
        pass

    if not comparador.left_only and not comparador.right_only and not comparador.diff_files:
        print("Los contenidos a este nivel son idénticos.")

    if recursivo:
        for sub_dir in comparador.common_dirs:
            print()
            nuevo_dir1 = dir1 / sub_dir
            nuevo_dir2 = dir2 / sub_dir
            comparar_directorios(nuevo_dir1, nuevo_dir2, recursivo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compara dos directorios y muestra un informe de diferencias.",
        epilog="Ejemplo: python3 comparar_directorios.py ./dir_viejo ./dir_nuevo -r"
    )
    parser.add_argument(
        "dir1",
        type=str,
        help="El primer directorio a comparar."
    )
    parser.add_argument(
        "dir2",
        type=str,
        help="El segundo directorio a comparar."
    )
    parser.add_argument(
        "-r", "--recursivo",
        action="store_true",
        help="Realiza la comparación de forma recursiva en los subdirectorios."
    )

    args = parser.parse_args()

    dir1_path = Path(args.dir1)
    dir2_path = Path(args.dir2)

    print("=============================================")
    print("  Comparador de Directorios de Nemás OS")
    print("=============================================\n")

    comparar_directorios(dir1_path, dir2_path, args.recursivo)

    print("\n=============================================")
    print("  Comparación completada.")
    print("=============================================")
