#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QListWidget
)

class NameGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.names = {
            "English": (["John", "James", "Robert", "Michael", "William"], ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth"]),
            "Spanish": (["Jose", "Luis", "Juan", "Carlos", "Javier"], ["Maria", "Carmen", "Ana", "Isabel", "Laura"]),
            "Fantasy": (["Eldon", "Kael", "Roric", "Fendrel", "Gareth"], ["Lyra", "Seraphina", "Elara", "Astrid", "Rowan"])
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generador de Nombres de Personaje')
        self.setGeometry(300, 300, 400, 500)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.origin_combo = QComboBox()
        self.origin_combo.addItems(self.names.keys())

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Masculino", "Femenino"])

        self.generate_btn = QPushButton("Generar")
        self.generate_btn.clicked.connect(self.generate_names)

        form_layout.addWidget(QLabel("Origen:"))
        form_layout.addWidget(self.origin_combo)
        form_layout.addWidget(QLabel("Género:"))
        form_layout.addWidget(self.gender_combo)
        form_layout.addWidget(self.generate_btn)

        self.result_list = QListWidget()

        layout.addLayout(form_layout)
        layout.addWidget(self.result_list)
        self.setLayout(layout)

    def generate_names(self):
        origin = self.origin_combo.currentText()
        gender_idx = 0 if self.gender_combo.currentText() == "Masculino" else 1

        name_pool = self.names[origin][gender_idx]

        self.result_list.clear()
        # Generate 10 random names
        for _ in range(10):
            self.result_list.addItem(random.choice(name_pool))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = NameGeneratorGUI()
    ventana.show()
    sys.exit(app.exec_())
