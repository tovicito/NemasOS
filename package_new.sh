#!/bin/bash
# This script packages all new utilities.
# It's overwritten each time a new batch is added.

# Clean up previous files if they exist to avoid duplication
# This is a bit brute-force but effective for this workflow.
rm nemas-utils-pkg/usr/bin/nemas-*
rm nemas-utils-pkg/usr/share/applications/nemas-*.desktop

# --- Batch 1 (Character Counter) ---
cp contador_caracteres_gui.py nemas-utils-pkg/usr/bin/nemas-contador-caracteres
chmod +x nemas-utils-pkg/usr/bin/nemas-contador-caracteres
cat > nemas-utils-pkg/usr/share/applications/nemas-contador-caracteres.desktop << EOL
[Desktop Entry]
Name=Contador de Caracteres
Exec=/usr/bin/nemas-contador-caracteres
Icon=accessories-character-map
Type=Application
EOL

# --- Batch 2 (5 utilities) ---
cp base64_gui.py nemas-utils-pkg/usr/bin/nemas-base64
chmod +x nemas-utils-pkg/usr/bin/nemas-base64
cat > nemas-utils-pkg/usr/share/applications/nemas-base64.desktop << EOL
[Desktop Entry]
Name=Base64 Util
Exec=/usr/bin/nemas-base64
Icon=applications-utilities
Type=Application
EOL

cp url_codec_gui.py nemas-utils-pkg/usr/bin/nemas-url-codec
chmod +x nemas-utils-pkg/usr/bin/nemas-url-codec
cat > nemas-utils-pkg/usr/share/applications/nemas-url-codec.desktop << EOL
[Desktop Entry]
Name=URL Codec
Exec=/usr/bin/nemas-url-codec
Icon=applications-utilities
Type=Application
EOL

cp markdown_previewer_gui.py nemas-utils-pkg/usr/bin/nemas-markdown-previewer
chmod +x nemas-utils-pkg/usr/bin/nemas-markdown-previewer
cat > nemas-utils-pkg/usr/share/applications/nemas-markdown-previewer.desktop << EOL
[Desktop Entry]
Name=Markdown Previewer
Exec=/usr/bin/nemas-markdown-previewer
Icon=text-markdown
Type=Application
EOL

cp json_formatter_gui.py nemas-utils-pkg/usr/bin/nemas-json-formatter
chmod +x nemas-utils-pkg/usr/bin/nemas-json-formatter
cat > nemas-utils-pkg/usr/share/applications/nemas-json-formatter.desktop << EOL
[Desktop Entry]
Name=JSON Formatter
Exec=/usr/bin/nemas-json-formatter
Icon=text-x-script
Type=Application
EOL

cp case_converter_gui.py nemas-utils-pkg/usr/bin/nemas-case-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-case-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-case-converter.desktop << EOL
[Desktop Entry]
Name=Case Converter
Exec=/usr/bin/nemas-case-converter
Icon=format-text-capitalize
Type=Application
EOL

# --- Batch 3 (10 utilities) ---
cp lorem_ipsum_gui.py nemas-utils-pkg/usr/bin/nemas-lorem-ipsum
chmod +x nemas-utils-pkg/usr/bin/nemas-lorem-ipsum
cat > nemas-utils-pkg/usr/share/applications/nemas-lorem-ipsum.desktop << EOL
[Desktop Entry]
Name=Lorem Ipsum Generator
Exec=/usr/bin/nemas-lorem-ipsum
Icon=applications-utilities
Type=Application
EOL

cp hex_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-hex-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-hex-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-hex-viewer.desktop << EOL
[Desktop Entry]
Name=Hex Viewer
Exec=/usr/bin/nemas-hex-viewer
Icon=applications-utilities
Type=Application
EOL

cp checksum_gui.py nemas-utils-pkg/usr/bin/nemas-checksum
chmod +x nemas-utils-pkg/usr/bin/nemas-checksum
cat > nemas-utils-pkg/usr/share/applications/nemas-checksum.desktop << EOL
[Desktop Entry]
Name=Checksum Calculator
Exec=/usr/bin/nemas-checksum
Icon=applications-utilities
Type=Application
EOL

cp diff_checker_gui.py nemas-utils-pkg/usr/bin/nemas-diff-checker
chmod +x nemas-utils-pkg/usr/bin/nemas-diff-checker
cat > nemas-utils-pkg/usr/share/applications/nemas-diff-checker.desktop << EOL
[Desktop Entry]
Name=Diff Checker
Exec=/usr/bin/nemas-diff-checker
Icon=document-properties
Type=Application
EOL

cp duplicate_finder_gui.py nemas-utils-pkg/usr/bin/nemas-duplicate-finder
chmod +x nemas-utils-pkg/usr/bin/nemas-duplicate-finder
cat > nemas-utils-pkg/usr/share/applications/nemas-duplicate-finder.desktop << EOL
[Desktop Entry]
Name=Duplicate File Finder
Exec=/usr/bin/nemas-duplicate-finder
Icon=system-search
Type=Application
EOL

cp empty_folder_deleter_gui.py nemas-utils-pkg/usr/bin/nemas-empty-folder-deleter
chmod +x nemas-utils-pkg/usr/bin/nemas-empty-folder-deleter
cat > nemas-utils-pkg/usr/share/applications/nemas-empty-folder-deleter.desktop << EOL
[Desktop Entry]
Name=Empty Folder Deleter
Exec=/usr/bin/nemas-empty-folder-deleter
Icon=user-trash
Type=Application
EOL

cp image_converter_gui.py nemas-utils-pkg/usr/bin/nemas-image-converter
chmod +x nemas-utils-pkg/usr/bin/nemas-image-converter
cat > nemas-utils-pkg/usr/share/applications/nemas-image-converter.desktop << EOL
[Desktop Entry]
Name=Image Converter
Exec=/usr/bin/nemas-image-converter
Icon=multimedia-photo-viewer
Type=Application
EOL

cp audio_player_gui.py nemas-utils-pkg/usr/bin/nemas-audio-player
chmod +x nemas-utils-pkg/usr/bin/nemas-audio-player
cat > nemas-utils-pkg/usr/share/applications/nemas-audio-player.desktop << EOL
[Desktop Entry]
Name=Audio Player
Exec=/usr/bin/nemas-audio-player
Icon=multimedia-audio-player
Type=Application
EOL

cp video_player_gui.py nemas-utils-pkg/usr/bin/nemas-video-player
chmod +x nemas-utils-pkg/usr/bin/nemas-video-player
cat > nemas-utils-pkg/usr/share/applications/nemas-video-player.desktop << EOL
[Desktop Entry]
Name=Video Player
Exec=/usr/bin/nemas-video-player
Icon=multimedia-video-player
Type=Application
EOL

cp pdf_merger_gui.py nemas-utils-pkg/usr/bin/nemas-pdf-merger
chmod +x nemas-utils-pkg/usr/bin/nemas-pdf-merger
cat > nemas-utils-pkg/usr/share/applications/nemas-pdf-merger.desktop << EOL
[Desktop Entry]
Name=PDF Merger
Exec=/usr/bin/nemas-pdf-merger
Icon=application-pdf
Type=Application
EOL

# --- Batch 4 (10 utilities) ---
cp file_encryptor_gui.py nemas-utils-pkg/usr/bin/nemas-file-encryptor
chmod +x nemas-utils-pkg/usr/bin/nemas-file-encryptor
cat > nemas-utils-pkg/usr/share/applications/nemas-file-encryptor.desktop << EOL
[Desktop Entry]
Name=File Encryptor
Exec=/usr/bin/nemas-file-encryptor
Icon=utilities-password
Type=Application
EOL

cp batch_resizer_gui.py nemas-utils-pkg/usr/bin/nemas-batch-resizer
chmod +x nemas-utils-pkg/usr/bin/nemas-batch-resizer
cat > nemas-utils-pkg/usr/share/applications/nemas-batch-resizer.desktop << EOL
[Desktop Entry]
Name=Batch Image Resizer
Exec=/usr/bin/nemas-batch-resizer
Icon=applications-graphics
Type=Application
EOL

cp exif_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-exif-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-exif-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-exif-viewer.desktop << EOL
[Desktop Entry]
Name=EXIF Viewer
Exec=/usr/bin/nemas-exif-viewer
Icon=applications-graphics
Type=Application
EOL

cp file_checksum_gui.py nemas-utils-pkg/usr/bin/nemas-file-checksum
chmod +x nemas-utils-pkg/usr/bin/nemas-file-checksum
cat > nemas-utils-pkg/usr/share/applications/nemas-file-checksum.desktop << EOL
[Desktop Entry]
Name=File Checksum
Exec=/usr/bin/nemas-file-checksum
Icon=applications-utilities
Type=Application
EOL

cp ip_viewer_gui.py nemas-utils-pkg/usr/bin/nemas-ip-viewer
chmod +x nemas-utils-pkg/usr/bin/nemas-ip-viewer
cat > nemas-utils-pkg/usr/share/applications/nemas-ip-viewer.desktop << EOL
[Desktop Entry]
Name=IP Viewer
Exec=/usr/bin/nemas-ip-viewer
Icon=network-wired
Type=Application
EOL

cp port_scanner_gui.py nemas-utils-pkg/usr/bin/nemas-port-scanner
chmod +x nemas-utils-pkg/usr/bin/nemas-port-scanner
cat > nemas-utils-pkg/usr/share/applications/nemas-port-scanner.desktop << EOL
[Desktop Entry]
Name=Port Scanner
Exec=/usr/bin/nemas-port-scanner
Icon=network-wired
Type=Application
EOL

cp whois_lookup_gui.py nemas-utils-pkg/usr/bin/nemas-whois-lookup
chmod +x nemas-utils-pkg/usr/bin/nemas-whois-lookup
cat > nemas-utils-pkg/usr/share/applications/nemas-whois-lookup.desktop << EOL
[Desktop Entry]
Name=WHOIS Lookup
Exec=/usr/bin/nemas-whois-lookup
Icon=network-wired
Type=Application
EOL

cp dns_lookup_gui.py nemas-utils-pkg/usr/bin/nemas-dns-lookup
chmod +x nemas-utils-pkg/usr/bin/nemas-dns-lookup
cat > nemas-utils-pkg/usr/share/applications/nemas-dns-lookup.desktop << EOL
[Desktop Entry]
Name=DNS Lookup
Exec=/usr/bin/nemas-dns-lookup
Icon=network-wired
Type=Application
EOL

cp http_header_gui.py nemas-utils-pkg/usr/bin/nemas-http-header
chmod +x nemas-utils-pkg/usr/bin/nemas-http-header
cat > nemas-utils-pkg/usr/share/applications/nemas-http-header.desktop << EOL
[Desktop Entry]
Name=HTTP Header Viewer
Exec=/usr/bin/nemas-http-header
Icon=network-wired
Type=Application
EOL

cp ping_tool_gui.py nemas-utils-pkg/usr/bin/nemas-ping-tool
chmod +x nemas-utils-pkg/usr/bin/nemas-ping-tool
cat > nemas-utils-pkg/usr/share/applications/nemas-ping-tool.desktop << EOL
[Desktop Entry]
Name=Ping Tool
Exec=/usr/bin/nemas-ping-tool
Icon=network-wired
Type=Application
EOL
