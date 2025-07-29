from __future__ import annotations

import importlib.resources as pkg_resources
import os
import platform
import subprocess
import sys

from yamlfmt import BIN_NAME


def get_executable_path():
    with pkg_resources.as_file(pkg_resources.files("yamlfmt").joinpath(f"./{BIN_NAME}")) as p:
        executable_path = p

    if platform.system() != "Windows":
        if not os.access(executable_path, os.X_OK):
            current_mode = executable_path.stat().st_mode
            executable_path.chmod(current_mode | 0o111)

    return executable_path


def main():
    executable_path = get_executable_path()
    result = subprocess.run([executable_path] + sys.argv[1:], check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
