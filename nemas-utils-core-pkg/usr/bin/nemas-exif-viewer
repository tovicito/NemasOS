#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QTextEdit
)
from PIL import Image
from PIL.ExifTags import TAGS

class ExifViewerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor de Datos EXIF')
        self.setGeometry(300, 300, 500, 600)
        layout = QVBoxLayout()

        self.browse_btn = QPushButton("Seleccionar Imagen...")
        self.browse_btn.clicked.connect(self.view_exif)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        layout.addWidget(self.browse_btn)
        layout.addWidget(self.result_text)
        self.setLayout(layout)

    def view_exif(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Images (*.jpg *.jpeg *.tiff)")
        if not file_path:
            return

        try:
            img = Image.open(file_path)
            exif_data = img._getexif()

            if not exif_data:
                self.result_text.setText("No se encontraron datos EXIF en la imagen.")
                return

            result = f"Datos EXIF para: {os.path.basename(file_path)}\n\n"
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    value = value.decode(errors='ignore')
                result += f"{tag}: {value}\n"

            self.result_text.setText(result)

        except Exception as e:
            self.result_text.setText(f"Error al leer el archivo: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ExifViewerGUI()
    ventana.show()
    sys.exit(app.exec_())
