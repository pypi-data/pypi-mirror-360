import asyncio
import collections.abc
import contextlib
import logging
import typing
import weakref

import packaging.version

from sila import framework, server

from . import sila
from .config import Config
from .features.core.sila_service import SiLAService

Handler = collections.abc.Callable[..., typing.Union[typing.Any, typing.Awaitable[typing.Any]]]

T = typing.TypeVar("T", bound=sila.Feature)


class Connector:
    """Main app."""

    def __init__(self, config: typing.Optional[dict] = None):
        self.__config = Config.model_validate(config or {}, strict=False)

        self._ready = asyncio.Event()
        self._shutdown = asyncio.Event()
        self._shutdown_handlers: list[Handler] = []

        _parsed_version = packaging.version.parse(self.config.sila_server.get("version", "0.0.0"))
        self.config.sila_server["version"] = ".".join(str(v) for v in _parsed_version.release)

        self.config.sila_server["tls"] = self.config.sila_server.get("tls", False)
        self.config.cloud_server_endpoint["tls"] = self.config.cloud_server_endpoint.get("tls", False)

        options = {
            # The period (in milliseconds) after which a keepalive ping is sent on the transport.
            "grpc.keepalive_time_ms": 60 * 1000,
            # The amount of time (in milliseconds) the sender of the keepalive ping waits for an
            # acknowledgement. If it does not receive an acknowledgment within this time, it will
            # close the connection.
            "grpc.keepalive_timeout_ms": 3 * 60 * 1000,
            # If set to 1 (0 : false; 1 : true), allows keepalive pings to be sent even if there
            # are no calls in flight.
            "grpc.keepalive_permit_without_calls": 0,
            # How many pings can the client send before needing to send a data/header frame.
            "grpc.http2.max_pings_without_data": 0,
        } | self.config.cloud_server_endpoint.get("options", {})
        self.config.cloud_server_endpoint["options"] = framework.ChannelOptions(**options)

        self._sila_server = server.Server(self.config.sila_server)
        self._discovery = server.Discovery(self._sila_server)
        self._cloud_server = server.CloudServer(self.config.cloud_server_endpoint)
        self._cloud_server.context = self._sila_server

        self.register(SiLAService())

    async def start(self) -> None:
        """Start the connector and all related services."""

        await asyncio.gather(
            asyncio.create_task(self._sila_server.start()),
            asyncio.create_task(self._discovery.start()),
            asyncio.create_task(self._cloud_server.start()),
        )
        self._ready.set()

    async def stop(self) -> None:
        """Stop the connector and all related services."""

        for shutdown_handler in self._shutdown_handlers:
            with contextlib.suppress(Exception):
                if asyncio.iscoroutinefunction(shutdown_handler):
                    await shutdown_handler()
                else:
                    shutdown_handler()

        await asyncio.gather(
            self._sila_server.stop(grace=5),
            self._cloud_server.stop(grace=5),
            self._discovery.stop(),
        )

    async def wait_for_ready(self) -> None:
        """Wait until the connector is ready."""

        await self._ready.wait()
        self._ready.clear()

    async def wait_for_termination(self) -> None:
        """Wait until the connector is terminated."""

        await self._shutdown.wait()
        self._shutdown.clear()

    def get_feature(self, feature: type[T]) -> T:
        """
        Get the instance of a registered feature by its type.

        Args:
          feature: The type of the feature to receive.

        Returns:
          The feature registered with this connector.

        Raises:
          ValueError: If the given type is invalid or not
            recognized.
        """

        try:
            return next(feat for feat in self._sila_server.features.values() if isinstance(feat, feature))
        except StopIteration:
            msg = ""
            msg = f"Requested unknown feature '{feature.__name__}'."
            raise ValueError(msg) from None

    def register(self, feature: sila.Feature) -> None:
        """Register a new feature to this driver."""

        self.logger.debug("Added feature: %s", feature)
        self._sila_server.register_feature(feature)
        feature._app = weakref.proxy(self)

    @property
    def config(self) -> Config:
        """The configuration."""

        return self.__config

    @property
    def sila_server(self) -> server.Server:
        """The SiLA Server."""

        return self._sila_server

    @property
    def logger(self) -> logging.Logger:
        """A standard Python :class:`~logging.Logger` for the app."""

        return logging.getLogger(__package__)

    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled."""

        return True

    def on_shutdown(self, handler: Handler) -> None:
        """
        Add a shutdown hook to be called in the terminating phase.

        This will be in response to an explicit call to `app.stop()` or
        upon receipt of system signals such as SIGINT, SIGTERM or SIGHUP.

        Args:
          handler: The method to be called on shutdown.

        Raises:
          TypeError: If the `handler` argument is not callable.
        """

        if not callable(handler):
            msg = "The `handler` argument must be callable."
            raise TypeError(msg)

        self._shutdown_handlers.append(handler)

    def off_shutdown(self, handler: Handler) -> None:
        """
        Remove a previously added shutdown hook.

        Args:
          handler: The handler to be removed from the shutdown hooks.
        """

        with contextlib.suppress(ValueError):
            self._shutdown_handlers.remove(handler)
