import dataclasses

import typing_extensions as typing

from sila.server import Custom

from ..common import Dataclass, Feature


@dataclasses.dataclass
class CustomDataType(Dataclass):
    """A SiLA custom data type definition."""

    @typing.override
    @classmethod
    def attach(cls, feature: Feature) -> type[Custom]:
        super().attach(feature)

        if cls._identifier in feature.data_type_definitions:
            return feature.data_type_definitions[cls._identifier]

        cls._custom = Custom.create(
            identifier=cls._identifier,
            display_name=cls._name,
            description=cls._description,
            data_type=cls._infer_data_type(feature),
            feature=feature,
        )
        feature._custom_data_types[cls._identifier] = cls
        return cls._custom
