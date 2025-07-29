import dataclasses
import inspect
import typing
import warnings

import sila

from .. import utils


def define_error(exception: typing.Union[Exception, type[Exception]]) -> type[sila.DefinedExecutionError]:
    """
    Convert an exception into a defined execution error.

    Args:
      exception: The exception class or instance to convert.

    Returns:
      A DefinedExecutionError object with the parsed information from the exception.
    """

    if not inspect.isclass(exception):
        exception = exception.__class__

    if issubclass(exception, sila.DefinedExecutionError):
        return exception

    display_name = utils.to_display_name(exception.__name__)
    identifier = display_name.replace(" ", "")
    description = inspect.getdoc(exception) or ""

    return sila.DefinedExecutionError.create(identifier=identifier, display_name=display_name, description=description)


@dataclasses.dataclass
class DefinedExecutionError(Exception):
    """A defined execution error."""

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        msg = "Using `sila.DefinedExecutionError` is deprecated, please directly inherit from `Exception`."
        warnings.warn(msg, stacklevel=2)

    def __init__(self, *args, identifier: str = "", display_name: str = "", description: str = "", **kwargs):
        pass
