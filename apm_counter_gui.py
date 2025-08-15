#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton
)
from PyQt5.QtCore import QTimer, Qt, QEvent

class ApmCounterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.actions = 0
        self.seconds = 0
        self.is_running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Contador de APM (Acciones Por Minuto)')
        self.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout()

        self.apm_label = QLabel("APM: 0")
        font = self.apm_label.font(); font.setPointSize(32); self.apm_label.setFont(font)
        self.apm_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel("Haz clic o pulsa teclas en esta ventana para contar.")
        self.info_label.setAlignment(Qt.AlignCenter)

        self.start_stop_btn = QPushButton("Iniciar")
        self.start_stop_btn.clicked.connect(self.toggle_timer)

        layout.addWidget(self.apm_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.start_stop_btn)
        self.setLayout(layout)

        # Install event filter to capture key/mouse events
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if self.is_running and source is self:
            if event.type() in [QEvent.MouseButtonPress, QEvent.KeyPress]:
                self.actions += 1
        return super().eventFilter(source, event)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_stop_btn.setText("Iniciar")
        else:
            self.actions = 0
            self.seconds = 0
            self.timer.start(1000)
            self.start_stop_btn.setText("Parar")
        self.is_running = not self.is_running

    def update_time(self):
        self.seconds += 1
        if self.seconds > 0:
            apm = (self.actions / self.seconds) * 60
            self.apm_label.setText(f"APM: {apm:.0f}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = ApmCounterGUI()
    ventana.show()
    sys.exit(app.exec_())
