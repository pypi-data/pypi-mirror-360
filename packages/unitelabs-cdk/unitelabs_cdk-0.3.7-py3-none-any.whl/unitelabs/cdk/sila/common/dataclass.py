import dataclasses
import inspect
import warnings
import weakref

import typing_extensions as typing

from sila.server import DataType, Element, Feature, Structure

from .. import utils


@dataclasses.dataclass
class Dataclass:
    """Base class for dataclass based SiLA annotations."""

    _identifier: typing.ClassVar[str] = ""
    _name: typing.ClassVar[str] = ""
    _description: typing.ClassVar[str] = ""

    def __init_subclass__(
        cls,
        /,
        *,
        identifier: typing.Optional[str] = None,
        display_name: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
    ) -> None:
        super().__init_subclass__()

        if display_name is not None:
            msg = "Using `display_name` is deprecated, use `name` instead."
            warnings.warn(msg, stacklevel=2)
            name = display_name

        cls._name = name or utils.to_display_name(cls.__name__)
        cls._identifier = identifier or cls._name.replace(" ", "")
        cls._description = utils.parse_docs(inspect.getdoc(cls)).get("default", "")
        cls._feature: typing.Optional["Feature"] = None

    @classmethod
    def attach(cls, feature: "Feature") -> None:
        """
        Create and attach a dataclass to the `feature`.

        Args:
          feature: The `Feature` to which the dataclass will be attached.
        """

        cls._feature = weakref.proxy(feature)

    @classmethod
    def _infer_data_type(cls, feature: Feature) -> type[DataType]:
        docs = utils.parse_docs(inspect.getdoc(cls))

        from ..data_types.infer_data_type import infer

        fields = dataclasses.fields(cls)
        data_type: type[DataType]

        if len(fields) == 0:
            msg = (
                f"Could not detect any fields on '{cls._identifier}'. "
                "Did you forget to annotated your data type definition with `@dataclasses.dataclass`?"
            )
            raise ValueError(msg)
        if len(fields) == 1 and utils.humanize(fields[0].name).replace(" ", "") == cls._identifier:
            data_type = infer(fields[0].type, feature)
        else:
            elements: dict[str, Element] = {}
            for index, field in enumerate(fields):
                field_display_name = utils.humanize(field.name)
                field_identifier = field_display_name.replace(" ", "")
                parameter = docs.get("parameter", [])
                elements[field.name] = Element(
                    identifier=field_identifier,
                    display_name=field_display_name,
                    description=parameter[index].get("default", "") if len(parameter) > index else "",
                    data_type=infer(field.type, feature),
                )
            data_type = Structure.create(elements=elements, name=cls.__name__)

        return data_type
