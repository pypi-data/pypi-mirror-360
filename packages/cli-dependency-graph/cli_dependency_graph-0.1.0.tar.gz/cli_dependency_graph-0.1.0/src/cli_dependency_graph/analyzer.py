"""
analyzer.py: Static analysis for Click/Typer commands using ast
"""
import ast
import os

def scan_for_commands(path: str) -> list[dict[str, str]]:
    """Scan a file or directory for top-level Click/Typer commands."""
    commands: list[dict[str, str]] = []
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    commands.extend(_scan_file(os.path.join(root, file)))
    else:
        commands.extend(_scan_file(path))
    return commands

def _scan_file(filepath: str) -> list[dict[str, str]]:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=filepath)
    except Exception:
        return []
    found: list[dict[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for deco in node.decorator_list:
                if (
                    isinstance(deco, ast.Call)
                    and isinstance(deco.func, ast.Attribute)
                    and deco.func.attr == "command"
                ):
                    found.append({"name": node.name, "file": filepath})
        if isinstance(node, ast.Assign):
            # Detect Typer() app assignment (very basic)
            if (
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "Typer"
            ):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        found.append({"name": target.id, "file": filepath, "type": "typer_app"})
    return found
