import inspect

import typing_extensions as typing

import sila

from .. import utils
from ..commands import IntermediateResponses, Parameters, Responses
from ..common import Decorator
from ..common.errors import define_error

if typing.TYPE_CHECKING:
    from ..common import Feature


class ObservableCommand(Decorator):
    """
    Any command for which observing the progress of execution is possible or does make sense.

    Args:
      name: Human readable name for the command. By default, this is
        automatically inferred by the name of the decorated method.
      identifier: Unique identifier of the command. By default, this
        equals the `name` without spaces.
      errors: A list of defined errors that may occur during command
        execution.

    Examples:
      Convert a feature method into an observable command:
      >>> class MyFeature(sila.Feature):
      ...   @sila.ObservableCommand
      ...   @sila.Response("Response A")
      ...   @sila.Response("Response B")
      ...   async def my_command(self, param_a: str, param_b: int) -> tuple[str, int]:
      ...     \"\"\"
      ...     Describe what your command does.
      ...     .. parameter:: Describe the purpose of param_a.
      ...     .. parameter:: Describe the purpose of param_b.
      ...     .. return:: The input parameter directly returned.
      ...     .. return:: Describe the purpose of param_b.
      ...     \"\"\"
      ...     return param_a, param_b
    """

    @typing.override
    def attach(self, feature: "Feature") -> sila.server.ObservableCommand:
        super().attach(feature)

        docs = utils.parse_docs(inspect.getdoc(self._function))

        self._name = self._name or utils.humanize(self._function.__name__)
        self._identifier = self._identifier or self._name.replace(" ", "")
        self._description = docs.get("default", "")

        self._parameters = Parameters.from_signature(feature, self._function).elements
        self._responses = Responses.from_signature(feature, self._function).elements
        self._intermediate_responses = IntermediateResponses.from_signature(feature, self._function).elements

        return sila.server.ObservableCommand(
            identifier=self._identifier,
            display_name=self._name,
            description=self._description,
            function=self.execute,
            errors={Error.identifier: Error for error in self._errors if (Error := define_error(error))},
            parameters=self._parameters,
            responses=self._responses,
            intermediate_responses=self._intermediate_responses,
            feature=feature,
        )
