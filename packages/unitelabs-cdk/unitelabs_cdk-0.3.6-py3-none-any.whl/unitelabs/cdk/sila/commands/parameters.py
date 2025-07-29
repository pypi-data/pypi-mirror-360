import collections.abc
import dataclasses
import inspect

import typing_extensions as typing

from sila.server import Element, Feature

from .. import utils
from .decorator import Decorator, parse_structure

PARAMETERS_ATTRIBUTE = "__parameters"
DOCUMENTATION_KEYWORD = "parameter"


@dataclasses.dataclass
class Parameter(Decorator):
    """
    A decorator class for defining parameters of an SiLA endpoint.

    Attributes:
      name: The name of the decorated parameter.
      description: A description providing more details about the decorated parameter.

    Examples:
      Option 1: Using decorators to define parameters for an endpoint method:
      >>> @Parameter(name="Parameter A", description="A string parameter.")
      >>> @Parameter(name="Parameter B", description="An integer parameter.")
      >>> def example_handler(self, /, param_a: str, param_b: int):
      >>>     ...

      Option 2: Using a docstring to define parameters:
      >>> def example_handler(self, /, param_a: str, param_b: int):
      >>>     \"\"\"
      >>>     .. parameter:: A string parameter.
      >>>       :name: Parameter A
      >>>     .. parameter:: An integer parameter.
      >>>       :name: Parameter B
      >>>     \"\"\"
      >>>     ...
    """

    def __call__(self, function: collections.abc.Callable) -> collections.abc.Callable:  # noqa: D102
        responses = getattr(function, PARAMETERS_ATTRIBUTE, [])
        setattr(function, PARAMETERS_ATTRIBUTE, [self, *responses])

        return function


@dataclasses.dataclass
class Parameters:
    """Represents a SiLA structure containing parameters, inferred from a callable's signature."""

    elements: dict[str, Element] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_signature(
        cls,
        feature: Feature,
        function: collections.abc.Callable,
    ) -> typing.Self:
        """
        Infer and construct parameter elements based on function signature annotations, decorators, and documentation.

        Args:
          feature: The SiLA feature context.
          function: The function to analyze for parameter elements.

        Returns:
          A Parameters object containing the inferred parameter elements.

        Raises:
          TypeError: If any function parameter is missing an annotation or the given annotation is not SiLA compliant.
        """

        signature = inspect.signature(function)
        docs = utils.parse_docs(inspect.getdoc(function)).get(DOCUMENTATION_KEYWORD, [])
        decorators: list[Parameter] = getattr(function, PARAMETERS_ATTRIBUTE, [])

        annotations: typing.Iterable[type] = []
        parameters = list(cls.__get_parameters(signature))
        for i, parameter in enumerate(cls.__get_parameters(signature)):
            if parameter.annotation is inspect.Parameter.empty:
                msg = f"Missing type annotation for parameter '{parameter.name}' in {function.__qualname__}."
                raise TypeError(msg)

            if i < len(decorators):
                decorators[i].name = decorators[i].name or utils.humanize(parameter.name)
            else:
                decorators.append(Parameter(utils.humanize(parameter.name)))

            annotations.append(parameter.annotation)

        structure = parse_structure(
            Parameters,
            feature,
            function,
            annotations,
            decorators,
            docs,
        )

        return cls({parameter.name: element for element, parameter in zip(structure.values(), parameters)})

    @classmethod
    def __get_parameters(cls, signature: inspect.Signature) -> typing.Iterable[inspect.Parameter]:
        """
        Get the relevant parameters from a given signature.

        Args:
          signature: The signature to extract parameters from.

        Returns:
          Parameters that are positional or keyword excluding 'self' and 'cls'.
        """

        return (
            parameter
            for parameter in signature.parameters.values()
            if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and parameter.name not in ("self", "cls")
        )

    @classmethod
    def get_mapping(cls, elements: dict[str, Element], function: collections.abc.Callable) -> dict[str, str]:
        """
        Map structure elements to function parameters based on their names.

        Args:
          elements: The structure elements to map.
          function: The function whose parameters are being mapped.

        Returns:
          A mapping of structure element identifiers to function parameter names.
        """

        signature = inspect.signature(function)
        return {
            element.identifier: parameter.name
            for element, parameter in zip(elements.values(), cls.__get_parameters(signature))
        }
