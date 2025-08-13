#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# contador_lineas_gui.py - GUI para contar líneas, palabras y caracteres (Nemás OS)
#

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class CountWorker(QThread):
    """ Hilo para contar en segundo plano. """
    archivo_procesado = pyqtSignal(str, int, int, int) # ruta, lineas, palabras, caracteres
    finalizado = pyqtSignal(int, int, int) # totales

    def __init__(self, archivos):
        super().__init__()
        self.archivos = archivos

    def run(self):
        total_lineas, total_palabras, total_caracteres = 0, 0, 0
        for ruta in self.archivos:
            try:
                with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                    lineas = contenido.count('\n') + 1 if contenido else 0
                    palabras = len(contenido.split())
                    caracteres = len(contenido)

                    self.archivo_procesado.emit(ruta, lineas, palabras, caracteres)
                    total_lineas += lineas
                    total_palabras += palabras
                    total_caracteres += caracteres
            except Exception:
                # Emitir con valores cero si hay error de lectura
                self.archivo_procesado.emit(ruta, 0, 0, 0)

        self.finalizado.emit(total_lineas, total_palabras, total_caracteres)

class ContadorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Contador de Líneas, Palabras y Caracteres')
        self.setGeometry(300, 300, 800, 600)
        layout = QHBoxLayout(self)

        # --- Panel Izquierdo (Selección de Archivos) ---
        panel_izq = QVBoxLayout()
        self.lista_archivos = QListWidget()
        btn_add_files = QPushButton("Añadir Archivos..."); btn_add_files.clicked.connect(self.anadir_archivos)
        btn_add_dir = QPushButton("Añadir Directorio..."); btn_add_dir.clicked.connect(self.anadir_directorio)
        btn_clear = QPushButton("Limpiar Lista"); btn_clear.clicked.connect(self.lista_archivos.clear)
        btn_process = QPushButton("Procesar Archivos"); btn_process.clicked.connect(self.procesar)
        panel_izq.addWidget(self.lista_archivos)
        panel_izq.addWidget(btn_add_files); panel_izq.addWidget(btn_add_dir)
        panel_izq.addWidget(btn_clear); panel_izq.addWidget(btn_process)

        # --- Panel Derecho (Resultados) ---
        panel_der = QVBoxLayout()
        self.tabla_resultados = QTableWidget(); self.tabla_resultados.setColumnCount(4)
        self.tabla_resultados.setHorizontalHeaderLabels(["Archivo", "Líneas", "Palabras", "Caracteres"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_resultados.setSortingEnabled(True)
        panel_der.addWidget(self.tabla_resultados)

        layout.addLayout(panel_izq, 1); layout.addLayout(panel_der, 2)

    def anadir_archivos(self):
        archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Archivos", os.path.expanduser("~"))
        if archivos:
            self.lista_archivos.addItems(archivos)

    def anadir_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio:
            for dirpath, _, filenames in os.walk(directorio):
                for f in filenames:
                    self.lista_archivos.addItem(os.path.join(dirpath, f))

    def procesar(self):
        if self.lista_archivos.count() == 0: return

        self.tabla_resultados.setRowCount(0)
        self.tabla_resultados.setSortingEnabled(False)

        archivos_a_procesar = [self.lista_archivos.item(i).text() for i in range(self.lista_archivos.count())]

        self.worker = CountWorker(archivos_a_procesar)
        self.worker.archivo_procesado.connect(self.agregar_fila_resultado)
        self.worker.finalizado.connect(self.agregar_fila_total)
        self.worker.start()

    def agregar_fila_resultado(self, ruta, lineas, palabras, caracteres):
        row = self.tabla_resultados.rowCount(); self.tabla_resultados.insertRow(row)
        self.tabla_resultados.setItem(row, 0, QTableWidgetItem(os.path.basename(ruta)))
        self.tabla_resultados.setItem(row, 1, self.create_numeric_item(lineas))
        self.tabla_resultados.setItem(row, 2, self.create_numeric_item(palabras))
        self.tabla_resultados.setItem(row, 3, self.create_numeric_item(caracteres))

    def agregar_fila_total(self, total_l, total_p, total_c):
        row = self.tabla_resultados.rowCount(); self.tabla_resultados.insertRow(row)

        total_item = QTableWidgetItem("TOTAL")
        font = total_item.font(); font.setBold(True); total_item.setFont(font)

        self.tabla_resultados.setItem(row, 0, total_item)
        self.tabla_resultados.setItem(row, 1, self.create_numeric_item(total_l, bold=True))
        self.tabla_resultados.setItem(row, 2, self.create_numeric_item(total_p, bold=True))
        self.tabla_resultados.setItem(row, 3, self.create_numeric_item(total_c, bold=True))
        self.tabla_resultados.setSortingEnabled(True)

    def create_numeric_item(self, value, bold=False):
        item = QTableWidgetItem(f"{value:,}")
        item.setData(Qt.UserRole, value)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if bold:
            font = item.font(); font.setBold(True); item.setFont(font)
        return item

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ContadorGUI()
    ventana.show()
    sys.exit(app.exec_())
