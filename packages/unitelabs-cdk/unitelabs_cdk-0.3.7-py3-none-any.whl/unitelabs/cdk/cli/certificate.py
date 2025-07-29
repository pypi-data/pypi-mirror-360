import pathlib

import click
import dotenv

import sila
from unitelabs.cdk import Config

config = Config()


@click.group()
def certificate() -> None:
    """Handle certificates for TLS encryption."""

    dotenv.load_dotenv()


@certificate.command()
@click.option(
    "--uuid",
    type=str,
    default=config.sila_server.get("uuid", None),
    required=True,
    help="The SiLA server's uuid.",
)
@click.option(
    "--host",
    type=str,
    default=lambda: config.sila_server.get("host", "0.0.0.0"),
    help="The SiLA server's host address.",
)
@click.option(
    "--target",
    "-t",
    type=str,
    default=".",
    help="The output directory in which to store the certificate files.",
)
def generate(uuid: str, host: str, target: str) -> None:
    """Generate a new self-signed certificate according to the SiLA 2 specification."""
    key, cert = sila.server.generate_certificate(uuid, host)

    directory = pathlib.Path(target)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "cert.pem").write_bytes(cert)
    (directory / "key.pem").write_bytes(key)


if __name__ == "__main__":
    certificate()
