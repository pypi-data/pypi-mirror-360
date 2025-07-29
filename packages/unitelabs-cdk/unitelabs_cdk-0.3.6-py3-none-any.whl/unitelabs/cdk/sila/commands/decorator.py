import collections.abc
import dataclasses
import inspect
import itertools
import warnings

from sila.server import Element, Feature

from ..data_types import infer


@dataclasses.dataclass
class Decorator:
    """
    A base class representing a generic decorator for SiLA endpoints.

    Attributes:
      name: The name of the decorated object such as `Parameter` and `Response`.
      description: A description providing more details about the decorated object.
    """

    name: str = ""
    description: str = ""


def parse_structure(
    factory: type,
    feature: Feature,
    function: collections.abc.Callable,
    annotations: collections.abc.Sequence[type],
    decorators: collections.abc.Sequence["Decorator"],
    docs: collections.abc.Sequence,
) -> dict[str, Element]:
    """
    Parse the structure for parameters or (intermediate) responses by combining annotations, decorators, and docs.

    Args:
      factory: The factory class to generate (Parameters or Responses).
      feature: The SiLA feature context.
      function: The function for which the parameters or responses are parsed.
      annotations: The type annotations of the function parameters or return values.
      decorators: The decorators specifying additional metadata.
      docs: The parsed docstring metadata.

    Returns:
      The resulting structure (Parameters or (Intermediate-)Responses).

    Raises:
      TypeError: If a type cannot be parsed from the annotations.
    """

    if len(docs) > len(annotations):
        warnings.warn_explicit(
            f"More documented items than annotations in {function.__qualname__}, using only the first {len(annotations)}.",  # noqa: E501
            category=UserWarning,
            filename=inspect.getfile(inspect.unwrap(function)),
            lineno=inspect.getsourcelines(inspect.unwrap(function))[1],
        )

    if len(decorators) > len(annotations):
        warnings.warn_explicit(
            f"More decorators than annotations in {function.__qualname__}, using only the first {len(annotations)}.",
            category=UserWarning,
            filename=inspect.getfile(inspect.unwrap(function)),
            lineno=inspect.getsourcelines(inspect.unwrap(function))[1],
        )

    elements: dict[str, Element] = {}
    for index, (annotation, decorator, doc) in enumerate(
        itertools.islice(itertools.zip_longest(annotations, decorators, docs), len(annotations))
    ):
        name = None
        description = ""

        if decorator is not None:
            name = decorator.name or name
            description = decorator.description or description

        if doc is not None:
            name = doc.get("name", name)
            description = description or doc.get("default", description)  # prefer decorator description, if any

        try:
            data_type = infer(annotation, feature)
        except TypeError:
            import traceback

            traceback.print_exc()
            msg = f"Unable to identify SiLA type from annotation '{annotation.__name__}' in {function.__qualname__}."
            raise TypeError(msg) from None

        if name is None:
            name = f"Unnamed {index}"
            warnings.warn_explicit(
                f"No name found for {factory.__name__} {index} in {function.__qualname__}, defaulting to '{name}'.",
                category=UserWarning,
                filename=inspect.getfile(inspect.unwrap(function)),
                lineno=inspect.getsourcelines(inspect.unwrap(function))[1],
            )

        element = Element(
            identifier=name.replace(" ", ""),
            display_name=name,
            description=description,
            data_type=data_type,
        )
        elements[element.identifier] = element

    return elements
