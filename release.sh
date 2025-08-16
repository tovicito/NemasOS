#!/bin/bash

# Script para crear la release de GitHub de forma segura, evitando problemas de parsing del shell.

RELEASE_TAG="v4.0.0"
RELEASE_TITLE="TPT 4.0: La Unificación Total"
RELEASE_FILE="tpt-4.0.0.tar.gz"

# La descripción se guarda en una variable para mayor claridad.
RELEASE_NOTES="**TPT 4.0 es la culminación de un esfuerzo masivo de refactorización y expansión, convirtiendo a TPT en un gestor de paquetes verdaderamente universal y robusto.**

### ✨ Características Principales

- **Búsqueda Universal:** Busca paquetes de forma concurrente en los repositorios de TPT, APT, Flatpak y Snap con un solo comando ('tpt search').
- **Instalación Inteligente:** Si un paquete se encuentra en múltiples fuentes, 'tpt install' ahora te preguntará cuál versión deseas instalar, dándote control total.
- **Fallback por Convención:** Si un paquete no está en ningún manifiesto, TPT intentará encontrarlo de forma inteligente en los repositorios basándose en convenciones de nomenclatura.
- **GUI Moderna con GTK4:** La interfaz gráfica ha sido completamente reconstruida con GTK4 y Libadwaita, ofreciendo una experiencia de usuario nativa, rápida y agradable. Incluye búsqueda asíncrona y un log integrado.
- **AADPO (Actualizaciones Antes Del PowerOff):** Un nuevo sistema de actualización que permite descargar e instalar actualizaciones de forma desatendida durante el apagado del sistema. Se integra perfectamente con 'systemd' ('tpt system-integrate').
- **Soporte Extendido de Formatos:** Se ha añadido soporte para '.tar.xz', '.deb.xz', '.ps1' (Powershell), paquetes de parches ('nemas_patch_zip') y metapaquetes ('meta_zip').

### 📦 Archivos de la Release

El archivo 'tpt-4.0.0.tar.gz' contiene la estructura completa del proyecto.

**Instalación recomendada:**
1. Descomprimir el archivo: \`tar -xzvf tpt-4.0.0.tar.gz\`
2. Mover el proyecto a una ubicación permanente: \`sudo mv tpt_project /opt/tpt\`
3. Mover los ejecutables a una ubicación permanente: \`sudo mv exec /opt/tpt/\`
4. Crear enlaces simbólicos para que los comandos estén disponibles en el PATH:
   \`\`\`bash
   sudo ln -sf /opt/tpt/exec/tpt /usr/local/bin/tpt
   sudo ln -sf /opt/tpt/exec/tpt-apply-updates /usr/local/bin/tpt-apply-updates
   \`\`\`

Gracias por usar TPT."

# El comando final para crear la release
gh release create "$RELEASE_TAG" "$RELEASE_FILE" \
    --title "$RELEASE_TITLE" \
    --notes "$RELEASE_NOTES" \
    --latest
