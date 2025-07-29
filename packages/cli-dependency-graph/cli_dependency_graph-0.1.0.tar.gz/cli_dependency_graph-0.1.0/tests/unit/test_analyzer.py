import tempfile
import os
from cli_dependency_graph.analyzer import scan_for_commands

def test_scan_for_commands_click():
    code = '''
import click
@click.command()
def foo():
    pass
'''
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        cmds = scan_for_commands(fname)
        assert any(c["name"] == "foo" for c in cmds)
    finally:
        os.remove(fname)

def test_scan_for_commands_typer():
    code = '''
from typer import Typer
app = Typer()
'''
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        cmds = scan_for_commands(fname)
        assert any(c["name"] == "app" and c.get("type") == "typer_app" for c in cmds)
    finally:
        os.remove(fname)
