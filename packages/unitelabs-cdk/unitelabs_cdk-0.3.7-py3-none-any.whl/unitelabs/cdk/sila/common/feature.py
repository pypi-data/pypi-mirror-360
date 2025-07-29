import collections.abc
import dataclasses
import functools
import inspect
import warnings

import typing_extensions as typing

import sila
from sila.server import Server

from .. import utils
from ..metadata import Metadatum
from .decorator import Decorator

if typing.TYPE_CHECKING:
    from ...connector import Connector
    from ..data_types import CustomDataType


@dataclasses.dataclass
class Feature(sila.framework.Feature):
    """
    A SiLA feature describes a specific behavior of a SiLA server.

    Args:
      identifier: The identifier of the feature.
      name: The display name of the feature.
    """

    def __init__(
        self,
        *args,
        identifier: typing.Optional[str] = None,
        display_name: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        metadata: typing.Optional[collections.abc.Sequence[type[Metadatum]]] = None,
        **kwargs,
    ):
        if display_name is not None:
            msg = "Using `display_name` is deprecated, use `name` instead."
            warnings.warn(msg, stacklevel=2)
            name = display_name

        name = name or utils.to_display_name(self.__class__.__name__)
        identifier = identifier or name.replace(" ", "")
        description = description or next((inspect.getdoc(cls) for cls in inspect.getmro(type(self))), "") or ""

        super().__init__(*args, identifier=identifier, display_name=name, description=description, **kwargs)

        for metadatum in metadata or []:
            metadatum.attach(self).add_to_feature(self)

        self._custom_data_types: dict[str, type["CustomDataType"]] = {}

        self._app: typing.Optional["Connector"] = None

        for cls in inspect.getmro(type(self)):
            for name, function in inspect.getmembers(cls, predicate=inspect.isfunction):
                if (handler := getattr(function, "__handler", None)) and isinstance(handler, Decorator):
                    method = getattr(self, name).__func__
                    method = functools.partial(method, self)
                    handler._function = functools.wraps(function)(method)

                    handler.attach(self)

    @property
    def app(self) -> "Connector":
        """The connector app this feature is registered with."""

        if not self._app:
            raise RuntimeError

        return self._app

    @property
    def server(self) -> Server:
        """The server this feature is registered with."""

        if not isinstance(self.context, Server):
            raise RuntimeError

        return self.context
