"""
cli.py: Typer CLI entrypoint for cli-dependency-graph
"""
import typer
from .analyzer import scan_for_commands
from .renderer import render_ascii_tree

app = typer.Typer()

# Global state for demo (replace with better state mgmt in real app)
cli_state: dict[str, list[dict[str, str]]] = {"commands": []}

@app.command()
def scan(path: str):
    """Scan a Python file or directory for CLI commands."""
    commands = scan_for_commands(path)
    cli_state["commands"] = commands
    typer.echo(f"Discovered commands: {[c['name'] for c in commands]}")

@app.command()
def show(path: str):
    scan(path)
    """Show the CLI command tree as ASCII."""
    if not cli_state["commands"]:
        typer.echo("No commands found. Run 'scan' first.")
        raise typer.Exit(1)
    typer.echo(render_ascii_tree(cli_state["commands"]))

@app.command()
def export(format: str = typer.Option("dot", help="Format: dot or svg"), output: str = "cli_graph.dot"):
    """Export the CLI graph to DOT or SVG."""
    typer.echo("TODO: Implement export (dot/svg)")

if __name__ == "__main__":
    app()
