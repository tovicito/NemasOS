import json
import os

# Files to ignore in the root directory
IGNORE_FILES = [
    'LICENSE',
    'README.md',
    'package.json',
    '.gitignore',
    'update_apps.py', # The script itself
    '.DS_Store',
]

# Github-related files are in a directory, so they won't be picked up by listdir + isfile
# but let's be explicit.
IGNORE_DIRS = [
    '.git',
    '.github',
]

def get_root_files():
    """Get a list of files in the root directory, excluding ignored files."""
    root_files = []
    for f in os.listdir('.'):
        if os.path.isfile(os.path.join('.', f)) and f not in IGNORE_FILES:
            root_files.append(f)
    return sorted(root_files)

def update_package_json(apps):
    """Update package.json with the list of apps."""
    with open('package.json', 'r+') as f:
        data = json.load(f)
        # Only update if the list of apps has changed
        if data.get('apps') != apps:
            data['apps'] = apps
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
            print("Updated package.json")
            return True
        else:
            print("No changes needed in package.json")
            return False

if __name__ == "__main__":
    apps = get_root_files()
    update_package_json(apps)
