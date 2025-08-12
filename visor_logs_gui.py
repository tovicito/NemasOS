#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# visor_logs_gui.py - GUI para ver logs de journalctl (Nemás OS)
#

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QComboBox, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class LogWorker(QThread):
    """ Hilo para ejecutar journalctl y leer su salida. """
    nueva_linea = pyqtSignal(str)
    finalizado = pyqtSignal(str)

    def __init__(self, comando):
        super().__init__()
        self.comando = comando
        self.proceso = None
        self.activo = True

    def run(self):
        try:
            self.proceso = subprocess.Popen(
                self.comando,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for linea in iter(self.proceso.stdout.readline, ''):
                if not self.activo: break
                self.nueva_linea.emit(linea.strip())

            self.proceso.stdout.close()
            self.proceso.wait()
            if self.activo:
                self.finalizado.emit("Proceso de logs finalizado.")
        except Exception as e:
            self.finalizado.emit(f"Error al ejecutar journalctl: {e}")

    def stop(self):
        self.activo = False
        if self.proceso and self.proceso.poll() is None:
            self.proceso.terminate()

class VisorLogsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Visor de Logs del Sistema (journalctl)')
        self.setGeometry(150, 150, 900, 700)
        layout = QVBoxLayout(self)

        # --- Panel de Filtros ---
        grid = QGridLayout()
        self.combo_num_lineas = QComboBox(); self.combo_num_lineas.addItems(['100', '500', '1000', '5000'])
        self.linea_unidad = QLineEdit(); self.linea_unidad.setPlaceholderText("Ej: nginx.service")
        self.combo_prioridad = QComboBox(); self.combo_prioridad.addItems(["Cualquiera", "0: emerg", "1: alert", "2: crit", "3: err", "4: warning", "5: notice", "6: info", "7: debug"])
        self.check_seguir = QCheckBox("Seguir en tiempo real (-f)")

        grid.addWidget(QLabel("Nº Líneas:"), 0, 0); grid.addWidget(self.combo_num_lineas, 0, 1)
        grid.addWidget(QLabel("Unidad (servicio):"), 0, 2); grid.addWidget(self.linea_unidad, 0, 3)
        grid.addWidget(QLabel("Prioridad:"), 1, 0); grid.addWidget(self.combo_prioridad, 1, 1)
        grid.addWidget(self.check_seguir, 1, 2, 1, 2)
        layout.addLayout(grid)

        # --- Botón de Acción ---
        self.btn_cargar = QPushButton("Cargar / Aplicar Filtros"); self.btn_cargar.clicked.connect(self.cargar_logs)
        layout.addWidget(self.btn_cargar)

        # --- Salida de Logs ---
        self.output_area = QTextEdit(); self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Monospace"))
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc;")
        layout.addWidget(self.output_area, 1)

        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)

    def construir_comando(self):
        cmd = ['journalctl']
        if self.check_seguir.isChecked():
            cmd.append('-f')

        cmd.append(f"-n {self.combo_num_lineas.currentText()}")

        if self.linea_unidad.text():
            cmd.extend(['-u', self.linea_unidad.text()])

        if self.combo_prioridad.currentIndex() > 0:
            # El valor es el índice - 1
            prioridad_val = self.combo_prioridad.currentIndex() - 1
            cmd.extend(['-p', str(prioridad_val)])

        return " ".join(cmd)

    def cargar_logs(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # Esperar a que el hilo termine

        comando = self.construir_comando()
        self.output_area.clear()
        self.label_estado.setText(f"Ejecutando: {comando}")

        self.worker = LogWorker(comando)
        self.worker.nueva_linea.connect(self.agregar_linea)
        self.worker.finalizado.connect(lambda msg: self.label_estado.setText(msg))
        self.worker.start()

    def agregar_linea(self, linea):
        # Colorear la línea según la prioridad (simplificado)
        if 'error' in linea.lower() or 'failed' in linea.lower():
            linea = f"<font color='#FF7B72'>{linea}</font>"
        elif 'warning' in linea.lower():
            linea = f"<font color='#FFB86C'>{linea}</font>"

        self.output_area.append(linea)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = VisorLogsGUI()
    ventana.show()
    sys.exit(app.exec_())
