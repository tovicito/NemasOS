#!/bin/bash

# Script para crear la release de GitHub de forma segura.

RELEASE_TAG="v5.0.0"
RELEASE_TITLE="TPT 5.0: El Renacimiento"
RELEASE_FILE="tpt-5.0.0.tar.gz"

RELEASE_NOTES="**TPT 5.0 es la versión más grande y ambiciosa hasta la fecha, reconstruida desde cero para ser una herramienta de gestión de paquetes verdaderamente profesional, robusta y fácil de usar.**

### ✨ Características Principales

- **Asistente de Configuración Inicial (Ultra-Setup):**
  - TPT ahora te da la bienvenida con un asistente de configuración la primera vez que se ejecuta.
  - **Personalización total:** Configura tu idioma, repositorios, comportamiento de la terminal (salida enriquecida, confirmaciones), ajustes de red y la integración con AADPO, todo desde una cómoda interfaz gráfica.

- **Soporte Multi-idioma (Internacionalización):**
  - La aplicación entera (CLI y GUI) está preparada para ser traducida.
  - Se incluyen traducciones iniciales para Español, Inglés y Portugués, generadas automáticamente.
  - El idioma se compila bajo demanda por el asistente de configuración para ahorrar espacio y recursos.

- **Sistema de Repositorios Git Inteligente:**
  - `tpt install` ahora puede **clonar repositorios Git** como último recurso si no encuentra un paquete.
  - Es lo suficientemente inteligente como para derivar la URL de clonación de `github.com` a partir de las URLs de `raw.githubusercontent.com`.
  - Clona únicamente la rama `regular` para máxima eficiencia.
  - `tpt upgrade` actualiza estos repositorios con `git pull` para mantener tus paquetes de Git al día.

- **Robustez y Experiencia de Usuario Mejoradas:**
  - **GUI en GTK4/Libadwaita:** Moderna, con indicadores de estado, y manejo de errores mejorado.
  - **Comando `uninstall` universal:** Ahora puede desinstalar paquetes de TPT y también intentar desinstalar paquetes de `apt`, `flatpak` y `snap`.
  - **Comando `aadpo-status`:** Para ver qué actualizaciones se aplicarán en el próximo reinicio.
  - **Confirmaciones Configurables:** Tú decides si quieres confirmar las acciones críticas.

### 📦 Archivos de la Release

El archivo `tpt-5.0.0.tar.gz` contiene la estructura completa del proyecto.

**Instalación recomendada:**
1. Descomprimir el archivo: \`tar -xzvf tpt-5.0.0.tar.gz\`
2. Mover el proyecto a una ubicación permanente: \`sudo mv tpt_project /opt/tpt\`
3. Mover los ejecutables a una ubicación permanente: \`sudo mv exec /opt/tpt/\`
4. Crear enlaces simbólicos para que los comandos estén disponibles en el PATH:
   \`\`\`bash
   sudo ln -sf /opt/tpt/exec/tpt /usr/local/bin/tpt
   sudo ln -sf /opt/tpt/exec/tpt-setup /usr/local/bin/tpt-setup
   sudo ln -sf /opt/tpt/exec/tpt-apply-updates /usr/local/bin/tpt-apply-updates
   \`\`\`
5. Ejecutar `tpt` por primera vez para lanzar el asistente de configuración.

Gracias por usar TPT."

# El comando final para crear la release
gh release create "$RELEASE_TAG" "$RELEASE_FILE" \
    --title "$RELEASE_TITLE" \
    --notes "$RELEASE_NOTES" \
    --latest
