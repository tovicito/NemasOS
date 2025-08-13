#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QTextEdit, QLabel, QCheckBox
)

class EmptyFolderDeleterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Eliminador de Carpetas Vacías')
        self.setGeometry(200, 200, 700, 500)

        layout = QVBoxLayout()
        dir_layout = QHBoxLayout()

        self.dir_path_edit = QLineEdit()
        self.browse_btn = QPushButton("Navegar...")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(QLabel("Directorio:"))
        dir_layout.addWidget(self.dir_path_edit)
        dir_layout.addWidget(self.browse_btn)

        self.dry_run_check = QCheckBox("Modo de simulación (no eliminar nada)")
        self.dry_run_check.setChecked(True)

        self.delete_btn = QPushButton("Buscar y Eliminar Carpetas Vacías")
        self.delete_btn.clicked.connect(self.delete_empty_folders)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(dir_layout)
        layout.addWidget(self.dry_run_check)
        layout.addWidget(self.delete_btn)
        layout.addWidget(QLabel("Registro de operaciones:"))
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.dir_path_edit.setText(directory)

    def delete_empty_folders(self):
        start_path = self.dir_path_edit.text()
        if not os.path.isdir(start_path):
            self.result_text.setText("Error: El directorio no es válido.")
            return

        is_dry_run = self.dry_run_check.isChecked()
        self.result_text.clear()

        if is_dry_run:
            self.result_text.append("--- MODO DE SIMULACIÓN ---\n")
        else:
            self.result_text.append("--- MODO DE ELIMINACIÓN REAL ---\n")

        QApplication.processEvents()

        deleted_folders = []
        for dirpath, dirnames, filenames in os.walk(start_path, topdown=False):
            if not dirnames and not filenames:
                try:
                    if not is_dry_run:
                        os.rmdir(dirpath)
                    self.result_text.append(f"Eliminada: {dirpath}\n")
                    deleted_folders.append(dirpath)
                except OSError as e:
                    self.result_text.append(f"Error al eliminar {dirpath}: {e}\n")

        if not deleted_folders:
            self.result_text.append("No se encontraron carpetas vacías.")
        else:
            self.result_text.append(f"\nProceso completado. Total de carpetas eliminadas: {len(deleted_folders)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = EmptyFolderDeleterGUI()
    ventana.show()
    sys.exit(app.exec_())
