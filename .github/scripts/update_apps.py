import os
import json
import hashlib
import subprocess
import shlex

# --- Configuration ---
# Files and directories to ignore in the root.
IGNORE_LIST = {
    'LICENSE',
    'README.md',
    'package.json',
    '.gitignore',
    '.github',  # Ignore the whole directory
    # Add any other files or directories to ignore
}
# Static description for all apps.
APP_DESCRIPTION = "App oficial de NemasOS"
# URL pattern for downloads. {repo_owner}, {repo_name}, {branch}, and {filename} will be replaced.
# The user specified a hardcoded URL, so we will use that.
URL_BASE = "https://raw.githubusercontent.com/tovicito/NemasOS/regular/"

def get_git_version(filepath):
    """
    Gets the number of commits for a file and returns it as a version string.
    e.g., 3 commits -> "3.0"
    """
    if not os.path.exists('.git'):
        # Running in an environment without git history, return default version.
        return "1.0"
    try:
        # Use rev-list to count commits for the file.
        command = f"git rev-list --count HEAD -- {shlex.quote(filepath)}"
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        count = int(process.stdout.strip())
        return f"{count}.0"
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        # Fallback for any git error or if git is not installed.
        print(f"Could not determine git version for {filepath}: {e}. Defaulting to 1.0.")
        return "1.0"

def get_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    """
    Main function to update the package.json file.
    """
    root_files = [f for f in os.listdir('.') if os.path.isfile(f) and f not in IGNORE_LIST]

    new_apps_list = []
    for filename in root_files:
        name, extension = os.path.splitext(filename)
        filepath = os.path.join('.', filename)

        app_data = {
            "name": name,
            "version": get_git_version(filepath),
            "description": APP_DESCRIPTION,
            "download_url": f"{URL_BASE}{filename}",
            "sha256": get_sha256(filepath),
            "extension": extension
        }
        new_apps_list.append(app_data)

    # Sort the list alphabetically by name for consistency
    new_apps_list.sort(key=lambda x: x['name'])

    # Read the current package.json and check if an update is needed
    try:
        with open('package.json', 'r') as f:
            package_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, create a default structure
        package_data = {"apps": []}

    # Compare old and new list of apps
    if package_data.get('apps') != new_apps_list:
        print("package.json is outdated. Updating...")
        package_data['apps'] = new_apps_list
        with open('package.json', 'w') as f:
            json.dump(package_data, f, indent=2)
        print("package.json updated successfully.")
    else:
        print("package.json is already up-to-date. No changes needed.")

if __name__ == "__main__":
    main()
