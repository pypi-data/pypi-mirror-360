import collections.abc
import dataclasses
import inspect

import typing_extensions as typing

import sila
from sila.server import Native, SiLAError, UndefinedExecutionError

from ..common import Dataclass
from ..common.errors import define_error
from ..data_types import Any
from ..data_types.convert_data_type import from_sila

if typing.TYPE_CHECKING:
    from ..common import Decorator, Feature

T = typing.TypeVar("T", bound=Any)


@dataclasses.dataclass
class Metadatum(typing.Generic[T], Dataclass):
    """
    Base class for metadata.

    Args:
      identifier: The identifier of the metadata.
      display_name: The display name of the metadata.
      description: The description of the metadata.
    """

    _affects: typing.ClassVar[set[str]] = set()
    _metadatum: typing.ClassVar[typing.Optional[type[sila.server.Metadata]]] = None

    def __init_subclass__(
        cls,
        /,
        *,
        identifier: typing.Optional[str] = None,
        display_name: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        errors: typing.Optional[collections.abc.Sequence[type[Exception]]] = None,
    ) -> None:
        super().__init_subclass__(identifier=identifier, display_name=display_name, name=name)

        cls._affects = set()
        cls._errors: list[type[Exception]] = list(errors or [])

    @typing.override
    @classmethod
    def attach(cls, feature: "Feature") -> type[sila.server.Metadata]:
        super().attach(feature)

        if cls._identifier in feature.metadata:
            cls._metadatum = typing.cast(type[sila.server.Metadata], feature.metadata[cls._identifier])

            return cls._metadatum

        cls._metadatum = sila.server.Metadata.create(
            identifier=cls._identifier,
            display_name=cls._name,
            description=cls._description,
            errors={Error.identifier: Error for error in cls._errors if (Error := define_error(error))},
            data_type=cls._infer_data_type(feature),
            affects=list(cls._affects),
            function=cls._intercept,
            feature=feature,
        )
        return cls._metadatum

    @classmethod
    async def _intercept(cls, value: Native) -> None:
        """Intercept method execution."""

        try:
            await cls.from_native(value).intercept()
        except SiLAError:
            raise
        except Exception as error:
            if type(error) in cls._errors:
                raise define_error(error)(str(error)) from None

            msg = f"{error.__class__.__name__}: {error}"
            raise UndefinedExecutionError(msg) from error

    @classmethod
    def _infer_metadata(cls, decorator: "Decorator") -> tuple[str, list[type["Metadatum"]]]:
        from .metadata import Metadata

        signature = inspect.signature(decorator._function)

        parameter: str = ""
        metadata: list[type["Metadatum"]] = []

        for param in signature.parameters.values():
            if (
                typing.get_origin(param.annotation) is typing.Annotated
                and (args := typing.get_args(param.annotation))
                and args[0] is Metadata
            ):
                parameter = param.name

                for arg in args[1:]:
                    if not issubclass(arg, Metadatum):
                        msg = (
                            f"Expected instance of `Metadatum` for metadata annotation, "
                            f"received '{arg.__name__}' for parameter '{param.name}'."
                        )
                        raise ValueError(msg)

                    if not decorator._handler:
                        raise RuntimeError

                    arg._affects.add(decorator._handler.fully_qualified_identifier)
                    if arg._metadatum:
                        arg._metadatum.affects = [
                            *arg._metadatum.affects,
                            decorator._handler.fully_qualified_identifier,
                        ]
                    metadata.append(arg)

                break

        return parameter, metadata

    @classmethod
    def from_native(cls, value: Native) -> typing.Self:
        """
        Convert a SiLA metadata value to this counterpart.

        Args:
          value: The value to parse.

        Returns:
          A new instance of this metadatum with the given value.
        """

        if cls._metadatum and issubclass(cls._metadatum.data_type, sila.Structure):
            return cls(**from_sila(value, cls._metadatum.data_type, cls._metadatum.feature))  # type: ignore

        return cls(value)  # type: ignore

    @property
    def _feature(self) -> "Feature":
        """The feature this metadata is registered with."""

        if not self._metadatum or not isinstance(self._metadatum.feature, Feature):
            raise RuntimeError

        return self._metadatum.feature

    async def intercept(self) -> None:
        """Intercept method execution."""
