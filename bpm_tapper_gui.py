#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel
)
from PyQt5.QtCore import Qt

class BpmTapperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.taps = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculadora de BPM por Toque')
        self.setGeometry(300, 300, 300, 200)
        layout = QVBoxLayout()

        self.bpm_label = QLabel("Toca el botón para empezar")
        self.bpm_label.setAlignment(Qt.AlignCenter)
        font = self.bpm_label.font(); font.setPointSize(24); self.bpm_label.setFont(font)

        self.tap_button = QPushButton("Toca aquí")
        self.tap_button.setMinimumHeight(100)
        self.tap_button.clicked.connect(self.record_tap)

        layout.addWidget(self.bpm_label)
        layout.addWidget(self.tap_button)
        self.setLayout(layout)

    def record_tap(self):
        current_time = time.time()
        self.taps.append(current_time)

        # Keep only the last 10 taps to average
        if len(self.taps) > 10:
            self.taps.pop(0)

        if len(self.taps) > 1:
            # Calculate average interval
            intervals = [self.taps[i] - self.taps[i-1] for i in range(1, len(self.taps))]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval > 0:
                bpm = 60.0 / avg_interval
                self.bpm_label.setText(f"{bpm:.1f} BPM")
        else:
            self.bpm_label.setText("Sigue tocando...")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = BpmTapperGUI()
    ventana.show()
    sys.exit(app.exec_())
