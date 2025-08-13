#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import hashlib
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QTextEdit, QLabel
)

class DuplicateFinderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Buscador de Archivos Duplicados')
        self.setGeometry(200, 200, 700, 500)

        layout = QVBoxLayout()
        dir_layout = QHBoxLayout()

        self.dir_path_edit = QLineEdit()
        self.dir_path_edit.setPlaceholderText("Selecciona un directorio...")
        self.browse_btn = QPushButton("Navegar...")
        self.browse_btn.clicked.connect(self.browse_directory)

        dir_layout.addWidget(QLabel("Directorio:"))
        dir_layout.addWidget(self.dir_path_edit)
        dir_layout.addWidget(self.browse_btn)

        self.find_btn = QPushButton("Encontrar Duplicados")
        self.find_btn.clicked.connect(self.find_duplicates)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addLayout(dir_layout)
        layout.addWidget(self.find_btn)
        layout.addWidget(QLabel("Archivos duplicados encontrados:"))
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.dir_path_edit.setText(directory)

    def find_duplicates(self):
        directory = self.dir_path_edit.text()
        if not os.path.isdir(directory):
            self.result_text.setText("Error: El directorio no es válido.")
            return

        self.result_text.setText("Buscando... Esto puede tardar un momento.")
        QApplication.processEvents() # Update the UI

        hashes = defaultdict(list)
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                try:
                    with open(path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        hashes[file_hash].append(path)
                except Exception:
                    # Skip files that can't be read
                    continue

        duplicates = {k: v for k, v in hashes.items() if len(v) > 1}

        if not duplicates:
            self.result_text.setText("No se encontraron archivos duplicados.")
            return

        result_str = ""
        for file_hash, paths in duplicates.items():
            result_str += f"Hash: {file_hash}\n"
            for path in paths:
                result_str += f"  - {path}\n"
            result_str += "\n"

        self.result_text.setText(result_str)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = DuplicateFinderGUI()
    ventana.show()
    sys.exit(app.exec_())
