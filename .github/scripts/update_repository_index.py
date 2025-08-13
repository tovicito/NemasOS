import os
import json
import hashlib
import subprocess
import shlex
from datetime import datetime, timezone

# --- Configuration ---
OUTPUT_FILENAME = "index.json"
IGNORE_LIST = {
    'LICENSE',
    'README.md',
    OUTPUT_FILENAME,
    '.gitignore',
    '.github',
}
APP_DESCRIPTION = "NemasOS package"
METADATA_DEFAULT = {"terminal": "true"}
URL_BASE = "https://raw.githubusercontent.com/tovicito/NemasOS/regular/"

def get_git_version(filepath):
    """Gets the number of commits for a file and returns it as a version string."""
    if not os.path.exists('.git'):
        return "1.0"
    try:
        command = f"git rev-list --count HEAD -- {shlex.quote(filepath)}"
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        count = int(process.stdout.strip())
        return f"{count}.0"
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        print(f"Could not determine git version for {filepath}: {e}. Defaulting to 1.0.")
        return "1.0"

def get_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    """Main function to build and update the repository index file."""
    repo_name = os.environ.get("GITHUB_REPOSITORY", "local/test-repo")
    last_updated = datetime.now(timezone.utc).isoformat()

    packages = {}
    root_files = [f for f in os.listdir('.') if os.path.isfile(f) and f not in IGNORE_LIST]

    for filename in root_files:
        name_no_ext, extension = os.path.splitext(filename)
        filepath = os.path.join('.', filename)

        package_data = {
            "version": get_git_version(filepath),
            "description": APP_DESCRIPTION,
            "download_url": f"{URL_BASE}{filename}",
            "sha256": get_sha256(filepath),
            "extension": extension,
            "metadata": METADATA_DEFAULT
        }
        packages[name_no_ext] = package_data

    # Create the final repository index object
    new_index_data = {
        "repository_name": repo_name,
        "last_updated": last_updated,
        "packages": packages
    }

    # Read the existing index file to compare
    try:
        with open(OUTPUT_FILENAME, 'r') as f:
            existing_index_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_index_data = {}

    # We need to compare smartly, ignoring the last_updated field
    # as it will always change.
    existing_packages = existing_index_data.get("packages", {})
    new_packages = new_index_data.get("packages", {})

    if existing_packages != new_packages or existing_index_data.get("repository_name") != new_index_data.get("repository_name"):
        print(f"{OUTPUT_FILENAME} is outdated. Updating...")
        with open(OUTPUT_FILENAME, 'w') as f:
            json.dump(new_index_data, f, indent=4)
        print(f"{OUTPUT_FILENAME} updated successfully.")
    else:
        print(f"{OUTPUT_FILENAME} is already up-to-date. No changes needed.")

if __name__ == "__main__":
    main()
