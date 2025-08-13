#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# temporizador_gui.py - Un simple temporizador/cuenta atrás con GUI (Nemás OS)
#

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, QTime

class TemporizadorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.tiempo_restante_s = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_timer)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Temporizador de Nemás OS')
        self.setGeometry(400, 400, 400, 300)
        layout = QVBoxLayout(self)

        # --- Display de Tiempo ---
        self.label_display = QLabel("00:00:00")
        font = self.label_display.font(); font.setPointSize(48); font.setBold(True)
        self.label_display.setFont(font)
        self.label_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_display)

        # --- Controles de Tiempo ---
        controles_layout = QHBoxLayout()
        self.spin_h = QSpinBox(); self.spin_h.setRange(0, 23); self.spin_h.setSuffix(" h")
        self.spin_m = QSpinBox(); self.spin_m.setRange(0, 59); self.spin_m.setSuffix(" m")
        self.spin_s = QSpinBox(); self.spin_s.setRange(0, 59); self.spin_s.setSuffix(" s")
        controles_layout.addWidget(QLabel("Establecer:"))
        controles_layout.addWidget(self.spin_h); controles_layout.addWidget(self.spin_m); controles_layout.addWidget(self.spin_s)
        layout.addLayout(controles_layout)

        # --- Mensaje de Notificación ---
        self.linea_mensaje = QLineEdit()
        self.linea_mensaje.setPlaceholderText("Mensaje de notificación (opcional)")
        layout.addWidget(self.linea_mensaje)

        # --- Botones de Acción ---
        botones_layout = QHBoxLayout()
        self.btn_iniciar = QPushButton("Iniciar"); self.btn_iniciar.clicked.connect(self.iniciar_temporizador)
        self.btn_pausar = QPushButton("Pausar"); self.btn_pausar.clicked.connect(self.pausar_reanudar_temporizador)
        self.btn_reiniciar = QPushButton("Reiniciar"); self.btn_reiniciar.clicked.connect(self.reiniciar_temporizador)
        self.btn_pausar.setEnabled(False)
        botones_layout.addWidget(self.btn_iniciar); botones_layout.addWidget(self.btn_pausar); botones_layout.addWidget(self.btn_reiniciar)
        layout.addLayout(botones_layout)

    def set_controles_enabled(self, enabled):
        """Habilita o deshabilita los spin boxes y el campo de mensaje."""
        self.spin_h.setEnabled(enabled)
        self.spin_m.setEnabled(enabled)
        self.spin_s.setEnabled(enabled)
        self.linea_mensaje.setEnabled(enabled)

    def iniciar_temporizador(self):
        h = self.spin_h.value(); m = self.spin_m.value(); s = self.spin_s.value()
        self.tiempo_restante_s = (h * 3600) + (m * 60) + s

        if self.tiempo_restante_s > 0:
            self.timer.start(1000) # Disparar cada 1000 ms (1 segundo)
            self.btn_iniciar.setEnabled(False)
            self.btn_pausar.setEnabled(True)
            self.btn_pausar.setText("Pausar")
            self.set_controles_enabled(False)

    def pausar_reanudar_temporizador(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_pausar.setText("Reanudar")
        else:
            self.timer.start(1000)
            self.btn_pausar.setText("Pausar")

    def reiniciar_temporizador(self):
        self.timer.stop()
        self.tiempo_restante_s = 0
        self.actualizar_display()
        self.set_controles_enabled(True)
        self.btn_iniciar.setEnabled(True)
        self.btn_pausar.setEnabled(False)
        self.btn_pausar.setText("Pausar")

    def actualizar_timer(self):
        if self.tiempo_restante_s > 0:
            self.tiempo_restante_s -= 1
            self.actualizar_display()
        else:
            self.timer.stop()
            self.mostrar_notificacion()
            self.reiniciar_temporizador()

    def actualizar_display(self):
        tiempo = QTime(0, 0, 0).addSecs(self.tiempo_restante_s)
        self.label_display.setText(tiempo.toString("hh:mm:ss"))

    def mostrar_notificacion(self):
        mensaje = self.linea_mensaje.text()
        if not mensaje:
            mensaje = "¡El tiempo ha terminado!"
        QMessageBox.information(self, "Temporizador Finalizado", mensaje)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = TemporizadorGUI()
    ventana.show()
    sys.exit(app.exec_())
