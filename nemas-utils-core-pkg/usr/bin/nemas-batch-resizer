#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QSpinBox, QListWidget
)
from PIL import Image

class BatchResizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Redimensionador de Imágenes por Lotes')
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.add_btn = QPushButton("Añadir Imágenes...")
        self.add_btn.clicked.connect(self.add_images)

        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 4096); self.width_spin.setValue(800)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 4096); self.height_spin.setValue(600)
        size_layout.addWidget(QLabel("Ancho:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Alto:"))
        size_layout.addWidget(self.height_spin)

        self.resize_btn = QPushButton("Redimensionar y Guardar...")
        self.resize_btn.clicked.connect(self.resize_images)

        layout.addWidget(self.add_btn)
        layout.addWidget(self.file_list)
        layout.addLayout(size_layout)
        layout.addWidget(self.resize_btn)
        self.setLayout(layout)

    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Imágenes", "", "Images (*.png *.jpg)")
        self.files.extend(files)
        for f in files:
            self.file_list.addItem(os.path.basename(f))

    def resize_images(self):
        if not self.files: return

        save_dir = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")
        if not save_dir: return

        width = self.width_spin.value()
        height = self.height_spin.value()

        for f in self.files:
            try:
                img = Image.open(f)
                img_resized = img.resize((width, height), Image.LANCZOS)
                base, ext = os.path.splitext(os.path.basename(f))
                save_path = os.path.join(save_dir, f"{base}_resized{ext}")
                img_resized.save(save_path)
            except Exception as e:
                print(f"Error processing {f}: {e}") # Log error to console

        # Add a message box for completion
        self.file_list.clear()
        self.files = []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = BatchResizerGUI()
    ventana.show()
    sys.exit(app.exec_())
