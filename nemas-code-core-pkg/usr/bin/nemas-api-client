#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QComboBox, QPlainTextEdit
)

class ApiClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Cliente API Simple')
        self.setGeometry(100, 100, 800, 700)

        main_layout = QVBoxLayout()
        request_layout = QHBoxLayout()

        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH"])

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://api.example.com/data")

        self.send_btn = QPushButton("Enviar")
        self.send_btn.clicked.connect(self.send_request)

        request_layout.addWidget(self.method_combo)
        request_layout.addWidget(self.url_edit)
        request_layout.addWidget(self.send_btn)

        self.request_body = QPlainTextEdit()
        self.request_body.setPlaceholderText("Cuerpo de la petición (ej. JSON para POST)")

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)

        main_layout.addLayout(request_layout)
        main_layout.addWidget(QLabel("Cuerpo (Body):"))
        main_layout.addWidget(self.request_body)
        main_layout.addWidget(QLabel("Respuesta:"))
        main_layout.addWidget(self.response_output)

        self.setLayout(main_layout)

    def send_request(self):
        method = self.method_combo.currentText()
        url = self.url_edit.text()
        body = self.request_body.toPlainText()

        if not url:
            self.response_output.setText("Por favor, introduce una URL.")
            return

        self.response_output.setText("Enviando petición...")
        QApplication.processEvents()

        try:
            headers = {'Content-Type': 'application/json'}

            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, data=body, headers=headers)
            elif method == "PUT":
                response = requests.put(url, data=body, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url)
            elif method == "PATCH":
                response = requests.patch(url, data=body, headers=headers)

            self.response_output.setText(f"Status Code: {response.status_code}\n\n")

            # Try to pretty-print JSON response
            try:
                json_response = response.json()
                self.response_output.append(json.dumps(json_response, indent=4))
            except json.JSONDecodeError:
                self.response_output.append(response.text)

        except requests.exceptions.RequestException as e:
            self.response_output.setText(f"Error de red: {e}")
        except Exception as e:
            self.response_output.setText(f"Error inesperado: {e}")


if __name__ == '__main__':
    # Requires python3-requests
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = ApiClientGUI()
    ventana.show()
    sys.exit(app.exec_())
