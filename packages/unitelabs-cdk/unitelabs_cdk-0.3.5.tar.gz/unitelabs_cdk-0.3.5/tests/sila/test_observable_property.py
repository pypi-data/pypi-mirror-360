import unittest.mock

import pytest

from sila import Stream
from sila.framework.errors.defined_execution_error import DefinedExecutionError
from unitelabs.cdk.sila.common.feature import Feature
from unitelabs.cdk.sila.property.observable_property import ObservableProperty


class DefinedError(Exception):
    pass


@pytest.fixture
def feature():
    return Feature(identifier="Feature", name="Feature")


@pytest.fixture
def handler():
    return ObservableProperty(identifier="ObservableProperty", name="Observable Property", errors=[DefinedError])


class TestExecute:
    # Execute synchronous function with default parameters.
    async def test_execute_synchronous_default_parameters(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        callback = unittest.mock.Mock()

        def function() -> Stream[int]:
            callback()
            yield 1
            yield 2
            yield 3

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        callback.assert_called_once_with()

        # Assert that the method returns the correct value
        assert result_0 == {"ObservableProperty": 1}
        assert result_1 == {"ObservableProperty": 2}
        assert result_2 == {"ObservableProperty": 3}

    # Verify that the method raises an error when the synchronous function raises.
    async def test_raises_when_synchronous_raises(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        def function() -> Stream[int]:
            msg = "Hello, World!"
            raise Exception(msg)

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        with pytest.raises(Exception, match=r"Exception: Hello, World!"):
            await result.__anext__()

    # Verify that the method raises a defined execution error when the synchronous decorator knows the error type.
    async def test_raises_when_synchronous_raises_known_error(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        def function() -> Stream[int]:
            msg = "Hello, World!"
            raise DefinedError(msg)

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        with pytest.raises(DefinedExecutionError) as exc_info:
            await result.__anext__()

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Common base class for all non-exit exceptions."
        assert exc_info.value.message == "Hello, World!"

    # Execute asynchronous function with default parameters.
    async def test_execute_asynchronous_default_parameters(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        callback = unittest.mock.AsyncMock()

        async def function() -> Stream[int]:
            await callback()
            yield 1
            yield 2
            yield 3

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        result_0 = await result.__anext__()
        result_1 = await result.__anext__()
        result_2 = await result.__anext__()

        # Assert that the function was called with the correct arguments
        callback.assert_awaited_once_with()

        # Assert that the method returns the correct value
        assert result_0 == {"ObservableProperty": 1}
        assert result_1 == {"ObservableProperty": 2}
        assert result_2 == {"ObservableProperty": 3}

    # Verify that the method raises an error when the asynchronous function raises.
    async def test_raises_when_asynchronous_raises(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        async def function() -> Stream[int]:
            msg = "Hello, World!"
            raise Exception(msg)

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        with pytest.raises(Exception, match=r"Exception: Hello, World!"):
            await result.__anext__()

    # Verify that the method raises a defined execution error when the asynchronous decorator knows the error type.
    async def test_raises_when_asynchronous_raises_known_error(self, feature: Feature, handler: ObservableProperty):
        # Initialize the observable property
        async def function() -> Stream[int]:
            msg = "Hello, World!"
            raise DefinedError(msg)

        handler(function)
        handler.attach(feature)

        # Execute function
        result = handler.execute(metadata={})
        with pytest.raises(DefinedExecutionError) as exc_info:
            await result.__anext__()

        assert exc_info.value.identifier == "DefinedError"
        assert exc_info.value.display_name == "Defined Error"
        assert exc_info.value.description == "Common base class for all non-exit exceptions."
        assert exc_info.value.message == "Hello, World!"
