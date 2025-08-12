#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gestor_servicios_gui.py - GUI para gestionar servicios de systemd (Nemás OS)
#

import sys
import os
import subprocess
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTextEdit
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

class SystemctlWorker(QThread):
    """
    Hilo de trabajo para ejecutar comandos de systemctl.
    """
    lista_servicios_obtenida = pyqtSignal(list)
    estado_obtenido = pyqtSignal(str)
    accion_finalizada = pyqtSignal(str, bool)

    def __init__(self, modo, servicio=None, accion=None):
        super().__init__()
        self.modo = modo
        self.servicio = servicio
        self.accion = accion

    def run(self):
        try:
            if self.modo == 'list':
                cmd = "systemctl list-units --type=service --all --no-pager"
                output = subprocess.check_output(cmd, shell=True, text=True)
                servicios = self.parse_list_units(output)
                self.lista_servicios_obtenida.emit(servicios)
            elif self.modo == 'status':
                cmd = f"systemctl status {self.servicio}"
                output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
                self.estado_obtenido.emit(output)
            elif self.modo == 'action':
                cmd = f"systemctl {self.accion} {self.servicio}"
                subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.accion_finalizada.emit(f"Acción '{self.accion}' completada para {self.servicio}.", True)
        except subprocess.CalledProcessError as e:
            # Para 'status', un código de salida no cero es normal (p.ej. servicio inactivo)
            if self.modo == 'status':
                self.estado_obtenido.emit(e.output)
            else:
                error_msg = e.stderr or e.output or "Error desconocido."
                self.accion_finalizada.emit(f"Error al ejecutar '{self.accion}' en {self.servicio}:\n{error_msg}", False)
        except Exception as e:
             self.accion_finalizada.emit(f"Error inesperado: {e}", False)

    def parse_list_units(self, output):
        lines = output.strip().split('\n')
        servicios = []
        # Expresión regular para capturar los campos, incluso si la descripción está vacía
        pattern = re.compile(r"^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)")
        for line in lines[1:-5]: # Omitir cabecera y pie de página
            match = pattern.match(line.lstrip('● '))
            if match:
                servicios.append(list(match.groups()))
        return servicios

class GestorServiciosGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()
        self.verificar_privilegios_y_cargar()

    def initUI(self):
        self.setWindowTitle('Gestor de Servicios de Nemás OS')
        self.setGeometry(150, 150, 900, 700)
        layout = QVBoxLayout()

        # --- Filtro y Refresco ---
        top_layout = QHBoxLayout()
        self.filtro_linea = QLineEdit(); self.filtro_linea.setPlaceholderText("Filtrar servicios...")
        self.filtro_linea.textChanged.connect(self.filtrar_tabla)
        btn_refrescar = QPushButton("Refrescar Lista"); btn_refrescar.clicked.connect(self.cargar_servicios)
        top_layout.addWidget(QLabel("Filtro:"))
        top_layout.addWidget(self.filtro_linea)
        top_layout.addWidget(btn_refrescar)
        layout.addLayout(top_layout)

        # --- Tabla de Servicios ---
        self.tabla_servicios = QTableWidget(); self.tabla_servicios.setColumnCount(5)
        self.tabla_servicios.setHorizontalHeaderLabels(["Servicio", "Carga", "Activo", "Sub", "Descripción"])
        self.tabla_servicios.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.tabla_servicios.setSelectionBehavior(QTableWidget.SelectRows); self.tabla_servicios.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_servicios.itemSelectionChanged.connect(self.actualizar_vista_estado)
        layout.addWidget(self.tabla_servicios)

        # --- Acciones y Estado ---
        bottom_layout = QHBoxLayout()
        # Acciones
        actions_layout = QVBoxLayout()
        self.btn_iniciar = QPushButton("Iniciar"); self.btn_iniciar.clicked.connect(lambda: self.ejecutar_accion('start'))
        self.btn_detener = QPushButton("Detener"); self.btn_detener.clicked.connect(lambda: self.ejecutar_accion('stop'))
        self.btn_reiniciar = QPushButton("Reiniciar"); self.btn_reiniciar.clicked.connect(lambda: self.ejecutar_accion('restart'))
        self.set_botones_accion_enabled(False)
        actions_layout.addWidget(self.btn_iniciar); actions_layout.addWidget(self.btn_detener); actions_layout.addWidget(self.btn_reiniciar)
        bottom_layout.addLayout(actions_layout)
        # Vista de estado
        self.vista_estado = QTextEdit(); self.vista_estado.setReadOnly(True)
        self.vista_estado.setFont(QFont("Monospace"))
        bottom_layout.addWidget(self.vista_estado, 1)
        layout.addLayout(bottom_layout)

        # --- Etiqueta de Estado General ---
        self.label_estado = QLabel("Listo."); layout.addWidget(self.label_estado)
        self.setLayout(layout)

    def verificar_privilegios_y_cargar(self):
        if os.geteuid() != 0:
            QMessageBox.critical(self, "Error de Privilegios", "Se requieren privilegios de administrador. Por favor, ejecuta con 'sudo'.")
            self.label_estado.setText("Error: Se requieren privilegios de administrador.")
            self.filtro_linea.setEnabled(False)
        else:
            self.cargar_servicios()

    def cargar_servicios(self):
        self.label_estado.setText("Cargando lista de servicios..."); self.tabla_servicios.setRowCount(0)
        self.worker = SystemctlWorker('list')
        self.worker.lista_servicios_obtenida.connect(self.poblar_tabla)
        self.worker.start()

    def poblar_tabla(self, servicios):
        self.tabla_servicios.setRowCount(len(servicios))
        for i, s in enumerate(servicios):
            for j, val in enumerate(s):
                self.tabla_servicios.setItem(i, j, QTableWidgetItem(val))
        self.label_estado.setText(f"Lista de servicios cargada. {len(servicios)} unidades encontradas.")

    def filtrar_tabla(self, texto):
        for i in range(self.tabla_servicios.rowCount()):
            mostrar_fila = texto.lower() in self.tabla_servicios.item(i, 0).text().lower()
            self.tabla_servicios.setRowHidden(i, not mostrar_fila)

    def set_botones_accion_enabled(self, enabled):
        self.btn_iniciar.setEnabled(enabled); self.btn_detener.setEnabled(enabled); self.btn_reiniciar.setEnabled(enabled)

    def actualizar_vista_estado(self):
        items = self.tabla_servicios.selectedItems()
        if not items:
            self.set_botones_accion_enabled(False)
            return

        self.set_botones_accion_enabled(True)
        servicio = items[0].text()
        self.vista_estado.setText(f"Cargando estado para {servicio}...")
        self.worker = SystemctlWorker('status', servicio=servicio)
        self.worker.estado_obtenido.connect(self.vista_estado.setText)
        self.worker.start()

    def ejecutar_accion(self, accion):
        items = self.tabla_servicios.selectedItems()
        if not items: return
        servicio = items[0].text()
        self.label_estado.setText(f"Ejecutando '{accion}' en {servicio}...")
        self.worker = SystemctlWorker('action', servicio=servicio, accion=accion)
        self.worker.accion_finalizada.connect(self.accion_finalizada)
        self.worker.start()

    def accion_finalizada(self, mensaje, exito):
        self.label_estado.setText(mensaje)
        if not exito: QMessageBox.critical(self, "Error de Acción", mensaje)
        # Refrescar la lista y el estado para ver los cambios
        self.cargar_servicios()
        self.actualizar_vista_estado()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = GestorServiciosGUI(); ventana.show()
    sys.exit(app.exec_())
