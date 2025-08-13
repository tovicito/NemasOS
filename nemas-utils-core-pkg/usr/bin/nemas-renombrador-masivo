#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# renombrador_masivo_gui.py - GUI para renombrar archivos masivamente (Nemás OS)
#

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor

class RenamerWorker(QThread):
    """
    Hilo para previsualizar o ejecutar el renombrado.
    """
    archivo_encontrado = pyqtSignal(str, str)  # old_name, new_name
    progreso_renombrado = pyqtSignal(int, bool, str)  # row, success, message
    finalizado = pyqtSignal(str)

    def __init__(self, modo, directorio, buscar, reemplazar, datos_preview=None):
        super().__init__()
        self.modo = modo  # 'preview' o 'rename'
        self.directorio = directorio
        self.buscar = buscar
        self.reemplazar = reemplazar
        self.datos_preview = datos_preview
        self.activo = True

    def run(self):
        if self.modo == 'preview':
            self.run_preview()
        elif self.modo == 'rename':
            self.run_rename()

    def run_preview(self):
        count = 0
        try:
            for filename in sorted(os.listdir(self.directorio)):
                if not self.activo: break
                if self.buscar in filename and os.path.isfile(os.path.join(self.directorio, filename)):
                    nuevo_nombre = filename.replace(self.buscar, self.reemplazar)
                    self.archivo_encontrado.emit(filename, nuevo_nombre)
                    count += 1
            self.finalizado.emit(f"Previsualización completa. Se encontraron {count} archivos para renombrar.")
        except Exception as e:
            self.finalizado.emit(f"Error en previsualización: {e}")

    def run_rename(self):
        count_ok = 0
        for i, (nombre_actual, nombre_nuevo) in enumerate(self.datos_preview):
            if not self.activo: break
            ruta_actual = os.path.join(self.directorio, nombre_actual)
            ruta_nueva = os.path.join(self.directorio, nombre_nuevo)
            try:
                if not os.path.exists(ruta_actual):
                    raise FileNotFoundError("El archivo original no existe.")
                if os.path.exists(ruta_nueva):
                    raise FileExistsError("Un archivo con el nuevo nombre ya existe.")
                os.rename(ruta_actual, ruta_nueva)
                self.progreso_renombrado.emit(i, True, "Renombrado con éxito")
                count_ok += 1
            except Exception as e:
                self.progreso_renombrado.emit(i, False, str(e))
        self.finalizado.emit(f"Proceso de renombrado completado. {count_ok}/{len(self.datos_preview)} archivos renombrados.")

    def stop(self):
        self.activo = False

class RenombradorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.preview_data = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Renombrador Masivo de Nemás OS')
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()

        # --- Controles ---
        grid = QGridLayout()
        self.linea_directorio = QLineEdit(); self.linea_directorio.setReadOnly(True)
        btn_dir = QPushButton("Seleccionar Directorio..."); btn_dir.clicked.connect(self.seleccionar_directorio)
        self.linea_buscar = QLineEdit(); self.linea_buscar.setPlaceholderText("Texto a buscar")
        self.linea_reemplazar = QLineEdit(); self.linea_reemplazar.setPlaceholderText("Reemplazar con")

        grid.addWidget(QLabel("Directorio:"), 0, 0); grid.addWidget(self.linea_directorio, 0, 1); grid.addWidget(btn_dir, 0, 2)
        grid.addWidget(QLabel("Buscar:"), 1, 0); grid.addWidget(self.linea_buscar, 1, 1, 1, 2)
        grid.addWidget(QLabel("Reemplazar:"), 2, 0); grid.addWidget(self.linea_reemplazar, 2, 1, 1, 2)
        layout.addLayout(grid)

        # --- Botones de Acción ---
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("1. Previsualizar Cambios"); self.btn_preview.clicked.connect(self.iniciar_preview)
        self.btn_rename = QPushButton("2. Aplicar Renombrado"); self.btn_rename.clicked.connect(self.iniciar_renombrado)
        self.btn_rename.setEnabled(False)
        btn_layout.addWidget(self.btn_preview); btn_layout.addWidget(self.btn_rename)
        layout.addLayout(btn_layout)

        # --- Tabla de Vista Previa ---
        self.tabla_preview = QTableWidget(); self.tabla_preview.setColumnCount(3)
        self.tabla_preview.setHorizontalHeaderLabels(["Nombre Actual", "Nombre Nuevo", "Estado"])
        self.tabla_preview.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_preview.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla_preview)

        # --- Estado ---
        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)
        self.setLayout(layout)

    def seleccionar_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio: self.linea_directorio.setText(directorio)

    def iniciar_preview(self):
        directorio = self.linea_directorio.text(); buscar = self.linea_buscar.text()
        if not all([directorio, buscar]):
            QMessageBox.warning(self, "Faltan Datos", "Debes seleccionar un directorio y un texto de búsqueda."); return
        self.reset_ui_state()
        self.worker = RenamerWorker('preview', directorio, buscar, self.linea_reemplazar.text())
        self.worker.archivo_encontrado.connect(self.agregar_a_preview)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.label_estado.setText("Generando previsualización..."); self.worker.start()

    def iniciar_renombrado(self):
        if not self.preview_data:
            QMessageBox.warning(self, "Sin Datos", "Debes generar una previsualización primero."); return

        respuesta = QMessageBox.confirm(self, "Confirmar Renombrado",
            f"¿Estás seguro de que quieres renombrar {len(self.preview_data)} archivos?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if respuesta == QMessageBox.No: return

        self.btn_preview.setEnabled(False); self.btn_rename.setEnabled(False)
        self.worker = RenamerWorker('rename', self.linea_directorio.text(), "", "", self.preview_data)
        self.worker.progreso_renombrado.connect(self.actualizar_fila_estado)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.label_estado.setText("Renombrando archivos..."); self.worker.start()

    def reset_ui_state(self):
        self.tabla_preview.setRowCount(0); self.preview_data = []
        self.btn_rename.setEnabled(False)

    def agregar_a_preview(self, old, new):
        self.preview_data.append((old, new))
        fila = self.tabla_preview.rowCount(); self.tabla_preview.insertRow(fila)
        self.tabla_preview.setItem(fila, 0, QTableWidgetItem(old))
        self.tabla_preview.setItem(fila, 1, QTableWidgetItem(new))
        self.tabla_preview.setItem(fila, 2, QTableWidgetItem("Listo para renombrar"))

    def actualizar_fila_estado(self, fila, exito, mensaje):
        estado_item = self.tabla_preview.item(fila, 2)
        estado_item.setText(mensaje)
        color = QColor("lightgreen") if exito else QColor("salmon")
        for col in range(3):
            self.tabla_preview.item(fila, col).setBackground(color)

    def proceso_finalizado(self, mensaje):
        self.label_estado.setText(mensaje)
        self.btn_preview.setEnabled(True)
        if self.worker.modo == 'preview' and self.preview_data:
            self.btn_rename.setEnabled(True)
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning(): self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = RenombradorGUI(); ventana.show()
    sys.exit(app.exec_())
