#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# backup_gui.py - GUI para crear backups con tar (Nemás OS)
#

import sys
import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

class BackupWorker(QThread):
    """ Hilo para ejecutar el comando tar en segundo plano. """
    linea_salida = pyqtSignal(str)
    proceso_finalizado = pyqtSignal(bool, str)

    def __init__(self, origen, destino_archivo):
        super().__init__()
        self.origen = origen
        self.destino_archivo = destino_archivo
        self.activo = True

    def run(self):
        # El comando necesita ejecutarse desde el directorio padre del origen
        # para que las rutas en el tarball sean relativas.
        directorio_padre = os.path.dirname(self.origen)
        nombre_origen = os.path.basename(self.origen)

        comando = ['tar', '-czvf', self.destino_archivo, nombre_origen]

        try:
            self.proceso = subprocess.Popen(
                comando,
                cwd=directorio_padre,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for linea in iter(self.proceso.stdout.readline, ''):
                if not self.activo: break
                self.linea_salida.emit(linea.strip())

            self.proceso.stdout.close()
            retorno = self.proceso.wait()

            if not self.activo:
                self.proceso_finalizado.emit(False, "Backup cancelado por el usuario.")
            elif retorno == 0:
                self.proceso_finalizado.emit(True, f"¡Backup completado con éxito!\nArchivo guardado en: {self.destino_archivo}")
            else:
                self.proceso_finalizado.emit(False, f"El proceso de backup falló con código de error {retorno}.")
        except Exception as e:
            self.proceso_finalizado.emit(False, f"Error crítico durante el backup: {e}")

    def stop(self):
        self.activo = False
        if hasattr(self, 'proceso') and self.proceso.poll() is None:
            self.proceso.terminate()

class BackupGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Utilidad de Backup de Nemás OS')
        self.setGeometry(300, 300, 700, 500)
        layout = QVBoxLayout(self)

        # --- Selección de Directorios y Archivo ---
        grid = QGridLayout()
        self.linea_origen = QLineEdit(); self.linea_origen.setPlaceholderText("Directorio a respaldar")
        btn_origen = QPushButton("Seleccionar..."); btn_origen.clicked.connect(lambda: self.seleccionar_directorio(self.linea_origen))

        self.linea_destino = QLineEdit(); self.linea_destino.setPlaceholderText("Carpeta donde se guardará el backup")
        btn_destino = QPushButton("Seleccionar..."); btn_destino.clicked.connect(lambda: self.seleccionar_directorio(self.linea_destino))

        self.linea_nombre_archivo = QLineEdit()

        grid.addWidget(QLabel("Directorio de Origen:"), 0, 0); grid.addWidget(self.linea_origen, 0, 1); grid.addWidget(btn_origen, 0, 2)
        grid.addWidget(QLabel("Directorio de Destino:"), 1, 0); grid.addWidget(self.linea_destino, 1, 1); grid.addWidget(btn_destino, 1, 2)
        grid.addWidget(QLabel("Nombre del Archivo:"), 2, 0); grid.addWidget(self.linea_nombre_archivo, 2, 1, 1, 2)
        layout.addLayout(grid)
        self.linea_destino.textChanged.connect(self.sugerir_nombre_archivo)

        # --- Botón de Acción ---
        self.btn_backup = QPushButton("Iniciar Backup")
        self.btn_backup.setStyleSheet("padding: 10px; font-size: 16px;")
        self.btn_backup.clicked.connect(self.gestionar_backup)
        layout.addWidget(self.btn_backup)

        # --- Salida de Comando ---
        self.output_area = QTextEdit(); self.output_area.setReadOnly(True)
        self.output_area.setFontFamily("Monospace")
        layout.addWidget(self.output_area, 1)

        # --- Estado ---
        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)

    def seleccionar_directorio(self, linea_edit):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio", os.path.expanduser("~"))
        if directorio: linea_edit.setText(directorio)

    def sugerir_nombre_archivo(self):
        fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.linea_nombre_archivo.setText(f"backup_{fecha_hora}.tar.gz")

    def gestionar_backup(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        else:
            self.iniciar_backup()

    def iniciar_backup(self):
        origen = self.linea_origen.text(); destino_dir = self.linea_destino.text(); nombre_archivo = self.linea_nombre_archivo.text()
        if not all([origen, destino_dir, nombre_archivo]):
            QMessageBox.warning(self, "Datos Incompletos", "Por favor, completa todos los campos."); return
        if not os.path.isdir(origen):
            QMessageBox.critical(self, "Error", "El directorio de origen no existe."); return
        if not os.path.isdir(destino_dir):
            QMessageBox.critical(self, "Error", "El directorio de destino no existe."); return

        destino_archivo = os.path.join(destino_dir, nombre_archivo)
        if os.path.exists(destino_archivo):
            resp = QMessageBox.question(self, "Archivo Existente", f"El archivo '{nombre_archivo}' ya existe. ¿Deseas sobreescribirlo?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if resp == QMessageBox.No: return

        self.output_area.clear()
        self.label_estado.setText("Iniciando backup...")
        self.btn_backup.setText("Cancelar Backup")

        self.worker = BackupWorker(origen, destino_archivo)
        self.worker.linea_salida.connect(self.output_area.append)
        self.worker.proceso_finalizado.connect(self.backup_finalizado)
        self.worker.start()

    def backup_finalizado(self, exito, mensaje):
        self.label_estado.setText(mensaje)
        if exito: QMessageBox.information(self, "Éxito", mensaje)
        else: QMessageBox.critical(self, "Fallo", mensaje)
        self.btn_backup.setText("Iniciar Backup")
        self.worker = None

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = BackupGUI(); ventana.show()
    sys.exit(app.exec_())
