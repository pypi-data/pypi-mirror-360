import os
import sys
from pathlib import Path
import subprocess

VERSION = "0.1.0"

def find_venv_path(search_parents=False):
    current = Path.cwd()
    search_dirs = [current] + list(current.parents) if search_parents else [current]
    for directory in search_dirs:
        for folder in [".venv", "venv", "env"]:
            win = directory / folder / "Scripts" / "python.exe"
            unix = directory / folder / "bin" / "python"
            if win.exists():
                return str(win)
            if unix.exists():
                return str(unix)
    return None

def print_help():
    print(f"""
localpython v{VERSION}
Run Python scripts using the local virtual environment (without activation)

Usage:
  localpython [options] <script> [args...]

Options:
  -p, --search-parent      Search for venv in parent directories
  --which                  Show path to venv Python interpreter
  --version                Show localpython version
  --help                   Show this help message

Examples:
  localpython script.py
  localpython -p script.py --your-script-arg
  localpython --which
""")


def main():
    args = sys.argv[1:]
    search_parents = False

    if not args or "--help" in args:
        print_help()
        return

    if "--version" in args:
        print(f"localpython v{VERSION}")
        return

    if "--which" in args:
        venv = find_venv_path("--search-parent" in args or "-p" in args)
        if venv:
            print(venv)
        else:
            print("No virtual environment found.")
            sys.exit(1)
        return

    if "-p" in args:
        search_parents = True
        args.remove("-p")
    if "--search-parent" in args:
        search_parents = True
        args.remove("--search-parent")

    if not args:
        print("Error: No script provided.\n")
        print_help()
        sys.exit(1)

    script = args[0]
    script_args = args[1:]

    venv_python = find_venv_path(search_parents)
    if not venv_python:
        print("No virtual environment found in current or parent directories.")
        sys.exit(1)

    subprocess.run([venv_python, script] + script_args)

