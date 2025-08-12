#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# organizador_descargas.py - Organiza archivos en la carpeta de Descargas (Nemás OS)
#

import os
import shutil
from pathlib import Path

# --- Configuración ---
# Elige la carpeta de descargas del usuario actual.
# En español, la carpeta de Descargas suele ser "Descargas".
CARPETA_DESCARGAS = Path.home() / "Descargas"

# Define las carpetas de destino y las extensiones de archivo asociadas.
CATEGORIAS = {
    "Imágenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documentos": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".txt", ".rtf", ".csv"],
    "Vídeos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "Música": [".mp3", ".wav", ".ogg", ".flac", ".aac"],
    "Comprimidos": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Programas": [".deb", ".AppImage", ".sh", ".py", ".exe", ".msi"],
    "Otros": [] # Para todo lo demás
}

def organizar_archivos():
    """
    Función principal que escanea la carpeta de descargas y mueve los archivos.
    """
    print("=============================================")
    print("  Organizador de Descargas de Nemás OS")
    print("=============================================")
    print(f"Buscando archivos en: {CARPETA_DESCARGAS}\\n")

    if not CARPETA_DESCARGAS.is_dir():
        print(f"Error: La carpeta de descargas '{CARPETA_DESCARGAS}' no existe.")
        print("Por favor, crea la carpeta o ajusta la variable 'CARPETA_DESCARGAS' en el script.")
        return

    # Crear las carpetas de categoría si no existen
    for categoria in list(CATEGORIAS.keys()):
        (CARPETA_DESCARGAS / categoria).mkdir(exist_ok=True)

    # Recorrer todos los archivos en la carpeta de descargas
    archivos_movidos = 0
    for archivo in CARPETA_DESCARGAS.iterdir():
        if archivo.is_file():
            # Ignorar archivos ocultos (que empiezan por .)
            if archivo.name.startswith('.'):
                continue

            sufijo = archivo.suffix.lower()
            categoria_destino = "Otros" # Por defecto

            # Encontrar la categoría para el archivo
            for categoria, sufijos in CATEGORIAS.items():
                if sufijo in sufijos:
                    categoria_destino = categoria
                    break

            # Mover el archivo
            destino = CARPETA_DESCARGAS / categoria_destino / archivo.name
            try:
                shutil.move(str(archivo), str(destino))
                print(f"Movido: '{archivo.name}' -> {categoria_destino}/")
                archivos_movidos += 1
            except Exception as e:
                print(f"Error al mover '{archivo.name}': {e}")

    print("\\n---------------------------------------------")
    if archivos_movidos > 0:
        print(f"¡Organización completada! Se han movido {archivos_movidos} archivos.")
    else:
        print("No se encontraron archivos nuevos para organizar.")
    print("=============================================")


if __name__ == "__main__":
    # Para Nemás OS, es común tener la carpeta "Descargas" en vez de "Downloads"
    if not CARPETA_DESCARGAS.exists():
        CARPETA_DESCARGAS_EN = Path.home() / "Downloads"
        if CARPETA_DESCARGAS_EN.exists():
            CARPETA_DESCARGAS = CARPETA_DESCARGAS_EN

    organizar_archivos()
