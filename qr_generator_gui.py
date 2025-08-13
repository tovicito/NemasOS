#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage

class QrGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generador de Códigos QR')
        self.setGeometry(300, 300, 400, 400)
        layout = QVBoxLayout()

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Texto o URL para codificar")

        self.generate_btn = QPushButton("Generar QR")
        self.generate_btn.clicked.connect(self.generate_qr)

        self.qr_label = QLabel("Aquí se mostrará el código QR")
        self.qr_label.setScaledContents(True)

        self.save_btn = QPushButton("Guardar Imagen...")
        self.save_btn.clicked.connect(self.save_qr)
        self.save_btn.setEnabled(False)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.qr_label)
        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.qr_image = None

    def generate_qr(self):
        text = self.text_edit.text()
        if not text:
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        self.qr_image = qr.make_image(fill='black', back_color='white')

        # Display in QLabel
        img = self.qr_image.convert("RGBA")
        qimage = QImage(img.tobytes("raw", "RGBA"), img.size[0], img.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qimage)
        self.qr_label.setPixmap(pixmap)
        self.save_btn.setEnabled(True)

    def save_qr(self):
        if self.qr_image:
            save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Código QR", "", "PNG Image (*.png)")
            if save_path:
                self.qr_image.save(save_path)

if __name__ == '__main__':
    # requires python3-qrcode and python3-pil
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = QrGeneratorGUI()
    ventana.show()
    sys.exit(app.exec_())
