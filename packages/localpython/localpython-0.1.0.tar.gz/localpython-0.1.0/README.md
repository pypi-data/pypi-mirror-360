# localpython

`localpython` is a simple CLI tool that runs Python scripts using the local project's virtual environment without requiring manual activation.

## Features

- 🧠 Automatically finds `.venv`, `venv`, or `env`
- 📁 Supports searching parent directories with `-p`
- ⚡ Fast, clean, cross-platform

## Usage

```bash
localpython script.py --your-args
localpython -p script.py --search