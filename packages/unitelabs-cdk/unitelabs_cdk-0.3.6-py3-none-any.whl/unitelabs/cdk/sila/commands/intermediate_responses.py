import collections.abc
import dataclasses
import inspect

import typing_extensions as typing

from sila.server import Element, Feature

from .. import utils
from .decorator import Decorator, parse_structure
from .intermediate import Intermediate

INTERMEDIATE_RESPONSES_ATTRIBUTE = "__intermediate_responses"


@dataclasses.dataclass
class IntermediateResponse(Decorator):
    '''
    A decorator class for defining intermediate responses of an SiLA endpoint.

    Attributes:
      name: The name of the decorated response.
      description: A description providing more details about the decorated response.

    Examples:
      Option 1: Using decorators to define intermediate responses for an endpoint method:
      >>> @Response(name="Intermediate Response A", description="A string intermediate response.")
      >>> @Response(name="Intermediate Response B", description="An integer intermediate response.")
      >>> def example_handler(self, /, *, intermediate: Intermediate[str, int]):
      >>>     ...

      Option 2: Using a docstring to define intermediate responses:
      >>> def example_handler(self, /, *, intermediate: Intermediate[str, int]):
      >>>     """
      >>>     .. yield:: A string intermediate response.
      >>>       :name: Intermediate Response A
      >>>     .. yield:: An integer intermediate response.
      >>>       :name: Intermediate Response B
      >>>     """
      >>>     ...
    '''

    def __call__(self, function: collections.abc.Callable) -> collections.abc.Callable:  # noqa: D102
        intermediate_responses = getattr(function, INTERMEDIATE_RESPONSES_ATTRIBUTE, [])
        setattr(function, INTERMEDIATE_RESPONSES_ATTRIBUTE, [self, *intermediate_responses])

        return function


@dataclasses.dataclass
class IntermediateResponses:
    """Represents a SiLA structure containing intermediate response elements, inferred from a callable's signature."""

    elements: dict[str, Element] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_signature(
        cls,
        feature: Feature,
        function: collections.abc.Callable,
    ) -> typing.Self:
        """
        Infer and construct intermediate response elements.

        Construction is based on function signature annotations, decorators, and documentation.

        Args:
          feature: The SiLA feature context.
          function: The function to analyze for intermediate response elements.

        Returns:
          An IntermediateResponses object containing the inferred intermediate response elements.

        Raises:
          TypeError: If the function's `intermediate` parameter type annotation is missing or invalid.
        """

        signature = inspect.signature(function)
        docs = utils.parse_docs(inspect.getdoc(function)).get("yield", [])
        decorators: list[IntermediateResponse] = getattr(function, INTERMEDIATE_RESPONSES_ATTRIBUTE, [])

        intermediate_parameter = signature.parameters.get("intermediate", None)

        if intermediate_parameter is None:
            return cls({})

        if typing.get_origin(intermediate_parameter.annotation) is not Intermediate:
            msg = f"Missing type annotation for parameter 'intermediate' in {function.__qualname__}."
            raise TypeError(msg)

        intermediate_annotation = typing.get_args(intermediate_parameter.annotation)[0]
        intermediate_annotation = (
            intermediate_annotation
            if issubclass(typing.get_origin(intermediate_annotation) or intermediate_annotation, tuple)
            else tuple[intermediate_annotation]
        )
        annotations = typing.get_args(intermediate_annotation)

        return cls(
            parse_structure(
                IntermediateResponses,
                feature,
                function,
                annotations,
                decorators,
                docs,
            )
        )
