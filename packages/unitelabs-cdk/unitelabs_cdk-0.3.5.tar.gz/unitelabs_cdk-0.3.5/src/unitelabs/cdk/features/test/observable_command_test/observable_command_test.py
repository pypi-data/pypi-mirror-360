# ruff: noqa: D205

import asyncio
import datetime

import typing_extensions as typing

from unitelabs.cdk import sila


class ObservableCommandTest(sila.Feature):
    """
    This is a test feature to test observable commands.
    It specifies various observable commands and returns defined answers to validate against.
    """

    def __init__(self):
        super().__init__(originator="org.silastandard", category="test")

    @sila.ObservableCommand()
    @sila.IntermediateResponse(name="Current Iteration")
    @sila.Response(name="Iteration Response")
    async def count(
        self,
        n: int,
        delay: typing.Annotated[
            float, sila.constraints.Unit(label="s", components=[sila.constraints.Unit.Component("Second")])
        ],
        *,
        status: sila.Status,
        intermediate: sila.Intermediate[int],
    ) -> int:
        """
        Count from 0 to N-1 and return the current number as intermediate response.

        .. parameter:: Number to count to
        .. parameter:: The delay for each iteration
        .. yield:: The current number, from 0 to N-1 (excluded).
        .. return:: The last number (N-1)
        """

        for i in range(n):
            status.update(
                progress=i / (n - 1),
                remaining_time=datetime.timedelta(seconds=delay * (n - i - 1)),
            )
            intermediate.send(i)

            await asyncio.sleep(delay)

        return n - 1

    @sila.ObservableCommand()
    @sila.Response(name="Received Value")
    async def echo_value_after_delay(
        self,
        value: int,
        delay: typing.Annotated[
            float, sila.constraints.Unit(label="s", components=[sila.constraints.Unit.Component("Second")])
        ],
        *,
        status: sila.Status,
    ) -> int:
        """
        Echo the given value after the specified delay. The command state must be "waiting" until the delay has passed.

        .. parameter:: The value to echo
        .. parameter:: The delay before the command execution starts
        .. return:: The Received Value
        """

        seconds, rest = divmod(delay, 1)
        for i in range(int(seconds)):
            await asyncio.sleep(1)
            status.update(progress=i / delay, remaining_time=datetime.timedelta(seconds=delay - i))

        await asyncio.sleep(rest)
        return value
