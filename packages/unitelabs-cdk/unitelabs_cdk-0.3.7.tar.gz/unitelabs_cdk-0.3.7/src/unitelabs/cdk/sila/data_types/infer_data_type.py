import dataclasses
import datetime
import inspect

import typing_extensions as typing

from sila.server import (
    Any,
    Binary,
    Boolean,
    Constrained,
    DataType,
    Date,
    Element,
    Integer,
    List,
    Native,
    Real,
    String,
    Structure,
    Time,
    Timestamp,
    Void,
)

from .. import utils
from ..common import Feature
from .custom_data_type import CustomDataType


def infer(annotation: type, feature: Feature) -> type[DataType]:
    """
    Infer the SiLA data type from a given python type annotation.

    Args:
      annotation: The python type annotation.
      feature: The feature.

    Returns:
      The corresponding SiLA data type.
    """

    if annotation == inspect._empty:
        return Void

    origin = typing.get_origin(annotation) or annotation

    if origin is None:
        return Void
    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        return Constrained.create(data_type=infer(args[0], feature), constraints=list(args[1:]))
    if origin is typing.Union and annotation is Native:
        return Any

    if issubclass(origin, type(None)):
        return Void
    if issubclass(origin, CustomDataType):
        return origin.attach(feature)
    if dataclasses.is_dataclass(origin):
        docs = utils.parse_docs(inspect.getdoc(origin))
        fields = dataclasses.fields(origin)

        elements: dict[str, Element] = {}
        fields_by_identifier: dict[str, str] = {}
        for index, field in enumerate(fields):
            field_display_name = utils.humanize(field.name)
            field_identifier = field_display_name.replace(" ", "")
            fields_by_identifier[field_identifier] = field.name
            elements[field.name] = Element(
                identifier=field_identifier,
                display_name=field_display_name,
                description=docs.get("parameter", [])[index].get("default", ""),
                data_type=infer(field.type, feature),
            )

        return Structure.create(elements=elements, name=origin.__name__)

    if issubclass(origin, DataType):
        return origin
    if issubclass(origin, bool):
        return Boolean
    if issubclass(origin, int):
        return Integer
    if issubclass(origin, float):
        return Real
    if issubclass(origin, str):
        return String
    if issubclass(origin, bytes):
        return Binary
    if issubclass(origin, datetime.datetime):
        return Timestamp
    if issubclass(origin, datetime.date):
        return Date
    if issubclass(origin, datetime.time):
        return Time
    if issubclass(origin, list):
        arg = typing.get_args(annotation)
        if not arg:
            msg = f"Unable to identify SiLA type from annotation '{annotation}'"
            raise TypeError(msg)

        return List.create(data_type=infer(arg[0], feature))

    msg = f"Unable to identify SiLA type from annotation '{annotation}'"
    raise TypeError(msg)
