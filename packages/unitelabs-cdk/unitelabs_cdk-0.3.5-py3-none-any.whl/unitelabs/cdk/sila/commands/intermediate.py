import typing
import weakref

from sila.server import CommandExecution, Element

T = typing.TypeVar("T")


class Intermediate(typing.Generic[T]):
    """A class representing an intermediate response in a command execution."""

    def __init__(self, command_execution: CommandExecution, responses: dict[str, Element]):
        self.command_execution: CommandExecution = weakref.proxy(command_execution)
        self.responses = responses

    def send(self, responses: T, /) -> None:
        """Send an intermediate response."""

        if responses is None:
            return

        result = {}
        responses = [responses] if not isinstance(responses, tuple) else responses
        resps = list(self.responses.values())
        for index, response in enumerate(responses):
            key = resps[index].identifier if index < len(resps) else index
            result[key] = response

        self.command_execution.send_intermediate_responses(result)
