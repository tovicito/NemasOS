import os
import json
import hashlib
import subprocess
import shlex
from datetime import datetime, timezone

# --- CONFIGURACIÓN ---
OUTPUT_FILENAME = "packages.json"
# Lista de archivos a ignorar en el directorio raíz
IGNORE_LIST = {
    'LICENSE',
    'README.md',
    OUTPUT_FILENAME,
    '.gitignore',
    '.github',
}
APP_DESCRIPTION = "NemasOS package"
METADATA_DEFAULT = {"terminal": "true"}
# URL base para las descargas
URL_BASE = "https://raw.githubusercontent.com/tovicito/NemasOS/regular/"

def get_git_version(filepath):
    """Obtiene el número de commits para un archivo y lo devuelve como versión."""
    if not os.path.exists('.git'):
        return "1.0"
    try:
        command = f"git rev-list --count HEAD -- {shlex.quote(filepath)}"
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        count = int(process.stdout.strip())
        return f"{count}.0"
    except Exception as e:
        print(f"No se pudo obtener la versión de git para {filepath}: {e}. Usando 1.0 por defecto.")
        return "1.0"

def get_sha256(filepath):
    """Calcula el hash SHA256 de un archivo."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    """Función principal para construir y actualizar el package.json."""
    repo_name = os.environ.get("GITHUB_REPOSITORY", "local/test-repo")
    last_updated = datetime.now(timezone.utc).isoformat()

    packages = {}
    # Escanea archivos en el directorio raíz
    root_files = [f for f in os.listdir('.') if os.path.isfile(f) and f not in IGNORE_LIST]

    for filename in root_files:
        name_no_ext, extension = os.path.splitext(filename)
        
        package_data = {
            "version": get_git_version(filename),
            "description": APP_DESCRIPTION,
            "download_url": f"{URL_BASE}{filename}",
            "sha256": get_sha256(filename),
            "extension": extension,
            "metadata": METADATA_DEFAULT
        }
        packages[name_no_ext] = package_data

    new_package_file_data = {
        "repository_name": repo_name,
        "last_updated": last_updated,
        "packages": packages
    }

    try:
        with open(OUTPUT_FILENAME, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Compara solo los paquetes y el nombre del repo para ver si hay cambios,
    # ignorando last_updated que siempre cambia.
    if existing_data.get("packages") != new_package_file_data.get("packages") or \
       existing_data.get("repository_name") != new_package_file_data.get("repository_name"):
        print(f"{OUTPUT_FILENAME} está desactualizado. Actualizando...")
        with open(OUTPUT_FILENAME, 'w') as f:
            json.dump(new_package_file_data, f, indent=4)
        print(f"{OUTPUT_FILENAME} actualizado con éxito.")
    else:
        print(f"{OUTPUT_FILENAME} ya está al día.")

if __name__ == "__main__":
    main()