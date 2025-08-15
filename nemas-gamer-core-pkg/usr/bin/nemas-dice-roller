#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt

class DiceRollerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Lanzador de Dados')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        self.num_dice_spin = QSpinBox()
        self.num_dice_spin.setRange(1, 100)

        self.dice_type_combo = QComboBox()
        self.dice_type_combo.addItems(["D4", "D6", "D8", "D10", "D12", "D20"])

        self.roll_btn = QPushButton("Lanzar")
        self.roll_btn.clicked.connect(self.roll_dice)

        form_layout.addWidget(self.num_dice_spin)
        form_layout.addWidget(self.dice_type_combo)
        form_layout.addWidget(self.roll_btn)

        self.result_label = QLabel("Resultado: ")
        self.result_label.setAlignment(Qt.AlignCenter)
        font = self.result_label.font(); font.setPointSize(18); self.result_label.setFont(font)

        layout.addLayout(form_layout)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def roll_dice(self):
        num_dice = self.num_dice_spin.value()
        dice_type_str = self.dice_type_combo.currentText()
        dice_sides = int(dice_type_str.replace('D', ''))

        total = 0
        for _ in range(num_dice):
            total += random.randint(1, dice_sides)

        self.result_label.setText(f"Resultado: {total}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = DiceRollerGUI()
    ventana.show()
    sys.exit(app.exec_())
