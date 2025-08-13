#!/bin/bash
echo "--- Starting final packaging process ---"

# Clean all previous packaging artifacts
rm -rf nemas-utils-pkg/usr/bin/*
rm -rf nemas-utils-pkg/usr/share/applications/*
echo "Cleaned old artifacts."

# --- Package Existing 20 Utilities ---
echo "Packaging 20 existing utilities..."
EXISTING_FILES=(*gui.py) # This will grab all of them, but we will handle new ones later
EXISTING_FILES=( $(ls *_gui.py | grep -v -e "placeholder" -e "color_picker" -e "stopwatch" -e "qr_generator" -e "lorem_ipsum" -e "hex_viewer" -e "checksum" -e "diff_checker" -e "duplicate_finder" -e "empty_folder_deleter" -e "image_converter" -e "audio_player" -e "video_player" -e "pdf_merger" -e "file_encryptor" -e "batch_resizer" -e "exif_viewer" -e "file_checksum" -e "ip_viewer" -e "port_scanner" -e "whois_lookup" -e "dns_lookup" -e "http_header" -e "ping_tool" -e "base64" -e "url_codec" -e "markdown_previewer" -e "json_formatter" -e "case_converter" -e "contador_caracteres" ) )
# This is getting too complex. I will just list them manually.

# --- Manually list all 77 files ---
ALL_GUI_FILES=(
    # Existing
    "backup_gui.py" "buscador_archivos_grandes_gui.py" "buscar_reemplazar_gui.py" "calculadora_gui.py"
    "comparador_directorios_gui.py" "contador_lineas_gui.py" "editor_texto_gui.py" "extractor_gui.py"
    "generador_contrasenas_gui.py" "generador_informe_gui.py" "gestor_portapapeles_gui.py"
    "gestor_servicios_gui.py" "gestor_usuarios_gui.py" "info_sistema_gui.py" "limpiador_gui.py"
    "renombrador_masivo_gui.py" "temporizador_gui.py" "test_velocidad_gui.py" "visor_imagenes_gui.py"
    "visor_logs_gui.py"
    # New - Full
    "contador_caracteres_gui.py" "base64_gui.py" "url_codec_gui.py" "markdown_previewer_gui.py"
    "json_formatter_gui.py" "case_converter_gui.py" "lorem_ipsum_gui.py" "hex_viewer_gui.py"
    "checksum_gui.py" "diff_checker_gui.py" "duplicate_finder_gui.py" "empty_folder_deleter_gui.py"
    "image_converter_gui.py" "audio_player_gui.py" "video_player_gui.py" "pdf_merger_gui.py"
    "file_encryptor_gui.py" "batch_resizer_gui.py" "exif_viewer_gui.py" "file_checksum_gui.py"
    "ip_viewer_gui.py" "port_scanner_gui.py" "whois_lookup_gui.py" "dns_lookup_gui.py"
    "http_header_gui.py" "ping_tool_gui.py" "qr_generator_gui.py" "color_picker_gui.py" "stopwatch_gui.py"
    # New - Placeholders
    "qr_reader_gui.py" "timestamp_converter_gui.py" "cron_editor_gui.py" "regex_tester_gui.py"
    "snippet_manager_gui.py" "json_to_yaml_gui.py" "yaml_to_json_gui.py" "system_monitor_gui.py"
    "process_viewer_gui.py" "clipboard_history_gui.py" "screen_ruler_gui.py" "digital_clock_gui.py"
    "simple_calendar_gui.py" "unit_converter_gui.py" "world_clock_gui.py" "sketchpad_gui.py"
    "system_uptime_gui.py" "font_viewer_gui.py" "todo_list_gui.py" "random_number_gui.py"
    "barcode_generator_gui.py" "weather_applet_gui.py" "shutdown_gui.py" "brightness_control_gui.py"
    "screenshot_tool_gui.py" "weekly_planner_gui.py"
)

for f in "\${ALL_GUI_FILES[@]}"; do
  basename=\$(echo "\$f" | sed 's/_gui.py//')
  cmdname="nemas-\${basename//_/-}"

  echo "Packaging \$f as \$cmdname"
  cp "\$f" "nemas-utils-pkg/usr/bin/\$cmdname"
  chmod +x "nemas-utils-pkg/usr/bin/\$cmdname"

  name_human_readable=\$(echo "\$basename" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')

  desktop_file="nemas-utils-pkg/usr/share/applications/\$cmdname.desktop"
  cat > "\$desktop_file" << EOL
[Desktop Entry]
Version=1.0
Name=\$name_human_readable
Comment=A Nemás OS utility.
Exec=/usr/bin/\$cmdname
Icon=applications-utilities
Terminal=false
Type=Application
Categories=Utility;
EOL
done

echo "--- Packaging complete ---"
