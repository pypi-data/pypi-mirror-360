import collections.abc
import functools
import inspect
import warnings
import weakref

import typing_extensions as typing

from sila import Element, MetadataIdentifier, Structure
from sila.server import CommandExecution, Handler, Native, SiLAError, UndefinedExecutionError

from ..data_types import from_sila, to_sila
from ..metadata import Metadatum
from .errors import define_error

if typing.TYPE_CHECKING:
    from .feature import Feature


class Decorator:
    """Base class for decorator based SiLA annotations."""

    def __init__(
        self,
        /,
        *,
        identifier: typing.Optional[str] = None,
        display_name: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        errors: typing.Optional[collections.abc.Sequence[type[Exception]]] = None,
    ) -> None:
        if display_name is not None:
            msg = "Using `display_name` is deprecated, use `name` instead."
            warnings.warn(msg, stacklevel=2)
            name = display_name

        self._identifier = identifier or ""
        self._name = name or ""
        self._description = ""
        self._parameters: dict[str, Element] = {}
        self._responses: dict[str, Element] = {}
        self._intermediate_responses: dict[str, Element] = {}
        self._handler: typing.Optional[Handler] = None
        self._metadata: tuple[str, list[type[Metadatum]]] = ("", [])
        self._errors: list[type[Exception]] = list(errors or [])
        self._function: collections.abc.Callable = lambda: ...
        self._feature: typing.Optional["Feature"] = None

    def __call__(self, function: collections.abc.Callable) -> collections.abc.Callable:
        """Call the decorator to wrap the given method."""

        self._function = weakref.proxy(function)
        setattr(function, "__handler", self)

        return function

    def attach(self, feature: "Feature") -> None:
        """
        Create and attach a handler to the `feature`.

        Args:
          feature: The `Feature` to which the handler will be attached.
        """

        self._feature = weakref.proxy(feature)

    async def execute(self, metadata: dict[MetadataIdentifier, Native], **parameters) -> Native:
        """
        Execute a given function with the provided keyword arguments.

        Args:
          metadata: Additional metadata sent from client to server.

        Returns:
          The result of the `function` execution.

        Raises:
          DefinedExecutionError: If the error type is in the list of defined errors.
          UndefinedExecutionError: If an unexpected error occurs during execution.
        """

        if not self._feature:
            raise RuntimeError

        try:
            function = self._with_metadata(self._function, metadata)
            function = self._with_parameters(function, parameters)

            responses = await self._execute(function)

            return to_sila(responses, Structure.create(self._responses), self._feature)
        except SiLAError:
            raise
        except Exception as error:
            import traceback

            traceback.print_exc()
            if type(error) in self._errors:
                raise define_error(error)(str(error)) from None

            msg = f"{error.__class__.__name__}: {error}"
            raise UndefinedExecutionError(msg) from error

    async def _execute(self, function: collections.abc.Callable) -> Native:
        responses = function()

        if inspect.isawaitable(responses):
            responses = await responses

        if responses is None:
            return {}

        return responses

    def _with_metadata(
        self, function: collections.abc.Callable, metadata: dict[MetadataIdentifier, Native]
    ) -> collections.abc.Callable:
        if self._metadata[0]:
            function = functools.partial(
                function,
                **{
                    self._metadata[0]: {
                        metadatum: metadatum.from_native(metadata[metadatum._metadatum.fully_qualified_identifier()])
                        for metadatum in self._metadata[1]
                        if metadatum._metadatum
                    }
                },
            )

        return function

    def _with_parameters(
        self,
        function: collections.abc.Callable,
        parameters: collections.abc.Mapping[str, typing.Union[Native, CommandExecution]],
    ) -> collections.abc.Callable:
        if not self._feature:
            raise RuntimeError

        parameters = dict(parameters)
        command_execution = parameters.pop("command_execution", None)
        parameters = typing.cast(dict[str, Native], parameters)

        if command_execution and isinstance(command_execution, CommandExecution):
            from ..commands.intermediate import Intermediate
            from ..commands.status import Status

            signature = inspect.signature(function)
            for param in signature.parameters.values():
                annotation = typing.get_origin(param.annotation) or param.annotation
                if annotation is Status:
                    function = functools.partial(function, **{param.name: Status(command_execution)})
                if annotation is Intermediate:
                    function = functools.partial(
                        function, **{param.name: Intermediate(command_execution, self._intermediate_responses)}
                    )

        return functools.partial(
            function, **from_sila(parameters, Structure.create(elements=self._parameters), self._feature)
        )
