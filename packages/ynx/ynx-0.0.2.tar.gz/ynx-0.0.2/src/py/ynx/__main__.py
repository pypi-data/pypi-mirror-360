import click
from ynx.cli import develop


@click.group()
def cli():
    pass


cli.add_command(develop.cli, name="develop")

if __name__ == "__main__":
    cli()

