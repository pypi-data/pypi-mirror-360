import abc

from unitelabs.cdk import sila


class Unstable(sila.DefinedExecutionError):
    """Command understood but timeout for stable reading was reached."""


class Overloaded(sila.DefinedExecutionError):
    """Device in overload range."""


class Underloaded(sila.DefinedExecutionError):
    """Device in underload range."""


class WeighingServiceBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    This feature contains commands and properties used for common functions required when weighing things.

    The feature enables access to the current net weight (stable and dynamic) and the tare weight. Commands for zeroing
    and taring are provided.
    """

    def __init__(self, *args, **kwarg):
        super().__init__(
            originator="io.unitelabs",
            category="weighing",
            version="1.0",
            maturity_level="Draft",
            *args,  # noqa: B026
            **kwarg,
        )

    @abc.abstractmethod
    @sila.ObservableProperty(errors=[Overloaded, Underloaded])
    async def subscribe_weight(self) -> sila.Stream[float]:
        """Subscribe to the current net weight in gram, accessed immediately."""

    @abc.abstractmethod
    @sila.ObservableProperty()
    async def subscribe_tare_weight(self) -> sila.Stream[float]:
        """Subscribe to the stored tare weight in gram."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[Unstable, Overloaded, Underloaded])
    @sila.Response(name="Weight")
    def get_stable_weight(self) -> float:
        """
        Get the stable net weight in gram.

        .. return:: The stable net weight in gram.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    @sila.Response(name="Tare Weight")
    def tare(self) -> float:
        """
        Tare with the current net weight, executed immediately (Not stable).

        .. return:: The stored tare weight in gram.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[Unstable])
    @sila.Response(name="Tare Weight")
    def tare_stable(self) -> float:
        """
        Tare with the stable net weight.

        .. return:: The stored tare weight in gram.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    def set_tare_weight(self, tare_weight: float) -> None:
        """
        Set a new, custom tare weight in gram.

        .. parameter:: The tare weight to be stored in gram.
        """

    @abc.abstractmethod
    @sila.UnobservableCommand()
    def clear_tare_weight(self) -> None:
        """Clear the currently stored tare weight."""

    @abc.abstractmethod
    @sila.UnobservableCommand()
    def zero(self) -> None:
        """Zero the balance immediately."""

    @abc.abstractmethod
    @sila.UnobservableCommand(errors=[Unstable])
    def zero_stable(self) -> None:
        """Zero the balance with a stable measurement."""
