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
