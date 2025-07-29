import collections.abc
import inspect

import typing_extensions as typing

import sila
from sila.server import Native

from .. import utils
from ..common import Decorator
from ..common.errors import define_error
from ..data_types import infer
from ..metadata import Metadatum

if typing.TYPE_CHECKING:
    from ..common import Feature


class UnobservableProperty(Decorator):
    """A property describes certain aspects of a SiLA server that do not require an action on the SiLA server."""

    @typing.override
    def attach(self, feature: "Feature") -> None:
        super().attach(feature)

        self._name = self._name or utils.humanize(self._function.__name__.removeprefix("get_"))
        self._identifier = self._identifier or self._name.replace(" ", "")
        self._description = inspect.getdoc(self._function) or ""

        type_hint = inspect.signature(self._function).return_annotation
        data_type = infer(type_hint, feature)

        self._responses = {
            self._identifier: sila.Element(identifier=self._identifier, display_name=self._name, data_type=data_type)
        }

        self._handler = sila.server.UnobservableProperty(
            identifier=self._identifier,
            display_name=self._name,
            description=self._description,
            function=self.execute,
            errors={Error.identifier: Error for error in self._errors if (Error := define_error(error))},
            data_type=data_type,
            feature=feature,
        )
        self._metadata = Metadatum._infer_metadata(self)

    @typing.override
    async def _execute(self, function: collections.abc.Callable) -> Native:
        responses: Native = function()

        if inspect.isawaitable(responses):
            responses = await responses

        return {self._identifier: responses}
