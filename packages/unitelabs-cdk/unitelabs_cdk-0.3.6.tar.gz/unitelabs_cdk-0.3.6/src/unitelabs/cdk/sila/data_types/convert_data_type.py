import collections.abc
import dataclasses
import datetime

import typing_extensions as typing

import sila
import sila.datetime
from sila import (
    Binary,
    Boolean,
    Constrained,
    Custom,
    DataType,
    Date,
    Integer,
    List,
    Native,
    Real,
    String,
    Structure,
    Time,
    Timestamp,
)

if typing.TYPE_CHECKING:
    from ..common.feature import Feature
    from .custom_data_type import CustomDataType


Any = typing.Union[
    str,
    int,
    float,
    bytes,
    bool,
    sila.datetime.date,
    sila.datetime.time,
    sila.datetime.datetime,
    collections.abc.Sequence["Any"],
    collections.abc.Mapping[str, "Any"],
    "CustomDataType",
]


def to_sila(
    value: Native,
    data_type: type[DataType],
    feature: "Feature",
) -> sila.Native:
    """
    Convert a CDK native value to a SiLA native value.

    Args:
      value: The native CDK value to convert.
      data_type: The SiLA data type of the message.
      feature: The feature containing custmo data types.

    Returns:
      The converted SiLA native value.
    """

    if issubclass(data_type, Custom):
        custom = feature._custom_data_types[data_type.identifier]
        if not isinstance(value, custom):
            msg = f"Expected value to be of type '{custom.__name__}', received {type(value)}."
            raise ValueError(msg)

        values = dataclasses.asdict(value)

        if custom._custom and issubclass(custom._custom.data_type, Structure):
            return to_sila(values, data_type.data_type, feature)

        field = dataclasses.fields(custom)[0]
        item = dataclasses.asdict(value).get(field.name, None)

        if item is None:
            msg = f"Missing item '{field.name}' in values {values}."
            raise ValueError(msg)

        return to_sila(item, data_type.data_type, feature)

    if issubclass(data_type, Structure):
        if not isinstance(value, tuple) and not isinstance(value, dict):
            value = (value,)

        if isinstance(value, tuple):
            values = {}
            for index, name in enumerate(data_type.elements.keys()):
                if len(value) < index:
                    msg = f"Expected {len(data_type.elements)} elements in tuple, received {value}."
                    raise ValueError(msg)
                values[name] = value[index]

            value = values

        if not isinstance(value, dict):
            msg = f"Expected value to be of type 'dict', received {type(value)}."
            raise ValueError(msg)

        return {name: to_sila(value[name], element.data_type, feature) for name, element in data_type.elements.items()}

    if issubclass(data_type, List):
        if not isinstance(value, list):
            msg = f"Expected value to be of type 'list', received {type(value)}."
            raise ValueError(msg)

        return [to_sila(item, data_type.data_type, feature) for item in value]

    if issubclass(data_type, Constrained):
        return to_sila(value, data_type.data_type, feature)

    return value


@typing.overload
def from_sila(
    value: dict[str, sila.Native], data_type: type[Structure], feature: "Feature"
) -> collections.abc.Mapping[str, Any]: ...


@typing.overload
def from_sila(value: list[sila.Native], data_type: type[List], feature: "Feature") -> collections.abc.Sequence[Any]: ...


@typing.overload
def from_sila(value: sila.Native, data_type: type[Constrained], feature: "Feature") -> Any: ...


@typing.overload
def from_sila(value: sila.Native, data_type: type[Custom], feature: "Feature") -> "CustomDataType": ...


@typing.overload
def from_sila(value: Native, data_type: type[sila.Any], feature: "Feature") -> Any: ...


@typing.overload
def from_sila(value: str, data_type: type[String], feature: "Feature") -> str: ...


@typing.overload
def from_sila(value: int, data_type: type[Integer], feature: "Feature") -> int: ...


@typing.overload
def from_sila(value: float, data_type: type[Real], feature: "Feature") -> float: ...


@typing.overload
def from_sila(value: bytes, data_type: type[Binary], feature: "Feature") -> bytes: ...


@typing.overload
def from_sila(value: bool, data_type: type[Boolean], feature: "Feature") -> bool: ...


@typing.overload
def from_sila(value: datetime.date, data_type: type[Date], feature: "Feature") -> sila.datetime.date: ...


@typing.overload
def from_sila(value: datetime.time, data_type: type[Time], feature: "Feature") -> sila.datetime.time: ...


@typing.overload
def from_sila(value: datetime.datetime, data_type: type[Timestamp], feature: "Feature") -> sila.datetime.datetime: ...


@typing.overload
def from_sila(
    value: sila.Native, data_type: type[DataType], feature: "Feature"
) -> typing.Union[dict[str, Any], list[Any], Any]: ...


def from_sila(
    value: sila.Native, data_type: type[DataType], feature: "Feature"
) -> typing.Union[collections.abc.Mapping[str, Any], collections.abc.Sequence[Any], Any]:
    """
    Convert a SiLA native value to a CDK native value.

    Args:
      value: The native SiLA value to convert.
      data_type: The SiLA data type of the message.
      feature: The feature containing custmo data types.

    Returns:
      The converted CDK native value.
    """

    if issubclass(data_type, Custom):
        custom = feature._custom_data_types[data_type.identifier]

        if custom._custom and issubclass(custom._custom.data_type, Structure):
            if not isinstance(value, dict):
                msg = f"Expected value to be of type 'dict', received {type(value)}."
                raise ValueError(msg)

            return custom(**from_sila(value, custom._custom.data_type, feature))

        field = dataclasses.fields(custom)[0]
        return custom(**{field.name: from_sila(value, custom._custom.data_type, feature)})

    if issubclass(data_type, Structure):
        if not isinstance(value, dict):
            msg = f"Expected value to be of type 'dict', received {type(value)}."
            raise ValueError(msg)

        return {
            name: from_sila(value[name], element.data_type, feature) for name, element in data_type.elements.items()
        }

    if issubclass(data_type, List):
        if not isinstance(value, list):
            msg = f"Expected value to be of type 'list', received {type(value)}."
            raise ValueError(msg)

        return [from_sila(item, data_type.data_type, feature) for item in value]

    if issubclass(data_type, Constrained):
        return from_sila(value, data_type.data_type, feature)

    if issubclass(data_type, Date):
        if isinstance(value, sila.datetime.date):
            return value

        if isinstance(value, datetime.date):
            return sila.datetime.date(year=value.year, month=value.month, day=value.day)

        msg = f"Expected value to be of type 'date', received {type(value)}."
        raise ValueError(msg)

    if issubclass(data_type, Time):
        if isinstance(value, sila.datetime.time):
            return value

        if isinstance(value, datetime.time):
            return sila.datetime.time(
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
                tzinfo=value.tzinfo,
            )

        msg = f"Expected value to be of type 'time', received {type(value)}."
        raise ValueError(msg)

    if issubclass(data_type, Timestamp):
        if isinstance(value, sila.datetime.datetime):
            return value

        if isinstance(value, datetime.datetime):
            return sila.datetime.datetime(
                year=value.year,
                month=value.month,
                day=value.day,
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
                tzinfo=value.tzinfo,
            )

        msg = f"Expected value to be of type 'time', received {type(value)}."
        raise ValueError(msg)

    if issubclass(data_type, String):
        if not isinstance(value, str):
            msg = f"Expected value to be of type 'str', received {type(value)}."
            raise ValueError(msg)

        return value

    if issubclass(data_type, Integer):
        if not isinstance(value, int):
            msg = f"Expected value to be of type 'int', received {type(value)}."
            raise ValueError(msg)

        return value

    if issubclass(data_type, Real):
        if not isinstance(value, float):
            msg = f"Expected value to be of type 'float', received {type(value)}."
            raise ValueError(msg)

        return value

    if issubclass(data_type, Binary):
        if not isinstance(value, bytes):
            msg = f"Expected value to be of type 'bytes', received {type(value)}."
            raise ValueError(msg)

        return value

    if issubclass(data_type, Boolean):
        if not isinstance(value, bool):
            msg = f"Expected value to be of type 'bool', received {type(value)}."
            raise ValueError(msg)

        return value

    if issubclass(data_type, sila.Any):
        return value

    msg = f"Received unknown data type {data_type.__name__}."
    raise ValueError(msg)
