# CLI Dependency Graph

Statically analyze and visualize the structure of Python CLI apps built with Click or Typer.

## Features
- Detects `click.Group`, `click.command`, and Typer apps (`Typer()`) via static AST parsing (no code execution)
- CLI commands:
  - `scan <path>`: Discover command tree
  - `show`: Print ASCII tree
  - `export --format {dot,svg}`: Save graph file (planned)
- Renders CLI structure as ASCII (terminal) or DOT/SVG (export)

## Installation

```sh
pip install .
```

## Usage

### 1. Scan a Python CLI app

```sh
python -m cli_dependency_graph scan example_click_app.py
```

### 2. Show the discovered CLI structure

```sh
python -m cli_dependency_graph show
```

### 3. (Optional) Export the CLI graph

```sh
python -m cli_dependency_graph export --format dot --output cli_graph.dot
```

## Example CLI App

```python
import click

@click.group()
def cli():
    pass

@cli.command()
def hello():
    """Say hello"""
    print("Hello!")

@cli.command()
def goodbye():
    """Say goodbye"""
    print("Goodbye!")

if __name__ == "__main__":
    cli()
```

## Development

- Source code: `src/cli_dependency_graph/`
- Tests: `tests/unit/`

### Run tests

```sh
pytest
```

## Requirements
- Python 3.9+
- [Typer](https://typer.tiangolo.com/) >= 0.12.3
- [Click](https://click.palletsprojects.com/) >= 8.1.7
- [rich](https://rich.readthedocs.io/) >= 13.7.1
- [graphviz](https://graphviz.readthedocs.io/) >= 0.20.3
- [pytest](https://docs.pytest.org/) (for tests)

---
Contributions welcome!