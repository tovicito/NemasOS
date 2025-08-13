#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# extractor_gui.py - GUI para extraer archivos comprimidos (Nemás OS)
#

import sys
import os
import zipfile
import tarfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal

class ExtractWorker(QThread):
    """ Hilo para previsualizar o extraer archivos. """
    preview_listo = pyqtSignal(list)
    progreso = pyqtSignal(int)
    finalizado = pyqtSignal(bool, str)

    def __init__(self, modo, archivo, destino=None):
        super().__init__()
        self.modo = modo
        self.archivo = archivo
        self.destino = destino

    def run(self):
        try:
            if self.modo == 'preview':
                self.run_preview()
            elif self.modo == 'extract':
                self.run_extract()
        except Exception as e:
            self.finalizado.emit(False, str(e))

    def run_preview(self):
        try:
            if self.archivo.endswith('.zip'):
                with zipfile.ZipFile(self.archivo, 'r') as zf:
                    self.preview_listo.emit(zf.namelist())
            elif self.archivo.endswith(('.tar.gz', '.tgz', '.tar')):
                with tarfile.open(self.archivo, 'r:*') as tf:
                    self.preview_listo.emit(tf.getnames())
            else:
                raise TypeError("Formato de archivo no soportado.")
        except Exception as e:
            self.finalizado.emit(False, f"No se pudo leer el archivo: {e}")

    def run_extract(self):
        try:
            if self.archivo.endswith('.zip'):
                with zipfile.ZipFile(self.archivo, 'r') as zf:
                    miembros = zf.infolist()
                    for i, miembro in enumerate(miembros):
                        zf.extract(miembro, self.destino)
                        self.progreso.emit(int((i + 1) * 100 / len(miembros)))
            elif self.archivo.endswith(('.tar.gz', '.tgz', '.tar')):
                with tarfile.open(self.archivo, 'r:*') as tf:
                    miembros = tf.getmembers()
                    for i, miembro in enumerate(miembros):
                        tf.extract(miembro, self.destino)
                        self.progreso.emit(int((i + 1) * 100 / len(miembros)))
            self.finalizado.emit(True, "Extracción completada con éxito.")
        except Exception as e:
            self.finalizado.emit(False, f"Error durante la extracción: {e}")

class ExtractorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Extractor de Archivos de Nemás OS')
        self.setGeometry(300, 300, 700, 500)
        layout = QVBoxLayout(self)

        # --- Selección ---
        grid = QGridLayout()
        self.linea_archivo = QLineEdit(); self.linea_archivo.setPlaceholderText("Selecciona un archivo (.zip, .tar.gz, etc.)")
        btn_sel_arc = QPushButton("Seleccionar Archivo..."); btn_sel_arc.clicked.connect(self.seleccionar_archivo)
        self.linea_destino = QLineEdit(); self.linea_destino.setPlaceholderText("Selecciona una carpeta de destino")
        btn_sel_dest = QPushButton("Seleccionar Destino..."); btn_sel_dest.clicked.connect(self.seleccionar_destino)
        grid.addWidget(QLabel("Archivo:"), 0, 0); grid.addWidget(self.linea_archivo, 0, 1); grid.addWidget(btn_sel_arc, 0, 2)
        grid.addWidget(QLabel("Destino:"), 1, 0); grid.addWidget(self.linea_destino, 1, 1); grid.addWidget(btn_sel_dest, 1, 2)
        layout.addLayout(grid)

        # --- Vista Previa ---
        self.tabla_contenido = QTableWidget(); self.tabla_contenido.setColumnCount(1)
        self.tabla_contenido.setHorizontalHeaderLabels(["Contenido del Archivo"])
        self.tabla_contenido.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.tabla_contenido)

        # --- Acción y Progreso ---
        bottom_layout = QHBoxLayout()
        self.btn_extraer = QPushButton("Extraer Archivos"); self.btn_extraer.setEnabled(False)
        self.btn_extraer.clicked.connect(self.iniciar_extraccion)
        self.progreso = QProgressBar(); self.progreso.setValue(0)
        bottom_layout.addWidget(self.btn_extraer, 1); bottom_layout.addWidget(self.progreso, 2)
        layout.addLayout(bottom_layout)

    def seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos Comprimidos (*.zip *.tar.gz *.tgz *.tar)")
        if ruta:
            self.linea_archivo.setText(ruta)
            self.linea_destino.setText(os.path.dirname(ruta))
            self.iniciar_preview()

    def seleccionar_destino(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Destino", os.path.expanduser("~"))
        if directorio: self.linea_destino.setText(directorio)

    def iniciar_preview(self):
        archivo = self.linea_archivo.text()
        if not archivo: return
        self.tabla_contenido.setRowCount(0)
        self.btn_extraer.setEnabled(False)
        self.worker = ExtractWorker('preview', archivo)
        self.worker.preview_listo.connect(self.poblar_preview)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.worker.start()

    def poblar_preview(self, filelist):
        self.tabla_contenido.setRowCount(len(filelist))
        for i, item in enumerate(filelist):
            self.tabla_contenido.setItem(i, 0, QTableWidgetItem(item))
        self.btn_extraer.setEnabled(True)

    def iniciar_extraccion(self):
        archivo = self.linea_archivo.text(); destino = self.linea_destino.text()
        if not all([archivo, destino]):
            QMessageBox.warning(self, "Datos Incompletos", "Debes seleccionar un archivo y un destino."); return

        self.btn_extraer.setEnabled(False)
        self.progreso.setValue(0)
        self.worker = ExtractWorker('extract', archivo, destino)
        self.worker.progreso.connect(self.progreso.setValue)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.worker.start()

    def proceso_finalizado(self, exito, mensaje):
        self.btn_extraer.setEnabled(True)
        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
        else:
            QMessageBox.critical(self, "Error", mensaje)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ExtractorGUI()
    ventana.show()
    sys.exit(app.exec_())
