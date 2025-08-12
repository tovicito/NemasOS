#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# test_velocidad_gui.py - GUI para medir la velocidad de internet (Nemás OS)
#

import sys
import speedtest
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class SpeedtestWorker(QThread):
    """ Hilo para ejecutar el test de velocidad en segundo plano. """
    test_finalizado = pyqtSignal(dict)
    actualizacion_estado = pyqtSignal(str)

    def run(self):
        resultado = {'error': None}
        try:
            self.actualizacion_estado.emit("Buscando el mejor servidor...")
            st = speedtest.Speedtest()
            st.get_best_server()

            self.actualizacion_estado.emit(f"Host: {st.results.server['host']} ({st.results.server['country']})")

            self.actualizacion_estado.emit("Realizando test de descarga...")
            st.download()

            self.actualizacion_estado.emit("Realizando test de subida...")
            st.upload()

            res_dict = st.results.dict()
            resultado['ping'] = res_dict['ping']
            resultado['descarga'] = res_dict['download'] / 1_000_000  # a Mbps
            resultado['subida'] = res_dict['upload'] / 1_000_000  # a Mbps
            resultado['servidor'] = f"{res_dict['server']['name']} ({res_dict['server']['country']})"

        except Exception as e:
            resultado['error'] = str(e)

        self.test_finalizado.emit(resultado)

class TestVelocidadGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Test de Velocidad de Nemás OS')
        self.setGeometry(300, 300, 450, 400)
        layout = QVBoxLayout(self)

        # --- Título ---
        titulo = QLabel("Test de Velocidad de Internet")
        font_titulo = QFont(); font_titulo.setPointSize(20); font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # --- Botón de Inicio ---
        self.btn_iniciar = QPushButton("Iniciar Test")
        self.btn_iniciar.setStyleSheet("padding: 15px; font-size: 18px;")
        self.btn_iniciar.clicked.connect(self.iniciar_test)
        layout.addWidget(self.btn_iniciar)

        # --- Resultados ---
        grid_resultados = QGridLayout()
        font_label = QFont(); font_label.setPointSize(14)
        font_valor = QFont(); font_valor.setPointSize(16); font_valor.setBold(True)

        self.label_ping = QLabel("Ping (ms):"); self.label_ping.setFont(font_label)
        self.valor_ping = QLabel("-"); self.valor_ping.setFont(font_valor)

        self.label_descarga = QLabel("Descarga (Mbps):"); self.label_descarga.setFont(font_label)
        self.valor_descarga = QLabel("-"); self.valor_descarga.setFont(font_valor)

        self.label_subida = QLabel("Subida (Mbps):"); self.label_subida.setFont(font_label)
        self.valor_subida = QLabel("-"); self.valor_subida.setFont(font_valor)

        grid_resultados.addWidget(self.label_ping, 0, 0); grid_resultados.addWidget(self.valor_ping, 0, 1)
        grid_resultados.addWidget(self.label_descarga, 1, 0); grid_resultados.addWidget(self.valor_descarga, 1, 1)
        grid_resultados.addWidget(self.label_subida, 2, 0); grid_resultados.addWidget(self.valor_subida, 2, 1)
        layout.addLayout(grid_resultados)

        # --- Estado ---
        self.label_estado = QLabel("Listo para iniciar el test.")
        self.label_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_estado)
        layout.addStretch(1)

    def iniciar_test(self):
        self.btn_iniciar.setEnabled(False)
        self.btn_iniciar.setText("Realizando test...")
        self.reset_valores()

        self.worker = SpeedtestWorker()
        self.worker.actualizacion_estado.connect(self.actualizar_estado)
        self.worker.test_finalizado.connect(self.mostrar_resultados)
        self.worker.start()

    def reset_valores(self):
        self.valor_ping.setText("-")
        self.valor_descarga.setText("-")
        self.valor_subida.setText("-")
        self.label_estado.setText("Iniciando...")

    def actualizar_estado(self, mensaje):
        self.label_estado.setText(mensaje)

    def mostrar_resultados(self, resultado):
        self.btn_iniciar.setEnabled(True)
        self.btn_iniciar.setText("Iniciar Test")

        if resultado['error']:
            QMessageBox.critical(self, "Error", f"No se pudo completar el test de velocidad:\n{resultado['error']}")
            self.label_estado.setText("Error al realizar el test.")
            return

        self.valor_ping.setText(f"{resultado['ping']:.2f}")
        self.valor_descarga.setText(f"{resultado['descarga']:.2f}")
        self.valor_subida.setText(f"{resultado['subida']:.2f}")
        self.label_estado.setText(f"Test completado. Servidor: {resultado['servidor']}")

    def closeEvent(self, event):
        # Asegurarse de que el hilo no quede corriendo si se cierra la ventana
        if self.worker and self.worker.isRunning():
            self.worker.terminate() # No es la forma más limpia, pero para este caso es aceptable
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = TestVelocidadGUI()
    ventana.show()
    sys.exit(app.exec_())
