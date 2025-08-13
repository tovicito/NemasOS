#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from PyQt5.QtCore import QTimer, Qt, QTime

class StopwatchGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.time = QTime(0, 0, 0)
        self.is_running = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Cronómetro')
        self.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout()

        self.time_label = QLabel(self.time.toString("hh:mm:ss.zzz"))
        font = self.time_label.font()
        font.setPointSize(40)
        self.time_label.setFont(font)
        self.time_label.setAlignment(Qt.AlignCenter)

        btn_layout = QHBoxLayout()
        self.start_stop_btn = QPushButton("Iniciar")
        self.reset_btn = QPushButton("Reiniciar")

        self.start_stop_btn.clicked.connect(self.toggle_timer)
        self.reset_btn.clicked.connect(self.reset_timer)

        btn_layout.addWidget(self.start_stop_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addWidget(self.time_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_stop_btn.setText("Iniciar")
        else:
            self.timer.start(1) # Update every millisecond
            self.start_stop_btn.setText("Parar")
        self.is_running = not self.is_running

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        self.time.setHMS(0,0,0,0)
        self.time_label.setText(self.time.toString("hh:mm:ss.zzz"))
        self.start_stop_btn.setText("Iniciar")

    def update_time(self):
        self.time = self.time.addMSecs(1)
        self.time_label.setText(self.time.toString("hh:mm:ss.zzz"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = StopwatchGUI()
    ventana.show()
    sys.exit(app.exec_())
