import os
import pathlib
import sys
import typing

import pytest
from click.testing import CliRunner

from unitelabs.cdk.cli import TLSConfigurationError

main_file_text = """
import asyncio
from unitelabs.cdk import compose_app
from . import create_app

async def main():
    app = await compose_app(create_app)
    await app.start()

if __name__ == "__main__":
    asyncio.run(main())
"""

init_file_text = """
from unitelabs.cdk import Connector

async def create_app():
    app = Connector(
        {
            "sila_server": {
                "name":  "UniteLabs Example",
                "type": "Example",
                "description": "A UniteLabs SiLA Python Example Server",
                "version": "0.1.0",
                "vendor_url": "https://unitelabs.io/",
                "host": "localhost"

            }
        }
    )
    yield app
"""

cert = """
-----BEGIN CERTIFICATE-----
MIIC/jCCAeagAwIBAgIURXGhJmigNdNvgR3wMdlsv43VhCEwDQYJKoZIhvcNAQEL
BQAwEDEOMAwGA1UEAwwFU2lMQTIwHhcNMjQxMDA5MTMwNDU1WhcNMjUxMDA5MTMw
NDU1WjAQMQ4wDAYDVQQDDAVTaUxBMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC
AQoCggEBAMCSToXHEzV76zHO3pATJ+M3zRqnbZ9KwyGJzWCA7jmZZWkCligW7QgQ
COf8AdOcf5eZawop63HeDDqkuQtAAKwOUiVjLgoPXpu9l9lxDSBo1XfquTIvgNGY
wN7i2W9zQQ0U78iBJ7+xcEbkf9m/s5yyKXGOds1apBVx184Qb2MKnGc2mK6WkRf3
uIBBj/o3JzNlEu040zIok/A/DtRimgoxOipjzbLYRq5xLtod1tpyw1lsQGctfCNi
27bYApcA2UUpy0PG8BUMbT2jkwLTkruKrfx9x4tcHL3PH9s0oXWzijKFw8seAx15
LIhoyjonygZeoKaEAkT2Rv+WzGeUDRsCAwEAAaNQME4wGgYDVR0RBBMwEYIJbG9j
YWxob3N0hwR/AAABMDAGCCsGAQQBg8lXBCQ1YThmZGI3MS1lZTIzLTQ1MmMtODM1
Yy1lMjI0ZGY3YmU5NTAwDQYJKoZIhvcNAQELBQADggEBAF9NbU6GItVjepD1w4UA
2V4UUfcrKdk9xO0FVEF/lRyPoRaoKzO08k5AJ47tmjqqqpijzYXspKta+UEMiAUE
qoCRhgLCvtrAIp7nhsCNw7fyK+i+866q1dyB2VogDbLwxyAj4nxd4o2flWNPaTqr
XgQ9xGuww3Izngr+MGFKsE9CJ7b5emq67lfGQ8UkwvfU2XhcPWPJAyHi2kQPVXFk
UmmzQoqnqELfSNpnd5zUrgdVVtABHZ+rsCJpldU0yO5OQ4pfm+f56VmS2Da2vDZt
GkEfLq/po/VTGOB6bZ1oV+kR+ZHbRpCh0mAQ+OvuUuWOAmuQ30m26nA+w7+VyLux
ht4=
-----END CERTIFICATE-----

"""
key = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwJJOhccTNXvrMc7ekBMn4zfNGqdtn0rDIYnNYIDuOZllaQKW
KBbtCBAI5/wB05x/l5lrCinrcd4MOqS5C0AArA5SJWMuCg9em72X2XENIGjVd+q5
Mi+A0ZjA3uLZb3NBDRTvyIEnv7FwRuR/2b+znLIpcY52zVqkFXHXzhBvYwqcZzaY
rpaRF/e4gEGP+jcnM2US7TjTMiiT8D8O1GKaCjE6KmPNsthGrnEu2h3W2nLDWWxA
Zy18I2LbttgClwDZRSnLQ8bwFQxtPaOTAtOSu4qt/H3Hi1wcvc8f2zShdbOKMoXD
yx4DHXksiGjKOifKBl6gpoQCRPZG/5bMZ5QNGwIDAQABAoIBAE023PFbH2Kkq2uv
TSJr6+R5rW3wkE38xj0eahE14U+LKFRwyxCMEMLY2xlZvMnCyI5a38aVhGiF5lVl
UyUlpp9Wpq2DFSTHgOHlpYt0fxTttBp/LX7n+TkRjNRSFWlQx1adfH/i+bMtTJ3A
ZVtEOJqt/VwhCZXRsFVA7o0bne4R0VZZW/5eDH4nF9JNQsvOo2Qrcx7fRzld4khx
7Y3lbf363RQndONdJ7znPMZMd1RzFWygsjbU8vjcL2rA7bDEHLkqKc6er+RDPTWq
SgnMT2vL/+lzQxuf59JaIBU3nJA02+8jLWjMpRLSbvnNuxV/YN4j9+tzC5ChPm/4
+3HnwBECgYEA/0EtN1hl8SbwEAz+hoVB6pOhjIPOBrKqT/1xRLyPPGt5zlM3vFmc
o60LV5hcWI7dajd4TRc6mYZEYpMkWPY9FQKSANH1WmHwp9rRUwDyTCn6xvza5dk/
cV1ZnvMMjwfKi531NhZQerA4Fg/3CoiToBXIWRBl4+Vhh2Tx1mcUuA8CgYEAwSJE
+nbESRR5rbKEC1Yezc+RuxzhVqIWApOVZx29O6VLMmlL+O1ZiK6Z08YUNNno6otc
Lnhi3I5bv2O5CS4ubUpqtwLuOKKJPLdx8ZBh5aJ/1LVfEmqih58FxzYiZ3+Hfsjy
PaqSwEDp3CcShZ6Tzz8eaeJFaG9k56a659QU7jUCgYAaG2FzirAKhTAChEG4IoMG
agkY5RY6ayWuPr7KB/sic9+mca5+ri+uMfG6CNRRHnOY/IlqYRjWQPxXlLMgAjdn
IbcrLE5K6z+A+4lzUuJ1VcnXdl8xKRIrFyAmeLdtHZ/ivcopuQiMM9/YqdNbmXJ3
6iJusZWqRHjAL1vo0Ow2kwKBgQCNhKTyupA91IkMpCBphiNwP8bTSug7aO2j2azC
MGJ3EDm3qLyInLLcmsQRD7XCvGIVaySS0JfwcUf9R/9QIMzYPI1RqQ4R5deV6/3M
OjXh5F6y6GvPvN93bSj4vkwbdrE8T9ZhJVn/EhHKxb6mtnoshF2uzKR7UBSqQdv2
/8qOeQKBgQDdWqFawsUcMZmq3faoipofg0Gl8pZiKYjVOV5QBz8z2mxxUuHGB3VQ
17kBvR3rnhbyhj/kS0rq7mKib+8K9WjKeZr/ypr1oiOSXKPm5UqZTctFcAqkvgyE
Sz0JRTsDjVBHrdnbVUF6QNh+hqTkqYGMu2RcArnvmMdnQ5D1jMfe0A==
-----END RSA PRIVATE KEY-----

"""


@pytest.fixture
def connectorpkg(tmp_path) -> typing.Generator[typing.Tuple[CliRunner, pathlib.Path], None, None]:
    """
    Yield a fake package for testing with the following directory structure:

    test_package
    ├── __init__.py
    ├── __main__.py
    ├── test_key.pem
    └── test_cert.pem

    __init__.py defines `create_app()`
    __main__.py calls `compose_app()`
    """
    runner = CliRunner()
    tests_path = str(tmp_path.resolve())
    sys.path.append(tests_path)

    with runner.isolated_filesystem(tests_path) as path:
        test_package_path = pathlib.Path(path)
        assert test_package_path.exists()

        test_package_init = test_package_path / "__init__.py"
        test_package_init.touch()
        test_package_init.write_text(init_file_text)

        test_package_main = test_package_path / "__main__.py"
        test_package_main.touch()
        test_package_main.write_text(main_file_text)

        cert_file = test_package_path / "test_cert.pem"
        cert_file.touch()
        cert_file.write_bytes(cert.encode("ascii"))

        key_file = test_package_path / "test_key.pem"
        key_file.touch()
        key_file.write_bytes(key.encode("ascii"))

        yield runner, test_package_path

    os.environ["SILA_SERVER__TLS"] = "false"  # prevent envvar leakage to other tests


@pytest.mark.parametrize(
    "envvars,has_cert,has_key",
    [
        ({"SILA_SERVER__TLS": "true"}, False, False),
        ({"SILA_SERVER__CERT": "test_cert.pem"}, True, False),
        ({"SILA_SERVER__KEY": "test_key.pem"}, False, True),
        ({"SILA_SERVER__TLS": "true", "SILA_SERVER__CERT": "test_cert.pem"}, True, False),
        ({"SILA_SERVER__TLS": "true", "SILA_SERVER__KEY": "test_key.pem"}, False, True),
    ],
)
class TestConnectorStartShouldFail:  # We cannot force CliRunner to exit running process, therefore we can only test unhappy paths.
    # Without setting ENVVARS the default values are set for cert and key which DNE
    def test_tls_default_settings(self, connectorpkg, envvars, has_cert, has_key):
        runner, test_path = connectorpkg

        # update paths in envvars
        for k, v in envvars.items():
            if k != "SILA_SERVER__TLS":
                envvars[k] = str(test_path / v)

        from unitelabs.cdk.cli import connector

        result = runner.invoke(
            connector,
            ["start", "--tls"],
            env=runner.make_env(envvars),
        )
        assert result.exit_code == 1

        key = test_path / envvars.get("SILA_SERVER__KEY", "key.pem")
        cert = test_path / envvars.get("SILA_SERVER__CERT", "cert.pem")

        exc_msg = (
            f"Private key file at {key} does not exist. Specify path with --key."
            if has_cert
            else f"Certificate file at {cert} does not exist. Specify path with --cert. "
        )
        if not has_cert and not has_key:
            exc_msg = f"Certificate file at {cert} does not exist. Specify path with --cert. Private key file at {key} does not exist. Specify path with --key."

        assert isinstance(result.exception, TLSConfigurationError)
        assert result.exception.args[0] == exc_msg

    def test_cert_override_envvars(self, connectorpkg, envvars, has_cert, has_key):
        runner, test_path = connectorpkg

        # update paths in envvars
        for k, v in envvars.items():
            if k != "SILA_SERVER__TLS":
                envvars[k] = str(test_path / v)

        from unitelabs.cdk.cli import connector

        # create fake cert file for use with --cert
        cli_cert = test_path / "cli_cert.pem"
        cli_cert.touch()

        result = runner.invoke(
            connector,
            ["start", "--tls", "--cert", f"{cli_cert}"],
            env=runner.make_env(envvars),  # set envvars in within testing environment
        )

        if not has_key:
            assert result.exit_code == 1
            assert isinstance(result.exception, TLSConfigurationError)

            key = test_path / envvars.get("SILA_SERVER__KEY", "key.pem")
            assert result.exception.args[0] == f"Private key file at {key} does not exist. Specify path with --key."
        else:
            # All required paths provided, fails trying to create TLS connection with invalid file.
            # ValueError("Failed to bind to address 0.0.0.0:0") Invalid cert chain file.
            assert result.exit_code == 1
            assert isinstance(result.exception, RuntimeError)

    def test_key_override_envvars(self, connectorpkg, envvars, has_cert, has_key):
        runner, test_path = connectorpkg

        # update paths in envvars
        for k, v in envvars.items():
            if k != "SILA_SERVER__TLS":
                envvars[k] = str(test_path / v)

        from unitelabs.cdk.cli import connector

        # create fake key file for use with --key
        cli_key = test_path / "cli_key.pem"
        cli_key.touch()

        result = runner.invoke(
            connector,
            ["start", "--tls", "--key", f"{cli_key}"],
            env=runner.make_env(envvars),  # set envvars in within testing environment
        )

        if not has_cert:
            assert result.exit_code == 1
            assert isinstance(result.exception, TLSConfigurationError)

            cert = test_path / envvars.get("SILA_SERVER__CERT", "cert.pem")
            assert result.exception.args[0] == f"Certificate file at {cert} does not exist. Specify path with --cert. "

        else:
            # All required paths provided, fails trying to create TLS connection with invalid file.
            # ValueError("Failed to bind to address 0.0.0.0:0") Invalid cert chain file.
            assert result.exit_code == 1
            assert isinstance(result.exception, RuntimeError)
