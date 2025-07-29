[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Tests](https://github.com/G-Lauz/python-project-template/actions/workflows/test.yml/badge.svg)](https://github.com/G-Lauz/python-project-template/actions/workflows/test.yml)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)

# CLIpy
A python package that eases the creation of command line interface tools. It's a simple wrapper around the `argparse` module that simplifies the creation of CLI tools.

## Features

- Simplifies the creation of CLI tools.
- Supports `argparse` arguments.
- `@clipy.App` decorator: Adds a command-line parser with usage and description.
- `@clipy.Command` decorator: Adds a command to the command-line parser.
- `@clipy.Option` decorator: Adds an option to the command-line parser.

## Usage

```python
import clipy


@clipy.App(usage="mypackage <command> [options] [arg] ...", description="A CLI app")
@clipy.Option("option1", help="A global option")
@clipy.Command("command1", usage="mypackage command1 [options] [arg] ...", description="A descritpion", options=[
    clipy.Option("option2", help="Help message"),
    clipy.Option("flag", help="Help message", action="store_true")
])
@clipy.Command("command2", usage="mypackage command2 [options] [arg] ...", description="A descritpion", options=[
    clipy.Option("option3", help="Help message", required=True)
])
def main(command: clipy.CommandDefinition):
    print(f"Command: {command.name}")
    print("Options:")
    for key, value in command.options.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()  # pylint: disable=missing-kwoa
```

Then enjoy your CLI tool:

```bash
python script.py --help
python script.py --global-option1 arg1 --global-option2 arg2
python script.py command1 --help
python script.py --global-option command1 --option1 arg1
```

## Installation
```bash
pip install clipyx
```
From Github:
```bash
pip install git+https://github.com/G-Lauz/clipy.git@v0.1.0-pre0
```

Or clone the repository and install it manually:
```bash
git clone https://github.com/G-Lauz/clipy.git
cd clipy
pip install .
```
