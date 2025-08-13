#!/bin/bash
# Script to package the 20 existing GUI utilities into the nemas-utils-pkg directory

# First, clear the calculator files since I already did that one manually
# and I'm re-running for all of them.
rm nemas-utils-pkg/usr/bin/nemas-calculator
rm nemas-utils-pkg/usr/share/applications/nemas-calculator.desktop

for f in *_gui.py; do
  # Get the base name, e.g., "calculadora_gui.py" -> "calculadora"
  basename=$(echo "$f" | sed 's/_gui.py//')

  # Create the command name, e.g., "nemas-calculator"
  cmdname="nemas-${basename//_/-}" # replace underscores with hyphens

  # --- Create Executable ---
  echo "Processing $f..."
  cp "$f" "nemas-utils-pkg/usr/bin/$cmdname"
  chmod +x "nemas-utils-pkg/usr/bin/$cmdname"

  # --- Create .desktop file ---
  # Default values
  name_human_readable=$(echo "$basename" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')
  comment="A Nemás OS utility."
  icon="applications-utilities" # A good default

  # Customizations based on filename
  case $basename in
    "calculadora")
      name_human_readable="Calculadora"
      comment="Una simple calculadora de escritorio"
      icon="accessories-calculator"
      ;;
    "editor_texto")
      name_human_readable="Editor de Texto"
      comment="Un editor de texto simple"
      icon="accessories-text-editor"
      ;;
    "visor_imagenes")
      name_human_readable="Visor de Imágenes"
      comment="Un visor de imágenes simple"
      icon="multimedia-photo-viewer"
      ;;
    "info_sistema")
      name_human_readable="Información del Sistema"
      comment="Muestra información del sistema"
      icon="utilities-system-monitor"
      ;;
    "buscador_archivos_grandes")
      name_human_readable="Buscador de Archivos Grandes"
      comment="Encuentra archivos grandes en tu disco"
      icon="system-search"
      ;;
    "renombrador_masivo")
      name_human_readable="Renombrador Masivo"
      comment="Renombra múltiples archivos a la vez"
      icon="document-properties"
      ;;
    "generador_contrasenas")
      name_human_readable="Generador de Contraseñas"
      comment="Genera contraseñas seguras"
      icon="utilities-password"
      ;;
    "limpiador")
      name_human_readable="Limpiador de Sistema"
      comment="Limpia archivos innecesarios del sistema"
      icon="user-trash"
      ;;
  esac

  desktop_file="nemas-utils-pkg/usr/share/applications/$cmdname.desktop"
  echo "Creating $desktop_file..."
  cat > "$desktop_file" << EOL
[Desktop Entry]
Version=1.0
Name=$name_human_readable
Comment=$comment
Exec=/usr/bin/$cmdname
Icon=$icon
Terminal=false
Type=Application
Categories=Utility;
EOL

done

echo "Done."
