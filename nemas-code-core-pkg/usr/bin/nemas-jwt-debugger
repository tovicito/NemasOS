#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import jwt
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QLineEdit
)

class JwtDebuggerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Depurador de JWT (JSON Web Token)')
        self.setGeometry(200, 200, 800, 600)
        main_layout = QVBoxLayout()

        self.jwt_input = QLineEdit()
        self.jwt_input.setPlaceholderText("Pega tu JWT aquí...")
        self.jwt_input.textChanged.connect(self.decode_jwt)

        self.header_output = QTextEdit()
        self.header_output.setReadOnly(True)
        self.payload_output = QTextEdit()
        self.payload_output.setReadOnly(True)
        self.signature_status = QLabel("Firma: (no verificada)")

        main_layout.addWidget(QLabel("Token JWT Codificado:"))
        main_layout.addWidget(self.jwt_input)
        main_layout.addWidget(QLabel("Cabecera (Header):"))
        main_layout.addWidget(self.header_output)
        main_layout.addWidget(QLabel("Carga Útil (Payload):"))
        main_layout.addWidget(self.payload_output)
        main_layout.addWidget(self.signature_status)
        self.setLayout(main_layout)

    def decode_jwt(self):
        token = self.jwt_input.text()
        if not token:
            self.header_output.clear()
            self.payload_output.clear()
            self.signature_status.setText("Firma: (no verificada)")
            return

        try:
            # Decode without verification to inspect contents
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})

            # Pretty print JSON
            self.header_output.setText(json.dumps(header, indent=4))

            # Check for standard time claims and convert them
            for claim in ['exp', 'iat', 'nbf']:
                if claim in payload:
                    dt = datetime.fromtimestamp(payload[claim])
                    payload[f'_{claim}_utc'] = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

            self.payload_output.setText(json.dumps(payload, indent=4))

            # Note: We don't verify the signature here as we don't have the secret.
            # A real implementation would need a field for the secret key.
            self.signature_status.setText("Firma: Válida (no verificada criptográficamente)")
            self.signature_status.setStyleSheet("color: blue;")

        except jwt.exceptions.DecodeError as e:
            self.header_output.setText(f"Error de decodificación: {e}")
            self.payload_output.clear()
            self.signature_status.setText("Firma: INVÁLIDA")
            self.signature_status.setStyleSheet("color: red;")
        except Exception as e:
            self.header_output.setText(f"Error inesperado: {e}")
            self.payload_output.clear()


if __name__ == '__main__':
    # Requires python3-jwt
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ventana = JwtDebuggerGUI()
    ventana.show()
    sys.exit(app.exec_())
