#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_if_available(cmd: list[str]) -> None:
    exe = shutil.which(cmd[0])
    if not exe:
        return
    subprocess.run([exe, *cmd[1:]], check=False)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: post_install.py <prefix> <datadir>", file=sys.stderr)
        return 1

    prefix, datadir = sys.argv[1], sys.argv[2]
    share_dir = Path(prefix) / datadir

    schema_dir = share_dir / 'glib-2.0' / 'schemas'
    if schema_dir.is_dir() and any(schema_dir.glob('*.gschema.xml')):
        run_if_available(['glib-compile-schemas', str(schema_dir)])

    icons_dir = share_dir / 'icons' / 'hicolor'
    if icons_dir.is_dir():
        run_if_available(['gtk-update-icon-cache', '-qtf', str(icons_dir)])

    applications_dir = share_dir / 'applications'
    if applications_dir.is_dir():
        run_if_available(['update-desktop-database', str(applications_dir)])

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
