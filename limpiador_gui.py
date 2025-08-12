#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# limpiador_gui.py - Interfaz gráfica para limpiar el sistema en Nemás OS.
#

import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QCheckBox, QTextEdit, QLabel, QMessageBox, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class WorkerThread(QThread):
    """
    Este hilo ejecuta los comandos de limpieza en segundo plano para no congelar la GUI.
    """
    linea_leida = pyqtSignal(str)
    proceso_terminado = pyqtSignal(str)

    def __init__(self, comandos):
        super().__init__()
        self.comandos = comandos
        self.proceso = None

    def run(self):
        comando_completo = " && ".join(self.comandos)
        self.linea_leida.emit(f"Ejecutando: {comando_completo}\n")
        try:
            self.proceso = subprocess.Popen(
                comando_completo,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for linea in iter(self.proceso.stdout.readline, ''):
                self.linea_leida.emit(linea)

            self.proceso.stdout.close()
            retorno = self.proceso.wait()
            if retorno == 0:
                self.proceso_terminado.emit("¡Limpieza completada con éxito!")
            else:
                self.proceso_terminado.emit(f"Proceso terminado con errores (código {retorno}).")
        except Exception as e:
            self.proceso_terminado.emit(f"Error crítico al ejecutar el comando: {e}")

    def stop(self):
        if self.proceso and self.proceso.poll() is None:
            self.proceso.terminate()
            self.proceso.wait()

class LimpiadorGUI(QWidget):
    """
    Clase principal de la aplicación Limpiador del Sistema.
    """
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()
        self.verificar_privilegios()

    def initUI(self):
        self.setWindowTitle('Limpiador del Sistema de Nemás OS')
        self.setGeometry(300, 300, 700, 500)

        layout_principal = QVBoxLayout()

        # Título
        label_titulo = QLabel('Limpiador del Sistema')
        font_titulo = QFont(); font_titulo.setPointSize(18); font_titulo.setBold(True)
        label_titulo.setFont(font_titulo)
        label_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(label_titulo)

        # Aviso de privilegios
        self.label_aviso = QLabel()
        self.label_aviso.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(self.label_aviso)

        # Opciones de limpieza
        frame_opciones = QFrame()
        frame_opciones.setFrameShape(QFrame.StyledPanel)
        layout_opciones = QVBoxLayout(frame_opciones)

        label_opciones = QLabel("Selecciona las tareas de limpieza a realizar:")
        layout_opciones.addWidget(label_opciones)

        self.check_autoremove = QCheckBox("Eliminar paquetes innecesarios (apt autoremove)")
        self.check_autoremove.setChecked(True)
        self.check_clean = QCheckBox("Limpiar la caché de paquetes descargados (apt clean)")
        self.check_clean.setChecked(True)
        layout_opciones.addWidget(self.check_autoremove)
        layout_opciones.addWidget(self.check_clean)
        layout_principal.addWidget(frame_opciones)

        # Botón de acción
        self.btn_limpiar = QPushButton("Iniciar Limpieza")
        self.btn_limpiar.setStyleSheet("padding: 10px; font-size: 16px; background-color: #4CAF50; color: white;")
        self.btn_limpiar.clicked.connect(self.iniciar_limpieza)
        layout_principal.addWidget(self.btn_limpiar)

        # Área de salida de texto
        label_salida = QLabel("Salida del comando:")
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0; font-family: 'Monospace';")
        layout_principal.addWidget(label_salida)
        layout_principal.addWidget(self.output_area, 1)

        # Barra de estado
        self.label_estado = QLabel("Estado: En espera")
        layout_principal.addWidget(self.label_estado)

        self.setLayout(layout_principal)

    def verificar_privilegios(self):
        if os.geteuid() != 0:
            self.label_aviso.setText("<font color='red'><b>Se requieren privilegios de administrador.</b> Ejecuta con 'sudo'.</font>")
            self.btn_limpiar.setEnabled(False)
            self.btn_limpiar.setToolTip("Deshabilitado. Por favor, ejecuta la aplicación con 'sudo'.")
        else:
            self.label_aviso.setText("<font color='green'>Privilegios de administrador detectados.</font>")

    def iniciar_limpieza(self):
        comandos = []
        if self.check_autoremove.isChecked():
            comandos.append("apt autoremove -y")
        if self.check_clean.isChecked():
            comandos.append("apt clean")

        if not comandos:
            QMessageBox.warning(self, "Sin selección", "Por favor, selecciona al menos una tarea de limpieza.")
            return

        self.btn_limpiar.setEnabled(False)
        self.btn_limpiar.setText("Limpiando...")
        self.output_area.clear()
        self.label_estado.setText("Estado: Ejecutando tareas...")

        self.worker = WorkerThread(comandos)
        self.worker.linea_leida.connect(self.actualizar_salida)
        self.worker.proceso_terminado.connect(self.limpieza_terminada)
        self.worker.start()

    def actualizar_salida(self, linea):
        self.output_area.append(linea.strip())

    def limpieza_terminada(self, mensaje):
        self.label_estado.setText(f"Estado: {mensaje}")
        self.btn_limpiar.setEnabled(True)
        self.btn_limpiar.setText("Iniciar Limpieza")
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            respuesta = QMessageBox.question(self, 'Confirmar Salida',
                "Un proceso de limpieza está en curso. ¿Estás seguro de que quieres salir? Esto podría dejar el sistema en un estado inestable.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if respuesta == QMessageBox.Yes:
                self.worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = LimpiadorGUI()
    ventana.show()
    sys.exit(app.exec_())
