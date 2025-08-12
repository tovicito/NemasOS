#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# visor_imagenes_gui.py - Un visor de imágenes simple con GUI (Nemás OS)
#

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea, QAction,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

class VisorImagenesGUI(QMainWindow):
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    def __init__(self):
        super().__init__()
        self.lista_imagenes = []
        self.indice_actual = -1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Visor de Imágenes de Nemás OS")
        self.setGeometry(100, 100, 800, 600)

        # --- Widget Central ---
        self.scroll_area = QScrollArea()
        self.label_imagen = QLabel("Abre una imagen para empezar...")
        self.label_imagen.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.label_imagen)
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        # --- Acciones ---
        accion_abrir = QAction("Abrir...", self, triggered=self.abrir_imagen)
        self.accion_anterior = QAction("Anterior", self, triggered=self.imagen_anterior, enabled=False)
        self.accion_siguiente = QAction("Siguiente", self, triggered=self.imagen_siguiente, enabled=False)

        # --- Barra de Menú y Herramientas ---
        menu_archivo = self.menuBar().addMenu("&Archivo")
        menu_archivo.addAction(accion_abrir)

        toolbar = self.addToolBar("Principal")
        toolbar.addAction(accion_abrir)
        toolbar.addAction(self.accion_anterior)
        toolbar.addAction(self.accion_siguiente)

    def abrir_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir Imagen", "",
            f"Imágenes ({' '.join(['*' + f for f in self.SUPPORTED_FORMATS])})")

        if ruta:
            self.cargar_directorio(ruta)

    def cargar_directorio(self, ruta_imagen):
        directorio = os.path.dirname(ruta_imagen)
        self.lista_imagenes = sorted([
            os.path.join(directorio, f) for f in os.listdir(directorio)
            if os.path.splitext(f)[1].lower() in self.SUPPORTED_FORMATS
        ])

        try:
            self.indice_actual = self.lista_imagenes.index(ruta_imagen)
            self.mostrar_imagen_actual()
        except ValueError:
            QMessageBox.critical(self, "Error", "No se pudo encontrar la imagen en la lista del directorio.")

    def mostrar_imagen_actual(self):
        if not self.lista_imagenes: return

        ruta = self.lista_imagenes[self.indice_actual]
        pixmap = QPixmap(ruta)
        if pixmap.isNull():
            self.label_imagen.setText(f"No se pudo cargar la imagen:\n{os.path.basename(ruta)}")
            return

        self.label_imagen.setPixmap(pixmap)
        self.actualizar_estado_navegacion()
        self.setWindowTitle(f"{os.path.basename(ruta)} - Visor de Imágenes Nemás OS")

    def actualizar_estado_navegacion(self):
        tiene_imagenes = len(self.lista_imagenes) > 1
        self.accion_anterior.setEnabled(tiene_imagenes)
        self.accion_siguiente.setEnabled(tiene_imagenes)

    def imagen_anterior(self):
        if not self.lista_imagenes: return
        self.indice_actual = (self.indice_actual - 1) % len(self.lista_imagenes)
        self.mostrar_imagen_actual()

    def imagen_siguiente(self):
        if not self.lista_imagenes: return
        self.indice_actual = (self.indice_actual + 1) % len(self.lista_imagenes)
        self.mostrar_imagen_actual()

    def resizeEvent(self, event):
        # Esta es una forma simple de reescalar, pero pierde calidad si se agranda mucho.
        # Una implementación más avanzada podría recargar el pixmap original.
        if self.label_imagen.pixmap() and not self.label_imagen.pixmap().isNull():
             self.label_imagen.setPixmap(QPixmap(self.lista_imagenes[self.indice_actual]).scaled(
                self.label_imagen.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = VisorImagenesGUI()
    ventana.show()
    sys.exit(app.exec_())
