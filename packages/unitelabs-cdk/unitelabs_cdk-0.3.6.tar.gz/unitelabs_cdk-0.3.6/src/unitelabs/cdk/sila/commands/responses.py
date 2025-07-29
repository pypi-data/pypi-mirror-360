import collections.abc
import dataclasses
import inspect

import typing_extensions as typing

from sila.server import Element, Feature

from .. import utils
from .decorator import Decorator, parse_structure

RESPONSES_ATTRIBUTE = "__responses"
DOCUMENTATION_KEYWORD = "return"


@dataclasses.dataclass
class Response(Decorator):
    """
    A decorator class for defining responses of an SiLA endpoint.

    Attributes:
      name: The name of the decorated response.
      description: A description providing more details about the decorated response.

    Examples:
      Option 1: Using decorators to define responses for an endpoint method:
      >>> @Response(name="Response A", description="A string response.")
      >>> @Response(name="Response B", description="An integer response.")
      >>> def example_handler(self) -> tuple[str, int]:
      >>>     ...

      Option 2: Using a docstring to define responses:
      >>> def example_handler(self) -> tuple[str, int]:
      >>>     \"\"\"
      >>>     .. return:: A string response.
      >>>       :name: Response A
      >>>     .. return:: An integer response.
      >>>       :name: Response B
      >>>     \"\"\"
      >>>     ...
    """

    def __call__(self, function: collections.abc.Callable) -> collections.abc.Callable:  # noqa: D102
        responses = getattr(function, RESPONSES_ATTRIBUTE, [])
        setattr(function, RESPONSES_ATTRIBUTE, [self, *responses])

        return function


@dataclasses.dataclass
class Responses:
    """Represents a SiLA structure containing response elements, inferred from a callable's signature."""

    elements: dict[str, Element] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_signature(
        cls,
        feature: Feature,
        function: collections.abc.Callable,
    ) -> typing.Self:
        """
        Infer and construct response elements based on function signature annotations, decorators, and documentation.

        Args:
          feature: The SiLA feature context.
          function: The function to analyze for response elements.

        Returns:
          A Responses object containing the inferred response elements.

        Raises:
          TypeError: If the function's return type annotation is invalid.
        """

        signature = inspect.signature(function)
        docs = utils.parse_docs(inspect.getdoc(function)).get(DOCUMENTATION_KEYWORD, [])
        decorators: list[Response] = getattr(function, RESPONSES_ATTRIBUTE, [])

        if signature.return_annotation is None or signature.return_annotation is inspect.Parameter.empty:
            return cls({})

        origin = typing.get_origin(signature.return_annotation) or signature.return_annotation
        return_annotation = (
            signature.return_annotation
            if origin is not typing.Annotated and issubclass(origin, tuple)
            else tuple[signature.return_annotation]
        )
        annotations = typing.get_args(return_annotation)

        return cls(
            parse_structure(
                Responses,
                feature,
                function,
                annotations,
                decorators,
                docs,
            )
        )
