#!/usr//bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QProgressBar
)
from PyQt5.QtCore import QTimer
import pygame

class GamepadTesterGUI(QWidget):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gamepad_state)
        self.timer.start(50) # Update every 50ms
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Tester de Gamepad')
        self.setGeometry(300, 300, 400, 500)
        self.layout = QVBoxLayout()

        if not self.joystick:
            self.layout.addWidget(QLabel("No se encontró ningún gamepad."))
        else:
            self.name_label = QLabel(f"Gamepad: {self.joystick.get_name()}")
            self.layout.addWidget(self.name_label)

            self.axis_labels = []
            self.axis_bars = []
            for i in range(self.joystick.get_numaxes()):
                label = QLabel(f"Eje {i}: 0.0")
                bar = QProgressBar()
                bar.setRange(-100, 100)
                self.layout.addWidget(label)
                self.layout.addWidget(bar)
                self.axis_labels.append(label)
                self.axis_bars.append(bar)

            self.button_labels = []
            for i in range(self.joystick.get_numbuttons()):
                label = QLabel(f"Botón {i}: No presionado")
                self.layout.addWidget(label)
                self.button_labels.append(label)

        self.setLayout(self.layout)

    def update_gamepad_state(self):
        if not self.joystick:
            return

        pygame.event.pump() # Important to get latest state

        for i in range(self.joystick.get_numaxes()):
            axis_val = self.joystick.get_axis(i)
            self.axis_labels[i].setText(f"Eje {i}: {axis_val:.2f}")
            self.axis_bars[i].setValue(int(axis_val * 100))

        for i in range(self.joystick.get_numbuttons()):
            state = "Presionado" if self.joystick.get_button(i) else "No presionado"
            self.button_labels[i].setText(f"Botón {i}: {state}")

    def closeEvent(self, event):
        pygame.quit()
        event.accept()

if __name__ == '__main__':
    # Requires python3-pygame
    app = QApplication(sys.argv)
    ventana = GamepadTesterGUI()
    ventana.show()
    sys.exit(app.exec_())
