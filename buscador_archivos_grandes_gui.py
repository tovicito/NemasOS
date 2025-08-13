#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# buscador_archivos_grandes_gui.py - GUI para encontrar archivos grandes (Nemás OS)
#

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QSpinBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class SearchWorker(QThread):
    """
    Hilo de trabajo que busca archivos en segundo plano.
    """
    archivo_encontrado = pyqtSignal(str, float)  # Emite: ruta, tamaño_en_mb
    busqueda_finalizada = pyqtSignal(str)

    def __init__(self, directorio, tamano_min_mb):
        super().__init__()
        self.directorio = directorio
        self.tamano_min_bytes = tamano_min_mb * 1024 * 1024
        self.activo = True

    def run(self):
        num_encontrados = 0
        try:
            for dirpath, _, filenames in os.walk(self.directorio):
                if not self.activo:
                    break
                for filename in filenames:
                    if not self.activo:
                        break
                    ruta_completa = os.path.join(dirpath, filename)
                    try:
                        # Comprobar si es un enlace simbólico antes de getsize
                        if os.path.islink(ruta_completa):
                            continue
                        tamano_archivo_bytes = os.path.getsize(ruta_completa)
                        if tamano_archivo_bytes >= self.tamano_min_bytes:
                            tamano_archivo_mb = tamano_archivo_bytes / (1024 * 1024)
                            self.archivo_encontrado.emit(ruta_completa, tamano_archivo_mb)
                            num_encontrados += 1
                    except FileNotFoundError:
                        continue  # El archivo pudo ser eliminado durante el escaneo
            if self.activo:
                self.busqueda_finalizada.emit(f"Búsqueda completada. Se encontraron {num_encontrados} archivos.")
            else:
                self.busqueda_finalizada.emit("Búsqueda cancelada por el usuario.")
        except Exception as e:
            self.busqueda_finalizada.emit(f"Error durante la búsqueda: {e}")

    def stop(self):
        self.activo = False

class BuscadorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Buscador de Archivos Grandes de Nemás OS')
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()

        # --- Controles de Búsqueda ---
        controles_layout = QHBoxLayout()

        # Selección de directorio
        self.linea_directorio = QLineEdit()
        self.linea_directorio.setPlaceholderText("Selecciona un directorio para buscar...")
        self.linea_directorio.setReadOnly(True)
        btn_seleccionar = QPushButton("Seleccionar Directorio...")
        btn_seleccionar.clicked.connect(self.seleccionar_directorio)

        # Selección de tamaño
        label_tamano = QLabel("Tamaño mínimo (MB):")
        self.spin_tamano = QSpinBox()
        self.spin_tamano.setRange(1, 100000) # 1MB a 100GB
        self.spin_tamano.setValue(100)

        controles_layout.addWidget(btn_seleccionar)
        controles_layout.addWidget(self.linea_directorio, 1)
        controles_layout.addWidget(label_tamano)
        controles_layout.addWidget(self.spin_tamano)
        layout.addLayout(controles_layout)

        # Botón de Iniciar/Cancelar Búsqueda
        self.btn_buscar = QPushButton("Iniciar Búsqueda")
        self.btn_buscar.setStyleSheet("padding: 10px; font-size: 16px;")
        self.btn_buscar.clicked.connect(self.gestionar_busqueda)
        layout.addWidget(self.btn_buscar)

        # --- Tabla de Resultados ---
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(2)
        self.tabla_resultados.setHorizontalHeaderLabels(["Ruta del Archivo", "Tamaño"])
        self.tabla_resultados.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_resultados.setSortingEnabled(True)
        layout.addWidget(self.tabla_resultados)

        # --- Barra de Estado ---
        self.label_estado = QLabel("Estado: Listo. Selecciona un directorio para empezar.")
        layout.addWidget(self.label_estado)

        self.setLayout(layout)

    def seleccionar_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio:
            self.linea_directorio.setText(directorio)

    def gestionar_busqueda(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.btn_buscar.setText("Iniciar Búsqueda")
            self.label_estado.setText("Estado: Cancelando...")
        else:
            directorio = self.linea_directorio.text()
            if not directorio:
                QMessageBox.warning(self, "Falta Directorio", "Por favor, selecciona un directorio antes de iniciar la búsqueda.")
                return

            self.tabla_resultados.setRowCount(0) # Limpiar tabla
            tamano_min = self.spin_tamano.value()

            self.worker = SearchWorker(directorio, tamano_min)
            self.worker.archivo_encontrado.connect(self.anadir_archivo_a_tabla)
            self.worker.busqueda_finalizada.connect(self.busqueda_finalizada)

            self.btn_buscar.setText("Cancelar Búsqueda")
            self.label_estado.setText(f"Estado: Buscando en '{directorio}'...")
            self.worker.start()

    def anadir_archivo_a_tabla(self, ruta, tamano_mb):
        fila = self.tabla_resultados.rowCount()
        self.tabla_resultados.insertRow(fila)

        item_ruta = QTableWidgetItem(ruta)

        item_tamano = QTableWidgetItem()
        item_tamano.setData(Qt.DisplayRole, f"{tamano_mb:.2f} MB")
        item_tamano.setData(Qt.UserRole, tamano_mb) # Usado para ordenar numéricamente

        self.tabla_resultados.setItem(fila, 0, item_ruta)
        self.tabla_resultados.setItem(fila, 1, item_tamano)

    def busqueda_finalizada(self, mensaje):
        self.label_estado.setText(f"Estado: {mensaje}")
        self.btn_buscar.setText("Iniciar Búsqueda")
        self.worker = None
        # Ordenar por tamaño (columna 1) de forma descendente
        self.tabla_resultados.sortItems(1, Qt.DescendingOrder)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = BuscadorGUI()
    ventana.show()
    sys.exit(app.exec_())
