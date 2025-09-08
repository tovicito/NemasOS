#!/bin/bash

RELEASE_TAG="v6.0.0-plasma"
RELEASE_TITLE="TPT v6.0 - Integración con Plasma Discover"
RELEASE_FILE="tpt-plasma-backend.tar.gz"

RELEASE_NOTES="**TPT v6.0 representa una re-arquitectura completa, transformando TPT en un potente backend de línea de comandos con integración nativa para el centro de software de KDE, Plasma Discover.**

Esta versión abandona la GUI propia en favor de una experiencia de usuario más integrada y profesional en el escritorio Plasma.

### ✨ Características Principales

- **Backend de Plasma Discover:**
  - TPT ahora puede ser usado directamente desde Plasma Discover para buscar, instalar y desinstalar paquetes.
  - La integración se realiza a través de un backend de D-Bus, siguiendo las mejores prácticas de KDE.

- **CLI Refactorizada para Backend:**
  - La CLI ha sido simplificada y optimizada para uso no interactivo.
  - Se ha eliminado `rich` y toda la complejidad de la UI en la terminal.
  - Los comandos clave como `search` ahora pueden devolver resultados en formato JSON para ser consumidos por otros programas.

- **Instalación Simplificada de la Integración:**
  - El nuevo comando `tpt system-integrate install` instala automáticamente todos los componentes necesarios para que Discover reconozca a TPT (el ejecutable del backend, el archivo de metadatos y el servicio de D-Bus).

- **Core Simplificado:**
  - Se ha eliminado todo el código relacionado con la GUI en GTK y el asistente de configuración, resultando en una base de código más ligera y centrada.
  - El sistema de logging ha sido simplificado para usar el módulo estándar de Python.

### 📦 Archivos de la Release

El archivo `tpt-plasma-backend.tar.gz` contiene el proyecto completo.

**Instalación:**
1. Descomprimir el archivo: \`tar -xzvf tpt-plasma-backend.tar.gz\`
2. Navegar al directorio: \`cd tpt-plasma-project\` (o el nombre del directorio creado)
3. Ejecutar el comando de integración con permisos de superusuario: \`sudo ./exec/tpt system-integrate install\`
4. Reiniciar Plasma Discover.

Gracias por usar TPT."

# El comando final para crear la release
gh release create "$RELEASE_TAG" "$RELEASE_FILE" \
    --title "$RELEASE_TITLE" \
    --notes "$RELEASE_NOTES" \
    --latest
