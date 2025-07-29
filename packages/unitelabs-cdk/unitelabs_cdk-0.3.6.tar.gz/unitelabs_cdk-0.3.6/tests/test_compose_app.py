import asyncio
import collections.abc
import signal
import unittest.mock

import pytest

from unitelabs.cdk.compose_app import compose_app, signal_handler
from unitelabs.cdk.connector import Connector


class TestComposeApp:
    @pytest.fixture
    async def connector(self):
        with (
            unittest.mock.patch("sila.server.Server", spec=True),
            unittest.mock.patch("sila.server.Discovery", spec=True),
            unittest.mock.patch("sila.server.CloudServer", spec=True),
        ):
            yield Connector()

    # Compose app from function
    async def test_compose_app_from_function(self, connector: Connector):
        async def app_factory() -> Connector:
            return connector

        app = await compose_app(create_app=app_factory)

        assert app == connector

    # Compose app from async function
    async def test_compose_app_from_async_function(self, connector: Connector):
        async def app_factory() -> Connector:
            return connector

        app = await compose_app(create_app=app_factory)

        assert app == connector

    # Compose app from generator
    async def test_compose_app_from_generator(self, connector: Connector):
        def app_factory() -> collections.abc.Generator[Connector, None, None]:
            yield connector

        app = await compose_app(create_app=app_factory)

        assert app == connector

    # Compose app from generator sets shutdown handler
    async def test_compose_app_from_generator_sets_shutdown_handler(self, connector: Connector):
        shutdown_handler = unittest.mock.Mock()

        def app_factory() -> collections.abc.Generator[Connector, None, None]:
            yield connector
            shutdown_handler()

        app = await compose_app(create_app=app_factory)

        shutdown_handler.assert_not_called()

        await app.start()
        await app.stop()

        shutdown_handler.assert_called_once_with()

    # Compose app from generator sets shutdown handler with multple yields
    async def test_compose_app_from_generator_sets_shutdown_handler_with_multiple_yields(self, connector: Connector):
        shutdown_handler = unittest.mock.Mock()

        def app_factory() -> collections.abc.Generator[Connector, None, None]:
            yield connector
            yield connector
            yield connector
            shutdown_handler()

        app = await compose_app(create_app=app_factory)

        shutdown_handler.assert_not_called()

        await app.start()
        await app.stop()

        shutdown_handler.assert_called_once_with()

    # Compose app from async generator
    async def test_compose_app_from_async_generator(self, connector: Connector):
        async def app_factory() -> collections.abc.AsyncGenerator[Connector, None]:
            yield connector

        app = await compose_app(create_app=app_factory)

        assert app == connector

    # Compose app from generator sets shutdown handler
    async def test_compose_app_from_async_generator_sets_shutdown_handler(self, connector: Connector):
        shutdown_handler = unittest.mock.Mock()

        async def app_factory() -> collections.abc.AsyncGenerator[Connector, None]:
            yield connector
            shutdown_handler()

        app = await compose_app(create_app=app_factory)

        shutdown_handler.assert_not_called()

        await app.start()
        await app.stop()

        shutdown_handler.assert_called_once_with()

    # Compose app from generator sets shutdown handler
    async def test_compose_app_from_async_generator_sets_async_shutdown_handler(self, connector: Connector):
        shutdown_handler = unittest.mock.AsyncMock()

        async def app_factory() -> collections.abc.AsyncGenerator[Connector, None]:
            yield connector
            await shutdown_handler()

        app = await compose_app(create_app=app_factory)

        shutdown_handler.assert_not_awaited()

        await app.start()
        await app.stop()

        shutdown_handler.assert_awaited_once_with()

    # Fails to create app from invalid factory
    async def test_fails_create_app_from_invalid_factory(self):
        with pytest.raises(
            ValueError,
            match=r"Invalid `create_app`: 'Hello, World!'. Provide a callable function that returns a Connector.",
        ):
            await compose_app(
                create_app="Hello, World!",  # type: ignore
            )

    # Fails to create app from generator without yields
    async def test_fails_create_app_from_generator_without_yields(self):
        def app_factory() -> collections.abc.Generator[Connector, None, None]:
            yield from []

        with pytest.raises(ValueError, match=r"Unable to create app: `create_app` did not yield a value."):
            await compose_app(create_app=app_factory)

    # Fails to create app from async generator without yields
    async def test_fails_create_app_from_async_generator_without_yields(self):
        async def app_factory() -> collections.abc.AsyncGenerator[Connector, None]:
            for value in []:
                yield value

        with pytest.raises(ValueError, match=r"Unable to create app: `create_app` did not yield a value."):
            await compose_app(create_app=app_factory)


class TestSignalHandler:
    async def test_signal_handler_exists_with_signum(self):
        app = unittest.mock.Mock(_shutdown=asyncio.Event())

        signal_handler(signum=signal.SIGINT, app=app)

        assert app._shutdown.is_set()
