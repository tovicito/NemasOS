#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# comparador_directorios_gui.py - GUI para comparar directorios (Nemás OS)
#

import sys
import os
import filecmp
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QListWidget,
    QFileDialog, QCheckBox, QTabWidget, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

class CompareWorker(QThread):
    """
    Hilo de trabajo para comparar directorios en segundo plano.
    """
    comparacion_finalizada = pyqtSignal(dict)

    def __init__(self, dir1, dir2, recursivo):
        super().__init__()
        self.dir1 = dir1
        self.dir2 = dir2
        self.recursivo = recursivo
        self.activo = True

    def run(self):
        resultados = {'solo_en_1': [], 'solo_en_2': [], 'diferentes': []}
        try:
            self._comparar_recursivamente(self.dir1, self.dir2, resultados)
            self.comparacion_finalizada.emit(resultados)
        except Exception as e:
            # En caso de un error inesperado, podemos emitir un diccionario de error
            self.comparacion_finalizada.emit({'error': str(e)})

    def _comparar_recursivamente(self, dir1, dir2, resultados):
        if not self.activo: return

        comparador = filecmp.dircmp(dir1, dir2)

        # Obtener la ruta relativa para mostrarla en la UI
        base_path = Path(self.dir1)

        # Archivos solo en dir1
        for f in comparador.left_only:
            resultados['solo_en_1'].append(str(Path(dir1).relative_to(base_path) / f))
        # Archivos solo en dir2
        for f in comparador.right_only:
            resultados['solo_en_2'].append(str(Path(dir1).relative_to(base_path) / f))
        # Archivos con diferencias
        for f in comparador.diff_files:
            resultados['diferentes'].append(str(Path(dir1).relative_to(base_path) / f))

        if self.recursivo:
            for sub_dir in comparador.common_dirs:
                if not self.activo: break
                self._comparar_recursivamente(os.path.join(dir1, sub_dir), os.path.join(dir2, sub_dir), resultados)

    def stop(self):
        self.activo = False

class ComparadorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Comparador de Directorios de Nemás OS')
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()

        # --- Selección de Directorios ---
        grid = QGridLayout()
        self.linea_dir1 = QLineEdit(); self.linea_dir1.setPlaceholderText("Directorio base")
        self.linea_dir2 = QLineEdit(); self.linea_dir2.setPlaceholderText("Directorio a comparar")
        btn_dir1 = QPushButton("Seleccionar..."); btn_dir1.clicked.connect(lambda: self.seleccionar_directorio(self.linea_dir1))
        btn_dir2 = QPushButton("Seleccionar..."); btn_dir2.clicked.connect(lambda: self.seleccionar_directorio(self.linea_dir2))
        grid.addWidget(QLabel("Directorio 1:"), 0, 0); grid.addWidget(self.linea_dir1, 0, 1); grid.addWidget(btn_dir1, 0, 2)
        grid.addWidget(QLabel("Directorio 2:"), 1, 0); grid.addWidget(self.linea_dir2, 1, 1); grid.addWidget(btn_dir2, 1, 2)
        layout.addLayout(grid)

        # --- Opciones y Acción ---
        opciones_layout = QHBoxLayout()
        self.check_recursivo = QCheckBox("Comparación Recursiva")
        self.check_recursivo.setChecked(True)
        self.btn_comparar = QPushButton("Comparar Directorios")
        self.btn_comparar.clicked.connect(self.iniciar_comparacion)
        opciones_layout.addWidget(self.check_recursivo); opciones_layout.addStretch(1); opciones_layout.addWidget(self.btn_comparar)
        layout.addLayout(opciones_layout)

        # --- Resultados en Pestañas ---
        self.tabs = QTabWidget()
        self.lista_solo1 = QListWidget()
        self.lista_solo2 = QListWidget()
        self.lista_diferentes = QListWidget()
        self.tabs.addTab(self.lista_solo1, "Archivos solo en Directorio 1 (0)")
        self.tabs.addTab(self.lista_solo2, "Archivos solo en Directorio 2 (0)")
        self.tabs.addTab(self.lista_diferentes, "Archivos Diferentes (0)")
        layout.addWidget(self.tabs)

        # --- Estado ---
        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)
        self.setLayout(layout)

    def seleccionar_directorio(self, linea_edit):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio: linea_edit.setText(directorio)

    def iniciar_comparacion(self):
        dir1 = self.linea_dir1.text(); dir2 = self.linea_dir2.text()
        if not all([dir1, dir2]):
            QMessageBox.warning(self, "Faltan Datos", "Debes seleccionar dos directorios."); return

        self.limpiar_resultados()
        self.label_estado.setText("Comparando...")
        self.btn_comparar.setEnabled(False)

        self.worker = CompareWorker(dir1, dir2, self.check_recursivo.isChecked())
        self.worker.comparacion_finalizada.connect(self.mostrar_resultados)
        self.worker.start()

    def limpiar_resultados(self):
        self.lista_solo1.clear(); self.lista_solo2.clear(); self.lista_diferentes.clear()
        self.tabs.setTabText(0, "Archivos solo en Directorio 1 (0)")
        self.tabs.setTabText(1, "Archivos solo en Directorio 2 (0)")
        self.tabs.setTabText(2, "Archivos Diferentes (0)")

    def mostrar_resultados(self, resultados):
        if 'error' in resultados:
            self.label_estado.setText(f"Error: {resultados['error']}")
            QMessageBox.critical(self, "Error", f"Ocurrió un error durante la comparación:\n{resultados['error']}")
        else:
            self.lista_solo1.addItems(sorted(resultados['solo_en_1']))
            self.lista_solo2.addItems(sorted(resultados['solo_en_2']))
            self.lista_diferentes.addItems(sorted(resultados['diferentes']))

            self.tabs.setTabText(0, f"Archivos solo en Directorio 1 ({len(resultados['solo_en_1'])})")
            self.tabs.setTabText(1, f"Archivos solo en Directorio 2 ({len(resultados['solo_en_2'])})")
            self.tabs.setTabText(2, f"Archivos Diferentes ({len(resultados['diferentes'])})")

            self.label_estado.setText("Comparación completada.")

        self.btn_comparar.setEnabled(True)
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning(): self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = ComparadorGUI(); ventana.show()
    sys.exit(app.exec_())
