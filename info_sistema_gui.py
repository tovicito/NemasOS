#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# info_sistema_gui.py - Visor con GUI para la información del sistema (Nemás OS)
#

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QTabWidget, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

class InfoWorker(QThread):
    """
    Hilo de trabajo para ejecutar un comando y devolver su salida.
    """
    resultado_obtenido = pyqtSignal(str, str)  # Emite: id_comando, resultado

    def __init__(self, id_comando, comando_str):
        super().__init__()
        self.id_comando = id_comando
        self.comando_str = comando_str

    def run(self):
        try:
            salida = subprocess.check_output(self.comando_str, shell=True, text=True, stderr=subprocess.STDOUT)
            self.resultado_obtenido.emit(self.id_comando, salida)
        except subprocess.CalledProcessError as e:
            self.resultado_obtenido.emit(self.id_comando, f"Error al ejecutar el comando:\n{e.output}")
        except Exception as e:
            self.resultado_obtenido.emit(self.id_comando, f"Se ha producido un error inesperado:\n{e}")

class InfoSistemaGUI(QWidget):
    """
    Clase principal para el Visor de Información del Sistema.
    """
    COMANDOS = {
        "resumen": "echo '--- Sistema Operativo ---' && lsb_release -drc && echo '\n--- Kernel y Arquitectura ---' && uname -rm",
        "cpu": "lscpu",
        "memoria": "free -h",
        "almacenamiento": "df -h"
    }

    def __init__(self):
        super().__init__()
        self.hilos_trabajo = []
        self.initUI()
        self.cargar_toda_la_info()

    def initUI(self):
        self.setWindowTitle('Visor de Información del Sistema de Nemás OS')
        self.setGeometry(300, 300, 750, 550)

        layout_principal = QVBoxLayout()

        # Título
        label_titulo = QLabel('Información del Sistema')
        font_titulo = QFont(); font_titulo.setPointSize(18); font_titulo.setBold(True)
        label_titulo.setFont(font_titulo)
        label_titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(label_titulo)

        # Pestañas
        self.tabs = QTabWidget()

        # Crear una pestaña para cada comando
        for id_cmd in self.COMANDOS.keys():
            nombre_tab = id_cmd.capitalize()
            pestaña = QWidget()
            self.tabs.addTab(pestaña, nombre_tab)
            self.setup_tab(pestaña, id_cmd)

        layout_principal.addWidget(self.tabs)

        # Botón de refrescar
        btn_refrescar = QPushButton("Refrescar Toda la Información")
        btn_refrescar.clicked.connect(self.cargar_toda_la_info)
        layout_principal.addWidget(btn_refrescar)

        self.setLayout(layout_principal)

    def setup_tab(self, pestaña, id_comando):
        """Configura el layout de una pestaña individual."""
        layout_tab = QVBoxLayout()
        area_texto = QTextEdit()
        area_texto.setReadOnly(True)
        area_texto.setFont(QFont('Monospace', 10))
        area_texto.setLineWrapMode(QTextEdit.NoWrap)

        # Guardar una referencia al área de texto usando su id
        setattr(self, f"text_{id_comando}", area_texto)

        btn_copiar = QPushButton("Copiar al Portapapeles")
        btn_copiar.clicked.connect(lambda: self.copiar_info(id_comando))

        layout_tab.addWidget(area_texto)
        layout_tab.addWidget(btn_copiar)
        pestaña.setLayout(layout_tab)

    def cargar_toda_la_info(self):
        """Lanza hilos para ejecutar todos los comandos y poblar las pestañas."""
        for id_cmd, cmd_str in self.COMANDOS.items():
            area_texto = getattr(self, f"text_{id_cmd}")
            area_texto.setText("Cargando...")
            self.ejecutar_comando(id_cmd, cmd_str)

    def ejecutar_comando(self, id_comando, comando_str):
        hilo = InfoWorker(id_comando, comando_str)
        hilo.resultado_obtenido.connect(self.actualizar_texto)
        # Evitar que los hilos se destruyan prematuramente
        self.hilos_trabajo.append(hilo)
        hilo.start()

    def actualizar_texto(self, id_comando, resultado):
        """Slot para actualizar el área de texto cuando un hilo termina."""
        area_texto = getattr(self, f"text_{id_comando}")
        area_texto.setText(resultado.strip())

    def copiar_info(self, id_comando):
        """Copia el contenido de la pestaña actual al portapapeles."""
        area_texto = getattr(self, f"text_{id_comando}")
        texto_a_copiar = area_texto.toPlainText()
        if texto_a_copiar and texto_a_copiar != "Cargando...":
            QApplication.clipboard().setText(texto_a_copiar)
            QMessageBox.information(self, "Copiado", f"La información de la pestaña '{id_comando.capitalize()}' ha sido copiada.")
        else:
            QMessageBox.warning(self, "Aviso", "No hay información para copiar.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = InfoSistemaGUI()
    ventana.show()
    sys.exit(app.exec_())
