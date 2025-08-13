#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# buscar_reemplazar_gui.py - GUI para buscar y reemplazar texto en archivos (Nemás OS)
#

import sys
import os
import fnmatch
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
    QFileDialog, QHeaderView, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont

class SearchReplaceWorker(QThread):
    """ Hilo para buscar o reemplazar texto en archivos. """
    coincidencia_encontrada = pyqtSignal(str, int, str, str)  # archivo, linea_num, linea_vieja, linea_nueva
    archivo_procesado = pyqtSignal(int, bool, str)  # fila, exito, mensaje
    finalizado = pyqtSignal(str)

    def __init__(self, modo, **kwargs):
        super().__init__()
        self.modo = modo
        self.kwargs = kwargs
        self.activo = True

    def run(self):
        try:
            if self.modo == 'preview': self.run_preview()
            elif self.modo == 'replace': self.run_replace()
        except Exception as e:
            self.finalizado.emit(f"Error inesperado: {e}")

    def run_preview(self):
        directorio = self.kwargs['directorio']; patron = self.kwargs['patron']
        buscar = self.kwargs['buscar']; reemplazar = self.kwargs['reemplazar']
        count = 0
        for dirpath, _, filenames in os.walk(directorio):
            if not self.activo: break
            for filename in fnmatch.filter(filenames, patron):
                if not self.activo: break
                ruta_completa = os.path.join(dirpath, filename)
                try:
                    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, linea in enumerate(f, 1):
                            if buscar in linea:
                                linea_nueva = linea.replace(buscar, reemplazar)
                                self.coincidencia_encontrada.emit(ruta_completa, i, linea.strip(), linea_nueva.strip())
                                count += 1
                except Exception:
                    continue # Ignorar archivos que no se pueden leer
        self.finalizado.emit(f"Previsualización completa. {count} coincidencias encontradas.")

    def run_replace(self):
        cambios_por_archivo = self.kwargs['cambios']
        count_ok = 0
        for i, (archivo, linea_num, _, linea_nueva) in enumerate(cambios_por_archivo):
            if not self.activo: break
            try:
                with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                    lineas = f.readlines()

                lineas[linea_num - 1] = linea_nueva + '\n'

                with open(archivo, 'w', encoding='utf-8') as f:
                    f.writelines(lineas)

                self.archivo_procesado.emit(i, True, "Reemplazado")
                count_ok += 1
            except Exception as e:
                self.archivo_procesado.emit(i, False, str(e))
        self.finalizado.emit(f"Proceso completado. {count_ok}/{len(cambios_por_archivo)} cambios aplicados.")

    def stop(self): self.activo = False

class BuscadorReemplazadorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None; self.preview_data = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Buscar y Reemplazar en Archivos')
        self.setGeometry(150, 150, 900, 700)
        layout = QVBoxLayout(self)

        # --- Controles ---
        grid = QGridLayout()
        self.linea_dir = QLineEdit(); self.linea_dir.setPlaceholderText("Directorio a explorar")
        btn_dir = QPushButton("Seleccionar..."); btn_dir.clicked.connect(self.seleccionar_directorio)
        self.linea_patron = QLineEdit("*.txt"); self.linea_patron.setToolTip("Ej: *.py, *.html, * (todos)")
        self.linea_buscar = QLineEdit(); self.linea_buscar.setPlaceholderText("Texto a buscar")
        self.texto_reemplazar = QTextEdit(); self.texto_reemplazar.setFixedHeight(80)

        grid.addWidget(QLabel("Directorio:"), 0, 0); grid.addWidget(self.linea_dir, 0, 1); grid.addWidget(btn_dir, 0, 2)
        grid.addWidget(QLabel("Filtro de Archivos:"), 1, 0); grid.addWidget(self.linea_patron, 1, 1, 1, 2)
        grid.addWidget(QLabel("Buscar:"), 2, 0); grid.addWidget(self.linea_buscar, 2, 1, 1, 2)
        grid.addWidget(QLabel("Reemplazar con:"), 3, 0); grid.addWidget(self.texto_reemplazar, 3, 1, 1, 2)
        layout.addLayout(grid)

        # --- Botones de Acción ---
        btn_layout = QHBoxLayout()
        self.btn_preview = QPushButton("1. Previsualizar Cambios"); self.btn_preview.clicked.connect(self.iniciar_preview)
        self.btn_replace = QPushButton("2. Aplicar Cambios"); self.btn_replace.clicked.connect(self.iniciar_reemplazo)
        self.btn_replace.setEnabled(False)
        btn_layout.addWidget(self.btn_preview); btn_layout.addWidget(self.btn_replace)
        layout.addLayout(btn_layout)

        # --- Tabla de Vista Previa ---
        self.tabla_preview = QTableWidget(); self.tabla_preview.setColumnCount(4)
        self.tabla_preview.setHorizontalHeaderLabels(["Archivo", "Línea", "Contenido Original", "Contenido Nuevo"])
        self.tabla_preview.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla_preview.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla_preview.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.tabla_preview)
        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)
        self.setLayout(layout)

    def seleccionar_directorio(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio: self.linea_dir.setText(directorio)

    def iniciar_preview(self):
        params = {'directorio': self.linea_dir.text(), 'patron': self.linea_patron.text(), 'buscar': self.linea_buscar.text(), 'reemplazar': self.texto_reemplazar.toPlainText()}
        if not all([params['directorio'], params['patron'], params['buscar']]):
            QMessageBox.warning(self, "Faltan Datos", "Directorio, filtro y texto de búsqueda son obligatorios."); return
        self.tabla_preview.setRowCount(0); self.preview_data = []
        self.btn_replace.setEnabled(False)
        self.worker = SearchReplaceWorker('preview', **params)
        self.worker.coincidencia_encontrada.connect(self.agregar_a_preview)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.label_estado.setText("Buscando coincidencias..."); self.worker.start()

    def agregar_a_preview(self, archivo, linea_num, linea_vieja, linea_nueva):
        self.preview_data.append((archivo, linea_num, linea_vieja, linea_nueva))
        row = self.tabla_preview.rowCount(); self.tabla_preview.insertRow(row)
        self.tabla_preview.setItem(row, 0, QTableWidgetItem(archivo)); self.tabla_preview.setItem(row, 1, QTableWidgetItem(str(linea_num)))
        self.tabla_preview.setItem(row, 2, QTableWidgetItem(linea_vieja)); self.tabla_preview.setItem(row, 3, QTableWidgetItem(linea_nueva))

    def iniciar_reemplazo(self):
        if not self.preview_data: return
        resp = QMessageBox.question(self, "Confirmar", f"¿Aplicar {len(self.preview_data)} cambios?", QMessageBox.Yes | QMessageBox.No)
        if resp == QMessageBox.No: return

        # Agrupar cambios por archivo para un reemplazo más eficiente
        cambios_agrupados = {}
        for archivo, linea_num, _, linea_nueva in self.preview_data:
            if archivo not in cambios_agrupados:
                cambios_agrupados[archivo] = {}
            cambios_agrupados[archivo][linea_num - 1] = linea_nueva + '\n' # Guardar índice y contenido

        self.label_estado.setText("Aplicando cambios...")
        # Esta implementación es más compleja, la simplificaré para el ejemplo
        # La forma correcta sería reescribir cada archivo una vez.
        # Por simplicidad aquí, se procesará cada cambio individualmente,
        # lo que es ineficiente si hay múltiples cambios en un mismo archivo.
        self.worker = SearchReplaceWorker('replace', cambios=self.preview_data)
        self.worker.archivo_procesado.connect(self.actualizar_fila_reemplazo)
        self.worker.finalizado.connect(self.proceso_finalizado)
        self.worker.start()

    def actualizar_fila_reemplazo(self, fila, exito, mensaje):
        color = QColor("lightgreen") if exito else QColor("salmon")
        for col in range(self.tabla_preview.columnCount()):
            self.tabla_preview.item(fila, col).setBackground(color)

    def proceso_finalizado(self, mensaje):
        self.label_estado.setText(mensaje)
        if self.worker.modo == 'preview' and self.preview_data: self.btn_replace.setEnabled(True)
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning(): self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = BuscadorReemplazadorGUI(); ventana.show()
    sys.exit(app.exec_())
