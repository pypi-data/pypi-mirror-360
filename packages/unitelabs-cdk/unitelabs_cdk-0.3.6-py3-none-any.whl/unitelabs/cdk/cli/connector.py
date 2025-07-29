import click
import dotenv

from .start import start
from .sync import sync

CONTEXT_SETTINGS = dict(show_default=True)


@click.group(context_settings=CONTEXT_SETTINGS)
def connector() -> click.Group:
    """Connector commands."""
    dotenv.load_dotenv()


connector.add_command(start)
connector.add_command(sync)

if __name__ == "__main__":
    connector()
