#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# gestor_usuarios_gui.py - GUI para gestionar usuarios del sistema (Nemás OS)
#

import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal

class UserWorker(QThread):
    """ Hilo para ejecutar comandos de gestión de usuarios. """
    resultado = pyqtSignal(str, bool)

    def __init__(self, modo, **kwargs):
        super().__init__()
        self.modo = modo
        self.kwargs = kwargs

    def run(self):
        try:
            if self.modo == 'add':
                self.add_user()
            elif self.modo == 'del':
                self.del_user()
        except Exception as e:
            self.resultado.emit(str(e), False)

    def add_user(self):
        username = self.kwargs['username']
        password = self.kwargs['password']
        create_home = self.kwargs['create_home']

        cmd = ['useradd']
        if create_home:
            cmd.append('-m')
        cmd.append(username)

        subprocess.check_call(cmd)

        # Cambiar contraseña
        proc = subprocess.Popen(['passwd', username], stdin=subprocess.PIPE)
        proc.communicate(input=f"{password}\n{password}\n".encode())
        if proc.returncode != 0:
            raise Exception("No se pudo establecer la contraseña.")

        self.resultado.emit(f"Usuario '{username}' creado con éxito.", True)

    def del_user(self):
        username = self.kwargs['username']
        remove_home = self.kwargs['remove_home']

        cmd = ['userdel']
        if remove_home:
            cmd.append('-r')
        cmd.append(username)

        subprocess.check_call(cmd)
        self.resultado.emit(f"Usuario '{username}' eliminado con éxito.", True)

class AddUserDialog(QDialog):
    """ Diálogo para añadir un nuevo usuario. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Nuevo Usuario")
        layout = QFormLayout(self)

        self.username = QLineEdit(self)
        self.password = QLineEdit(self); self.password.setEchoMode(QLineEdit.Password)
        self.create_home = QCheckBox(self); self.create_home.setChecked(True)

        layout.addRow("Nombre de usuario:", self.username)
        layout.addRow("Contraseña:", self.password)
        layout.addRow("Crear directorio home:", self.create_home)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_data(self):
        return {
            'username': self.username.text(),
            'password': self.password.text(),
            'create_home': self.create_home.isChecked()
        }

class GestorUsuariosGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()
        self.verificar_privilegios_y_cargar()

    def initUI(self):
        self.setWindowTitle('Gestor de Usuarios de Nemás OS')
        self.setGeometry(200, 200, 700, 500)
        layout = QVBoxLayout(self)

        # --- Botones de acción ---
        action_layout = QHBoxLayout()
        btn_add = QPushButton("Añadir Usuario..."); btn_add.clicked.connect(self.abrir_dialogo_anadir)
        self.btn_del = QPushButton("Eliminar Usuario Seleccionado"); self.btn_del.clicked.connect(self.eliminar_usuario)
        self.btn_del.setEnabled(False)
        btn_refresh = QPushButton("Refrescar"); btn_refresh.clicked.connect(self.cargar_usuarios)
        action_layout.addWidget(btn_add); action_layout.addWidget(self.btn_del); action_layout.addStretch(1); action_layout.addWidget(btn_refresh)
        layout.addLayout(action_layout)

        # --- Tabla de usuarios ---
        self.tabla_usuarios = QTableWidget(); self.tabla_usuarios.setColumnCount(5)
        self.tabla_usuarios.setHorizontalHeaderLabels(["Usuario", "UID", "GID", "Directorio Home", "Shell"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectRows); self.tabla_usuarios.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_usuarios.itemSelectionChanged.connect(lambda: self.btn_del.setEnabled(True))
        layout.addWidget(self.tabla_usuarios)

    def verificar_privilegios_y_cargar(self):
        if os.geteuid() != 0:
            QMessageBox.critical(self, "Error de Privilegios", "Se requieren privilegios de administrador. Por favor, ejecuta con 'sudo'.")
            self.close()
        else:
            self.cargar_usuarios()

    def cargar_usuarios(self):
        self.tabla_usuarios.setRowCount(0)
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) == 7 and int(parts[2]) >= 1000:
                        row = self.tabla_usuarios.rowCount()
                        self.tabla_usuarios.insertRow(row)
                        for i, col in enumerate([0, 2, 3, 5, 6]):
                            self.tabla_usuarios.setItem(row, i, QTableWidgetItem(parts[col]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer la lista de usuarios: {e}")

    def abrir_dialogo_anadir(self):
        dialog = AddUserDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if not data['username'] or not data['password']:
                QMessageBox.warning(self, "Datos incompletos", "El nombre de usuario y la contraseña no pueden estar vacíos.")
                return
            self.worker = UserWorker('add', **data)
            self.worker.resultado.connect(self.accion_finalizada)
            self.worker.start()

    def eliminar_usuario(self):
        selected_items = self.tabla_usuarios.selectedItems()
        if not selected_items: return

        username = selected_items[0].text()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar Eliminación")
        msg_box.setText(f"¿Estás seguro de que quieres eliminar al usuario '{username}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        check_remove_home = QCheckBox("Eliminar directorio home", msg_box)
        msg_box.setCheckBox(check_remove_home)

        if msg_box.exec_() == QMessageBox.Yes:
            self.worker = UserWorker('del', username=username, remove_home=check_remove_home.isChecked())
            self.worker.resultado.connect(self.accion_finalizada)
            self.worker.start()

    def accion_finalizada(self, mensaje, exito):
        if exito: QMessageBox.information(self, "Éxito", mensaje)
        else: QMessageBox.critical(self, "Error", mensaje)
        self.cargar_usuarios()

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setStyle('Fusion')
    ventana = GestorUsuariosGUI(); ventana.show()
    sys.exit(app.exec_())
