#!/bin/bash
echo '--- Ensuring directories exist... ---'
mkdir -p nemas-utils-pkg/usr/bin
mkdir -p nemas-utils-pkg/usr/share/applications

echo '--- Cleaning up old artifacts... ---'
rm -f nemas-utils-pkg/usr/bin/*
rm -f nemas-utils-pkg/usr/share/applications/*

echo 'Packaging backup_gui.py...'
cp backup_gui.py nemas-utils-pkg/usr/bin/nemas-backup
chmod +x nemas-utils-pkg/usr/bin/nemas-backup
cat > nemas-utils-pkg/usr/share/applications/nemas-backup.desktop << EOL
[Desktop Entry]
Name=Backup Gui
Type=Application
Exec=/usr/bin/nemas-backup
Icon=applications-utilities
EOL

echo 'Packaging buscador_archivos_grandes_gui.py...'
cp buscador_archivos_grandes_gui.py nemas-utils-pkg/usr/bin/nemas-buscador-archivos-grandes
chmod +x nemas-utils-pkg/usr/bin/nemas-buscador-archivos-grandes
cat > nemas-utils-pkg/usr/share/applications/nemas-buscador-archivos-grandes.desktop << EOL
[Desktop Entry]
Name=Buscador Archivos Grandes Gui
Type=Application
Exec=/usr/bin/nemas-buscador-archivos-grandes
Icon=applications-utilities
EOL

echo 'Packaging buscar_reemplazar_gui.py...'
cp buscar_reemplazar_gui.py nemas-utils-pkg/usr/bin/nemas-buscar-reemplazar
chmod +x nemas-utils-pkg/usr/bin/nemas-buscar-reemplazar
cat > nemas-utils-pkg/usr/share/applications/nemas-buscar-reemplazar.desktop << EOL
[Desktop Entry]
Name=Buscar Reemplazar Gui
Type=Application
Exec=/usr/bin/nemas-buscar-reemplazar
Icon=applications-utilities
EOL

echo 'Packaging calculadora_gui.py...'
cp calculadora_gui.py nemas-utils-pkg/usr/bin/nemas-calculadora
chmod +x nemas-utils-pkg/usr/bin/nemas-calculadora
cat > nemas-utils-pkg/usr/share/applications/nemas-calculadora.desktop << EOL
[Desktop Entry]
Name=Calculadora Gui
Type=Application
Exec=/usr/bin/nemas-calculadora
Icon=applications-utilities
EOL

echo 'Packaging comparador_directorios_gui.py...'
cp comparador_directorios_gui.py nemas-utils-pkg/usr/bin/nemas-comparador-directorios
chmod +x nemas-utils-pkg/usr/bin/nemas-comparador-directorios
cat > nemas-utils-pkg/usr/share/applications/nemas-comparador-directorios.desktop << EOL
[Desktop Entry]
Name=Comparador Directorios Gui
Type=Application
Exec=/usr/bin/nemas-comparador-directorios
Icon=applications-utilities
EOL

echo 'Packaging contador_lineas_gui.py...'
cp contador_lineas_gui.py nemas-utils-pkg/usr/bin/nemas-contador-lineas
chmod +x nemas-utils-pkg/usr/bin/nemas-contador-lineas
cat > nemas-utils-pkg/usr/share/applications/nemas-contador-lineas.desktop << EOL
[Desktop Entry]
Name=Contador Lineas Gui
Type=Application
Exec=/usr/bin/nemas-contador-lineas
Icon=applications-utilities
EOL

echo 'Packaging editor_texto_gui.py...'
cp editor_texto_gui.py nemas-utils-pkg/usr/bin/nemas-editor-texto
chmod +x nemas-utils-pkg/usr/bin/nemas-editor-texto
cat > nemas-utils-pkg/usr/share/applications/nemas-editor-texto.desktop << EOL
[Desktop Entry]
Name=Editor Texto Gui
Type=Application
Exec=/usr/bin/nemas-editor-texto
Icon=applications-utilities
EOL

echo 'Packaging extractor_gui.py...'
cp extractor_gui.py nemas-utils-pkg/usr/bin/nemas-extractor
chmod +x nemas-utils-pkg/usr/bin/nemas-extractor
cat > nemas-utils-pkg/usr/share/applications/nemas-extractor.desktop << EOL
[Desktop Entry]
Name=Extractor Gui
Type=Application
Exec=/usr/bin/nemas-extractor
Icon=applications-utilities
EOL

echo 'Packaging generador_contrasenas_gui.py...'
cp generador_contrasenas_gui.py nemas-utils-pkg/usr/bin/nemas-generador-contrasenas
chmod +x nemas-utils-pkg/usr/bin/nemas-generador-contrasenas
cat > nemas-utils-pkg/usr/share/applications/nemas-generador-contrasenas.desktop << EOL
[Desktop Entry]
Name=Generador Contrasenas Gui
Type=Application
Exec=/usr/bin/nemas-generador-contrasenas
Icon=applications-utilities
EOL

echo 'Packaging generador_informe_gui.py...'
cp generador_informe_gui.py nemas-utils-pkg/usr/bin/nemas-generador-informe
chmod +x nemas-utils-pkg/usr/bin/nemas-generador-informe
cat > nemas-utils-pkg/usr/share/applications/nemas-generador-informe.desktop << EOL
[Desktop Entry]
Name=Generador Informe Gui
Type=Application
Exec=/usr/bin/nemas-generador-informe
Icon=applications-utilities
EOL

echo 'Packaging gestor_portapapeles_gui.py...'
cp gestor_portapapeles_gui.py nemas-utils-pkg/usr/bin/nemas-gestor-portapapeles
chmod +x nemas-utils-pkg/usr/bin/nemas-gestor-portapapeles
cat > nemas-utils-pkg/usr/share/applications/nemas-gestor-portapapeles.desktop << EOL
[Desktop Entry]
Name=Gestor Portapapeles Gui
Type=Application
Exec=/usr/bin/nemas-gestor-portapapeles
Icon=applications-utilities
EOL

echo 'Packaging gestor_servicios_gui.py...'
cp gestor_servicios_gui.py nemas-utils-pkg/usr/bin/nemas-gestor-servicios
chmod +x nemas-utils-pkg/usr/bin/nemas-gestor-servicios
cat > nemas-utils-pkg/usr/share/applications/nemas-gestor-servicios.desktop << EOL
[Desktop Entry]
Name=Gestor Servicios Gui
Type=Application
Exec=/usr/bin/nemas-gestor-servicios
Icon=applications-utilities
EOL

echo 'Packaging gestor_usuarios_gui.py...'
cp gestor_usuarios_gui.py nemas-utils-pkg/usr/bin/nemas-gestor-usuarios
chmod +x nemas-utils-pkg/usr/bin/nemas-gestor-usuarios
cat > nemas-utils-pkg/usr/share/applications/nemas-gestor-usuarios.desktop << EOL
[Desktop Entry]
Name=Gestor Usuarios Gui
Type=Application
Exec=/usr/bin/nemas-gestor-usuarios
Icon=applications-utilities
EOL

echo 'Packaging info_sistema_gui.py...'
cp info_sistema_gui.py nemas-utils-pkg/usr/bin/nemas-info-sistema
chmod +x nemas-utils-pkg/usr/bin/nemas-info-sistema
cat > nemas-utils-pkg/usr/share/applications/nemas-info-sistema.desktop << EOL
[Desktop Entry]
Name=Info Sistema Gui
Type=Application
Exec=/usr/bin/nemas-info-sistema
Icon=applications-utilities
EOL

echo 'Packaging limpiador_gui.py...'
cp limpiador_gui.py nemas-utils-pkg/usr/bin/nemas-limpiador
chmod +x nemas-utils-pkg/usr/bin/nemas-limpiador
cat > nemas-utils-pkg/usr/share/applications/nemas-limpiador.desktop << EOL
[Desktop Entry]
Name=Limpiador Gui
Type=Application
Exec=/usr/bin/nemas-limpiador
Icon=applications-utilities
EOL

echo 'Packaging renombrador_masivo_gui.py...'
cp renombrador_masivo_gui.py nemas-utils-pkg/usr/bin/nemas-renombrador-masivo
chmod +x nemas-utils-pkg/usr/bin/nemas-renombrador-masivo
cat > nemas-utils-pkg/usr/share/applications/nemas-renombrador-masivo.desktop << EOL
[Desktop Entry]
Name=Renombrador Masivo Gui
Type=Application
Exec=/usr/bin/nemas-renombrador-masivo
Icon=applications-utilities
EOL

echo 'Packaging temporizador_gui.py...'
cp temporizador_gui.py nemas-utils-pkg/usr/bin/nemas-temporizador
chmod +x nemas-utils-pkg/usr/bin/nemas-temporizador
cat > nemas-utils-pkg/usr/share/applications/nemas-temporizador.desktop << EOL
[Desktop Entry]
Name=Temporizador Gui
Type=Application
Exec=/usr/bin/nemas-temporizador
Icon=applications-utilities
EOL

echo 'Packaging test_velocidad_gui.py...'
cp test_velocidad_gui.py nemas-utils-pkg/usr/bin/nemas-test-velocidad
chmod +x nemas-utils-pkg/usr/bin/nemas-test-velocidad
cat > nemas-utils-pkg/usr/share/applications/nemas-test-velocidad.desktop << EOL
[Desktop Entry]
Name=Test Velocidad Gui
Type=Application
Exec=/usr/bin/nemas-test-velocidad
Icon=applications-utilities
EOL

echo 'Packaging visor_imagenes_gui.py...'
cp visor_imagenes_gui.py nemas-utils-pkg/usr/bin/nemas-visor-imagenes
chmod +x nemas-utils-pkg/usr/bin/nemas-visor-imagenes
cat > nemas-utils-pkg/usr/share/applications/nemas-visor-imagenes.desktop << EOL
[Desktop Entry]
Name=Visor Imagenes Gui
Type=Application
Exec=/usr/bin/nemas-visor-imagenes
Icon=applications-utilities
EOL

echo 'Packaging visor_logs_gui.py...'
cp visor_logs_gui.py nemas-utils-pkg/usr/bin/nemas-visor-logs
chmod +x nemas-utils-pkg/usr/bin/nemas-visor-logs
cat > nemas-utils-pkg/usr/share/applications/nemas-visor-logs.desktop << EOL
[Desktop Entry]
Name=Visor Logs Gui
Type=Application
Exec=/usr/bin/nemas-visor-logs
Icon=applications-utilities
EOL

echo 'Packaging contador_caracteres_gui.py...'
cp contador_caracteres_gui.py nemas-utils-pkg/usr/bin/nemas-contador-caracteres
chmod +x nemas-utils-pkg/usr/bin/nemas-contador-caracteres
cat > nemas-utils-pkg/usr/share/applications/nemas-contador-caracteres.desktop << EOL
[Desktop Entry]
Name=Contador Caracteres Gui
Type=Application
Exec=/usr/bin/nemas-contador-caracteres
Icon=applications-utilities
EOL

echo 'Packaging base64_gui.py...'
cp base64_gui.py nemas-utils-pkg/usr/bin/nemas-base64
chmod +x nemas-utils-pkg/usr/bin/nemas-base64
cat > nemas-utils-pkg/usr/share/applications/nemas-base64.desktop << EOL
[Desktop Entry]
Name=Base64 Gui
Type=Application
Exec=/usr/bin/nemas-base64
Icon=applications-utilities
EOL

echo 'Packaging url_codec_gui.py...'
cp url_codec_gui.py nemas-utils-pkg/usr/bin/nemas-url-codec
chmod +x nemas-utils-pkg/usr/bin/nemas-url-codec
cat > nemas-utils-pkg/usr/share/applications/nemas-url-codec.desktop << EOL
[Desktop Entry]
Name=Url Codec Gui
Type=Application
Exec=/usr/bin/nemas-url-codec
Icon=applications-utilities
EOL

echo 'Packaging markdown_previewer_gui.py...'
cp markdown_previewer_gui.py nemas-utils-pkg/usr/bin/nemas-markdown-previewer
chmod +x nemas-utils-pkg/usr/bin/nemas-markdown-previewer
cat > nemas-utils-pkg/usr/share/applications/nemas-markdown-previewer.desktop << EOL
[Desktop Entry]
Name=Markdown Previewer Gui
Type=Application
Exec=/usr/bin/nemas-markdown-previewer
Icon=applications-utilities
EOL

echo 'Packaging json_formatter_gui.py...'
cp json_formatter_gui.py nemas-utils-pkg/usr/bin/nemas-json-formatter
chmod +x nemas-utils-pkg/usr/bin/nemas-json-formatter
cat > nemas-utils-pkg/usr/share/applications/nemas-json-formatter.desktop << EOL
[Desktop Entry]
Name=Json Formatter Gui
Type=Application
Exec=/usr/bin/nemas-json-formatter
Icon=applications-utilities
EOL

echo 'Packaging case_converter_gui.py...'
cp case_converter_gui.py nemas-utils-pkg/usr/bin/nemas-case-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-case-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-case-converter.desktop << EOL
[Desktop Entry]
Name=Case Converter Gui
Type=Application
Exec=/usr/bin/nemas-case-converter
Icon=applications-utilities
EOL

echo 'Packaging lorem_ipsum_gui.py...'
cp lorem_ipsum_gui.py nemas-utils-pkg/usr/bin/nemas-lorem-ipsum
chmod +x nemas-utils-pkg/usr/bin/nemas-lorem-ipsum
cat > nemas-utils-pkg/usr/share/applications/nemas-lorem-ipsum.desktop << EOL
[Desktop Entry]
Name=Lorem Ipsum Gui
Type=Application
Exec=/usr/bin/nemas-lorem-ipsum
Icon=applications-utilities
EOL

echo 'Packaging hex_viewer_gui.py...'
cp hex_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-hex-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-hex-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-hex-viewer.desktop << EOL
[Desktop Entry]
Name=Hex Viewer Gui
Type=Application
Exec=/usr/bin/nemas-hex-viewer
Icon=applications-utilities
EOL

echo 'Packaging checksum_gui.py...'
cp checksum_gui.py nemas-utils-pkg/usr/bin/nemas-checksum
chmod +x nemas-utils-pkg/usr/bin/nemas-checksum
cat > nemas-utils-pkg/usr/share/applications/nemas-checksum.desktop << EOL
[Desktop Entry]
Name=Checksum Gui
Type=Application
Exec=/usr/bin/nemas-checksum
Icon=applications-utilities
EOL

echo 'Packaging diff_checker_gui.py...'
cp diff_checker_gui.py nemas-utils-pkg/usr/bin/nemas-diff-checker
chmod +x nemas-utils-pkg/usr/bin/nemas-diff-checker
cat > nemas-utils-pkg/usr/share/applications/nemas-diff-checker.desktop << EOL
[Desktop Entry]
Name=Diff Checker Gui
Type=Application
Exec=/usr/bin/nemas-diff-checker
Icon=applications-utilities
EOL

echo 'Packaging duplicate_finder_gui.py...'
cp duplicate_finder_gui.py nemas-utils-pkg/usr/bin/nemas-duplicate-finder
chmod +x nemas-utils-pkg/usr/bin/nemas-duplicate-finder
cat > nemas-utils-pkg/usr/share/applications/nemas-duplicate-finder.desktop << EOL
[Desktop Entry]
Name=Duplicate Finder Gui
Type=Application
Exec=/usr/bin/nemas-duplicate-finder
Icon=applications-utilities
EOL

echo 'Packaging empty_folder_deleter_gui.py...'
cp empty_folder_deleter_gui.py nemas-utils-pkg/usr/bin/nemas-empty-folder-deleter
chmod +x nemas-utils-pkg/usr/bin/nemas-empty-folder-deleter
cat > nemas-utils-pkg/usr/share/applications/nemas-empty-folder-deleter.desktop << EOL
[Desktop Entry]
Name=Empty Folder Deleter Gui
Type=Application
Exec=/usr/bin/nemas-empty-folder-deleter
Icon=applications-utilities
EOL

echo 'Packaging image_converter_gui.py...'
cp image_converter_gui.py nemas-utils-pkg/usr/bin/nemas-image-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-image-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-image-converter.desktop << EOL
[Desktop Entry]
Name=Image Converter Gui
Type=Application
Exec=/usr/bin/nemas-image-converter
Icon=applications-utilities
EOL

echo 'Packaging audio_player_gui.py...'
cp audio_player_gui.py nemas-utils-pkg/usr/bin/nemas-audio-player
chmod +x nemas-utils-pkg/usr/bin/nemas-audio-player
cat > nemas-utils-pkg/usr/share/applications/nemas-audio-player.desktop << EOL
[Desktop Entry]
Name=Audio Player Gui
Type=Application
Exec=/usr/bin/nemas-audio-player
Icon=applications-utilities
EOL

echo 'Packaging video_player_gui.py...'
cp video_player_gui.py nemas-utils-pkg/usr/bin/nemas-video-player
chmod +x nemas-utils-pkg/usr/bin/nemas-video-player
cat > nemas-utils-pkg/usr/share/applications/nemas-video-player.desktop << EOL
[Desktop Entry]
Name=Video Player Gui
Type=Application
Exec=/usr/bin/nemas-video-player
Icon=applications-utilities
EOL

echo 'Packaging pdf_merger_gui.py...'
cp pdf_merger_gui.py nemas-utils-pkg/usr/bin/nemas-pdf-merger
chmod +x nemas-utils-pkg/usr/bin/nemas-pdf-merger
cat > nemas-utils-pkg/usr/share/applications/nemas-pdf-merger.desktop << EOL
[Desktop Entry]
Name=Pdf Merger Gui
Type=Application
Exec=/usr/bin/nemas-pdf-merger
Icon=applications-utilities
EOL

echo 'Packaging file_encryptor_gui.py...'
cp file_encryptor_gui.py nemas-utils-pkg/usr/bin/nemas-file-encryptor
chmod +x nemas-utils-pkg/usr/bin/nemas-file-encryptor
cat > nemas-utils-pkg/usr/share/applications/nemas-file-encryptor.desktop << EOL
[Desktop Entry]
Name=File Encryptor Gui
Type=Application
Exec=/usr/bin/nemas-file-encryptor
Icon=applications-utilities
EOL

echo 'Packaging batch_resizer_gui.py...'
cp batch_resizer_gui.py nemas-utils-pkg/usr/bin/nemas-batch-resizer
chmod +x nemas-utils-pkg/usr/bin/nemas-batch-resizer
cat > nemas-utils-pkg/usr/share/applications/nemas-batch-resizer.desktop << EOL
[Desktop Entry]
Name=Batch Resizer Gui
Type=Application
Exec=/usr/bin/nemas-batch-resizer
Icon=applications-utilities
EOL

echo 'Packaging exif_viewer_gui.py...'
cp exif_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-exif-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-exif-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-exif-viewer.desktop << EOL
[Desktop Entry]
Name=Exif Viewer Gui
Type=Application
Exec=/usr/bin/nemas-exif-viewer
Icon=applications-utilities
EOL

echo 'Packaging file_checksum_gui.py...'
cp file_checksum_gui.py nemas-utils-pkg/usr/bin/nemas-file-checksum
chmod +x nemas-utils-pkg/usr/bin/nemas-file-checksum
cat > nemas-utils-pkg/usr/share/applications/nemas-file-checksum.desktop << EOL
[Desktop Entry]
Name=File Checksum Gui
Type=Application
Exec=/usr/bin/nemas-file-checksum
Icon=applications-utilities
EOL

echo 'Packaging ip_viewer_gui.py...'
cp ip_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-ip-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-ip-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-ip-viewer.desktop << EOL
[Desktop Entry]
Name=Ip Viewer Gui
Type=Application
Exec=/usr/bin/nemas-ip-viewer
Icon=applications-utilities
EOL

echo 'Packaging port_scanner_gui.py...'
cp port_scanner_gui.py nemas-utils-pkg/usr/bin/nemas-port-scanner
chmod +x nemas-utils-pkg/usr/bin/nemas-port-scanner
cat > nemas-utils-pkg/usr/share/applications/nemas-port-scanner.desktop << EOL
[Desktop Entry]
Name=Port Scanner Gui
Type=Application
Exec=/usr/bin/nemas-port-scanner
Icon=applications-utilities
EOL

echo 'Packaging whois_lookup_gui.py...'
cp whois_lookup_gui.py nemas-utils-pkg/usr/bin/nemas-whois-lookup
chmod +x nemas-utils-pkg/usr/bin/nemas-whois-lookup
cat > nemas-utils-pkg/usr/share/applications/nemas-whois-lookup.desktop << EOL
[Desktop Entry]
Name=Whois Lookup Gui
Type=Application
Exec=/usr/bin/nemas-whois-lookup
Icon=applications-utilities
EOL

echo 'Packaging dns_lookup_gui.py...'
cp dns_lookup_gui.py nemas-utils-pkg/usr/bin/nemas-dns-lookup
chmod +x nemas-utils-pkg/usr/bin/nemas-dns-lookup
cat > nemas-utils-pkg/usr/share/applications/nemas-dns-lookup.desktop << EOL
[Desktop Entry]
Name=Dns Lookup Gui
Type=Application
Exec=/usr/bin/nemas-dns-lookup
Icon=applications-utilities
EOL

echo 'Packaging http_header_gui.py...'
cp http_header_gui.py nemas-utils-pkg/usr/bin/nemas-http-header
chmod +x nemas-utils-pkg/usr/bin/nemas-http-header
cat > nemas-utils-pkg/usr/share/applications/nemas-http-header.desktop << EOL
[Desktop Entry]
Name=Http Header Gui
Type=Application
Exec=/usr/bin/nemas-http-header
Icon=applications-utilities
EOL

echo 'Packaging ping_tool_gui.py...'
cp ping_tool_gui.py nemas-utils-pkg/usr/bin/nemas-ping-tool
chmod +x nemas-utils-pkg/usr/bin/nemas-ping-tool
cat > nemas-utils-pkg/usr/share/applications/nemas-ping-tool.desktop << EOL
[Desktop Entry]
Name=Ping Tool Gui
Type=Application
Exec=/usr/bin/nemas-ping-tool
Icon=applications-utilities
EOL

echo 'Packaging qr_generator_gui.py...'
cp qr_generator_gui.py nemas-utils-pkg/usr/bin/nemas-qr-generator
chmod +x nemas-utils-pkg/usr/bin/nemas-qr-generator
cat > nemas-utils-pkg/usr/share/applications/nemas-qr-generator.desktop << EOL
[Desktop Entry]
Name=Qr Generator Gui
Type=Application
Exec=/usr/bin/nemas-qr-generator
Icon=applications-utilities
EOL

echo 'Packaging color_picker_gui.py...'
cp color_picker_gui.py nemas-utils-pkg/usr/bin/nemas-color-picker
chmod +x nemas-utils-pkg/usr/bin/nemas-color-picker
cat > nemas-utils-pkg/usr/share/applications/nemas-color-picker.desktop << EOL
[Desktop Entry]
Name=Color Picker Gui
Type=Application
Exec=/usr/bin/nemas-color-picker
Icon=applications-utilities
EOL

echo 'Packaging stopwatch_gui.py...'
cp stopwatch_gui.py nemas-utils-pkg/usr/bin/nemas-stopwatch
chmod +x nemas-utils-pkg/usr/bin/nemas-stopwatch
cat > nemas-utils-pkg/usr/share/applications/nemas-stopwatch.desktop << EOL
[Desktop Entry]
Name=Stopwatch Gui
Type=Application
Exec=/usr/bin/nemas-stopwatch
Icon=applications-utilities
EOL

echo 'Packaging qr_reader_gui.py...'
cp qr_reader_gui.py nemas-utils-pkg/usr/bin/nemas-qr-reader
chmod +x nemas-utils-pkg/usr/bin/nemas-qr-reader
cat > nemas-utils-pkg/usr/share/applications/nemas-qr-reader.desktop << EOL
[Desktop Entry]
Name=Qr Reader Gui
Type=Application
Exec=/usr/bin/nemas-qr-reader
Icon=applications-utilities
EOL

echo 'Packaging timestamp_converter_gui.py...'
cp timestamp_converter_gui.py nemas-utils-pkg/usr/bin/nemas-timestamp-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-timestamp-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-timestamp-converter.desktop << EOL
[Desktop Entry]
Name=Timestamp Converter Gui
Type=Application
Exec=/usr/bin/nemas-timestamp-converter
Icon=applications-utilities
EOL

echo 'Packaging cron_editor_gui.py...'
cp cron_editor_gui.py nemas-utils-pkg/usr/bin/nemas-cron-editor
chmod +x nemas-utils-pkg/usr/bin/nemas-cron-editor
cat > nemas-utils-pkg/usr/share/applications/nemas-cron-editor.desktop << EOL
[Desktop Entry]
Name=Cron Editor Gui
Type=Application
Exec=/usr/bin/nemas-cron-editor
Icon=applications-utilities
EOL

echo 'Packaging regex_tester_gui.py...'
cp regex_tester_gui.py nemas-utils-pkg/usr/bin/nemas-regex-tester
chmod +x nemas-utils-pkg/usr/bin/nemas-regex-tester
cat > nemas-utils-pkg/usr/share/applications/nemas-regex-tester.desktop << EOL
[Desktop Entry]
Name=Regex Tester Gui
Type=Application
Exec=/usr/bin/nemas-regex-tester
Icon=applications-utilities
EOL

echo 'Packaging snippet_manager_gui.py...'
cp snippet_manager_gui.py nemas-utils-pkg/usr/bin/nemas-snippet-manager
chmod +x nemas-utils-pkg/usr/bin/nemas-snippet-manager
cat > nemas-utils-pkg/usr/share/applications/nemas-snippet-manager.desktop << EOL
[Desktop Entry]
Name=Snippet Manager Gui
Type=Application
Exec=/usr/bin/nemas-snippet-manager
Icon=applications-utilities
EOL

echo 'Packaging json_to_yaml_gui.py...'
cp json_to_yaml_gui.py nemas-utils-pkg/usr/bin/nemas-json-to-yaml
chmod +x nemas-utils-pkg/usr/bin/nemas-json-to-yaml
cat > nemas-utils-pkg/usr/share/applications/nemas-json-to-yaml.desktop << EOL
[Desktop Entry]
Name=Json To Yaml Gui
Type=Application
Exec=/usr/bin/nemas-json-to-yaml
Icon=applications-utilities
EOL

echo 'Packaging yaml_to_json_gui.py...'
cp yaml_to_json_gui.py nemas-utils-pkg/usr/bin/nemas-yaml-to-json
chmod +x nemas-utils-pkg/usr/bin/nemas-yaml-to-json
cat > nemas-utils-pkg/usr/share/applications/nemas-yaml-to-json.desktop << EOL
[Desktop Entry]
Name=Yaml To Json Gui
Type=Application
Exec=/usr/bin/nemas-yaml-to-json
Icon=applications-utilities
EOL

echo 'Packaging system_monitor_gui.py...'
cp system_monitor_gui.py nemas-utils-pkg/usr/bin/nemas-system-monitor
chmod +x nemas-utils-pkg/usr/bin/nemas-system-monitor
cat > nemas-utils-pkg/usr/share/applications/nemas-system-monitor.desktop << EOL
[Desktop Entry]
Name=System Monitor Gui
Type=Application
Exec=/usr/bin/nemas-system-monitor
Icon=applications-utilities
EOL

echo 'Packaging process_viewer_gui.py...'
cp process_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-process-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-process-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-process-viewer.desktop << EOL
[Desktop Entry]
Name=Process Viewer Gui
Type=Application
Exec=/usr/bin/nemas-process-viewer
Icon=applications-utilities
EOL

echo 'Packaging clipboard_history_gui.py...'
cp clipboard_history_gui.py nemas-utils-pkg/usr/bin/nemas-clipboard-history
chmod +x nemas-utils-pkg/usr/bin/nemas-clipboard-history
cat > nemas-utils-pkg/usr/share/applications/nemas-clipboard-history.desktop << EOL
[Desktop Entry]
Name=Clipboard History Gui
Type=Application
Exec=/usr/bin/nemas-clipboard-history
Icon=applications-utilities
EOL

echo 'Packaging screen_ruler_gui.py...'
cp screen_ruler_gui.py nemas-utils-pkg/usr/bin/nemas-screen-ruler
chmod +x nemas-utils-pkg/usr/bin/nemas-screen-ruler
cat > nemas-utils-pkg/usr/share/applications/nemas-screen-ruler.desktop << EOL
[Desktop Entry]
Name=Screen Ruler Gui
Type=Application
Exec=/usr/bin/nemas-screen-ruler
Icon=applications-utilities
EOL

echo 'Packaging digital_clock_gui.py...'
cp digital_clock_gui.py nemas-utils-pkg/usr/bin/nemas-digital-clock
chmod +x nemas-utils-pkg/usr/bin/nemas-digital-clock
cat > nemas-utils-pkg/usr/share/applications/nemas-digital-clock.desktop << EOL
[Desktop Entry]
Name=Digital Clock Gui
Type=Application
Exec=/usr/bin/nemas-digital-clock
Icon=applications-utilities
EOL

echo 'Packaging simple_calendar_gui.py...'
cp simple_calendar_gui.py nemas-utils-pkg/usr/bin/nemas-simple-calendar
chmod +x nemas-utils-pkg/usr/bin/nemas-simple-calendar
cat > nemas-utils-pkg/usr/share/applications/nemas-simple-calendar.desktop << EOL
[Desktop Entry]
Name=Simple Calendar Gui
Type=Application
Exec=/usr/bin/nemas-simple-calendar
Icon=applications-utilities
EOL

echo 'Packaging unit_converter_gui.py...'
cp unit_converter_gui.py nemas-utils-pkg/usr/bin/nemas-unit-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-unit-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-unit-converter.desktop << EOL
[Desktop Entry]
Name=Unit Converter Gui
Type=Application
Exec=/usr/bin/nemas-unit-converter
Icon=applications-utilities
EOL

echo 'Packaging world_clock_gui.py...'
cp world_clock_gui.py nemas-utils-pkg/usr/bin/nemas-world-clock
chmod +x nemas-utils-pkg/usr/bin/nemas-world-clock
cat > nemas-utils-pkg/usr/share/applications/nemas-world-clock.desktop << EOL
[Desktop Entry]
Name=World Clock Gui
Type=Application
Exec=/usr/bin/nemas-world-clock
Icon=applications-utilities
EOL

echo 'Packaging sketchpad_gui.py...'
cp sketchpad_gui.py nemas-utils-pkg/usr/bin/nemas-sketchpad
chmod +x nemas-utils-pkg/usr/bin/nemas-sketchpad
cat > nemas-utils-pkg/usr/share/applications/nemas-sketchpad.desktop << EOL
[Desktop Entry]
Name=Sketchpad Gui
Type=Application
Exec=/usr/bin/nemas-sketchpad
Icon=applications-utilities
EOL

echo 'Packaging system_uptime_gui.py...'
cp system_uptime_gui.py nemas-utils-pkg/usr/bin/nemas-system-uptime
chmod +x nemas-utils-pkg/usr/bin/nemas-system-uptime
cat > nemas-utils-pkg/usr/share/applications/nemas-system-uptime.desktop << EOL
[Desktop Entry]
Name=System Uptime Gui
Type=Application
Exec=/usr/bin/nemas-system-uptime
Icon=applications-utilities
EOL

echo 'Packaging font_viewer_gui.py...'
cp font_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-font-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-font-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-font-viewer.desktop << EOL
[Desktop Entry]
Name=Font Viewer Gui
Type=Application
Exec=/usr/bin/nemas-font-viewer
Icon=applications-utilities
EOL

echo 'Packaging todo_list_gui.py...'
cp todo_list_gui.py nemas-utils-pkg/usr/bin/nemas-todo-list
chmod +x nemas-utils-pkg/usr/bin/nemas-todo-list
cat > nemas-utils-pkg/usr/share/applications/nemas-todo-list.desktop << EOL
[Desktop Entry]
Name=Todo List Gui
Type=Application
Exec=/usr/bin/nemas-todo-list
Icon=applications-utilities
EOL

echo 'Packaging random_number_gui.py...'
cp random_number_gui.py nemas-utils-pkg/usr/bin/nemas-random-number
chmod +x nemas-utils-pkg/usr/bin/nemas-random-number
cat > nemas-utils-pkg/usr/share/applications/nemas-random-number.desktop << EOL
[Desktop Entry]
Name=Random Number Gui
Type=Application
Exec=/usr/bin/nemas-random-number
Icon=applications-utilities
EOL

echo 'Packaging barcode_generator_gui.py...'
cp barcode_generator_gui.py nemas-utils-pkg/usr/bin/nemas-barcode-generator
chmod +x nemas-utils-pkg/usr/bin/nemas-barcode-generator
cat > nemas-utils-pkg/usr/share/applications/nemas-barcode-generator.desktop << EOL
[Desktop Entry]
Name=Barcode Generator Gui
Type=Application
Exec=/usr/bin/nemas-barcode-generator
Icon=applications-utilities
EOL

echo 'Packaging weather_applet_gui.py...'
cp weather_applet_gui.py nemas-utils-pkg/usr/bin/nemas-weather-applet
chmod +x nemas-utils-pkg/usr/bin/nemas-weather-applet
cat > nemas-utils-pkg/usr/share/applications/nemas-weather-applet.desktop << EOL
[Desktop Entry]
Name=Weather Applet Gui
Type=Application
Exec=/usr/bin/nemas-weather-applet
Icon=applications-utilities
EOL

echo 'Packaging shutdown_gui.py...'
cp shutdown_gui.py nemas-utils-pkg/usr/bin/nemas-shutdown
chmod +x nemas-utils-pkg/usr/bin/nemas-shutdown
cat > nemas-utils-pkg/usr/share/applications/nemas-shutdown.desktop << EOL
[Desktop Entry]
Name=Shutdown Gui
Type=Application
Exec=/usr/bin/nemas-shutdown
Icon=applications-utilities
EOL

echo 'Packaging brightness_control_gui.py...'
cp brightness_control_gui.py nemas-utils-pkg/usr/bin/nemas-brightness-control
chmod +x nemas-utils-pkg/usr/bin/nemas-brightness-control
cat > nemas-utils-pkg/usr/share/applications/nemas-brightness-control.desktop << EOL
[Desktop Entry]
Name=Brightness Control Gui
Type=Application
Exec=/usr/bin/nemas-brightness-control
Icon=applications-utilities
EOL

echo 'Packaging screenshot_tool_gui.py...'
cp screenshot_tool_gui.py nemas-utils-pkg/usr/bin/nemas-screenshot-tool
chmod +x nemas-utils-pkg/usr/bin/nemas-screenshot-tool
cat > nemas-utils-pkg/usr/share/applications/nemas-screenshot-tool.desktop << EOL
[Desktop Entry]
Name=Screenshot Tool Gui
Type=Application
Exec=/usr/bin/nemas-screenshot-tool
Icon=applications-utilities
EOL

echo 'Packaging weekly_planner_gui.py...'
cp weekly_planner_gui.py nemas-utils-pkg/usr/bin/nemas-weekly-planner
chmod +x nemas-utils-pkg/usr/bin/nemas-weekly-planner
cat > nemas-utils-pkg/usr/share/applications/nemas-weekly-planner.desktop << EOL
[Desktop Entry]
Name=Weekly Planner Gui
Type=Application
Exec=/usr/bin/nemas-weekly-planner
Icon=applications-utilities
EOL

echo '--- All files packaged successfully! ---'
