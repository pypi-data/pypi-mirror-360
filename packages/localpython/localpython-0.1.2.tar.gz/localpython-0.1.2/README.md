# localpython
**Run Python scripts using your local virtual environment — without activating it manually.**

`localpython` is a simple cross-platform CLI tool that automatically detects your local `.venv`, `venv`, or `env` folder and uses its Python interpreter to run a script — just like a smart alias.


## Features

- ✅ Runs scripts using `.venv/Scripts/python` or `bin/python`
- ✅ No need to activate virtual environments manually
- ✅ Supports arguments, flags, and quoted paths
- ✅ Automatically searches parent directories with `-p`
- ✅ Includes `--version`, `--which`, `--help`


## Installation

Install via `pip`:

```bash
pip install localpython
```

## Usage

### Basic

```bash
localpython script.py
```

### Pass arguments to your script

```bash
localpython script.py --input file.json --debug true
```

### Search in parent directories for a venv

```bash
localpython -p script.py --some arg
```

### Show path to the interpreter

```bash
localpython --which
```

### Show version

```bash
localpython --version
```

## Example

Given a project:

```
myproject/
├── .venv/
├── script.py
```

And a command:

```bash
localpython script.py --run fast
```

This tool will automatically run:

```bash
./.venv/Scripts/python script.py --run fast
```

(Or the Unix equivalent if on Linux/Mac)



## License

This project is licensed under the [MIT License](LICENSE).



## Author

Created by [Yali Ach](https://github.com/YaliAch)