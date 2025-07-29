import inspect

import typing_extensions as typing

import sila

from .. import utils
from ..commands import Parameters, Responses
from ..common import Decorator
from ..common.errors import define_error
from ..metadata import Metadatum

if typing.TYPE_CHECKING:
    from ..common import Feature


class UnobservableCommand(Decorator):
    """Any command for which observing the progress of execution is not possible or does not make sense."""

    @typing.override
    def attach(self, feature: "Feature") -> None:
        super().attach(feature)

        docs = utils.parse_docs(inspect.getdoc(self._function))

        self._name = self._name or utils.humanize(self._function.__name__)
        self._identifier = self._identifier or self._name.replace(" ", "")
        self._description = docs.get("default", "")

        self._parameters = Parameters.from_signature(feature, self._function).elements
        self._responses = Responses.from_signature(feature, self._function).elements

        self._handler = sila.server.UnobservableCommand(
            identifier=self._identifier,
            display_name=self._name,
            description=self._description,
            function=self.execute,
            errors={Error.identifier: Error for error in self._errors if (Error := define_error(error))},
            parameters=self._parameters,
            responses=self._responses,
            feature=feature,
        )
        self._metadata = Metadatum._infer_metadata(self)
