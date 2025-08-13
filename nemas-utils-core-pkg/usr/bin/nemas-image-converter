#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox
)
from PIL import Image

class ImageConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Convertidor de Imágenes')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.label_file = QLabel("No se ha seleccionado ningún archivo.")
        self.browse_btn = QPushButton("Seleccionar Imagen...")
        self.browse_btn.clicked.connect(self.browse_file)

        self.combo_format = QComboBox()
        self.combo_format.addItems(["PNG", "JPEG", "BMP", "GIF", "TIFF"])

        self.convert_btn = QPushButton("Convertir y Guardar")
        self.convert_btn.clicked.connect(self.convert_image)
        self.convert_btn.setEnabled(False)

        layout.addWidget(self.label_file)
        layout.addWidget(self.browse_btn)
        layout.addWidget(QLabel("Convertir a:"))
        layout.addWidget(self.combo_format)
        layout.addWidget(self.convert_btn)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.input_file = file_path
            self.label_file.setText(f"Archivo: {os.path.basename(file_path)}")
            self.convert_btn.setEnabled(True)

    def convert_image(self):
        if not self.input_file:
            return

        target_format = self.combo_format.currentText()

        # Suggest a filename for saving
        base, _ = os.path.splitext(self.input_file)
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar como...", f"{base}.{target_format.lower()}", f"{target_format} Files (*.{target_format.lower()})")

        if save_path:
            try:
                img = Image.open(self.input_file).convert("RGB" if target_format == 'JPEG' else "RGBA")
                img.save(save_path, format=target_format)
                self.label_file.setText(f"¡Convertido y guardado en {save_path}!")
            except Exception as e:
                self.label_file.setText(f"Error: {e}")

if __name__ == '__main__':
    # Requires python3-pil
    import os
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ImageConverterGUI()
    ventana.show()
    sys.exit(app.exec_())
