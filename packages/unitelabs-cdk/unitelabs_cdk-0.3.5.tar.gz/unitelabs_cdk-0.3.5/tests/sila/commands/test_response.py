import unittest.mock

import pytest

from sila import Element, Integer, String
from unitelabs.cdk.sila.commands.responses import Response, Responses


class TestFromSignature:
    # Verify that the method raises when typing annotations are unkown.
    async def test_raises_when_annotation_unknown(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> complex: ...

        # Infer responses
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'complex' in .+\.handler\."):
            Responses.from_signature(feature, handler)

    # Verify that the method raises when typing annotations are invalid.
    async def test_raises_when_annotation_invalid(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> list: ...

        # Infer responses
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'list' in .+\.handler\."):
            Responses.from_signature(feature, handler)

    # Infers responses with typing annotations missing.
    def test_infer_responses_annotation_missing(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(): ...

        # Infer responses
        responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {}

    # Infers responses with return none.
    def test_infer_responses_return_none(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> None: ...

        # Infer responses
        responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {}

    # Infers responses with signature.
    def test_infer_responses_signature(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> str: ...

        # Infer responses
        with pytest.warns(match=r"No name found for Responses 0 in .+\.handler, defaulting to 'Unnamed 0'\."):
            responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {
            "Unnamed0": Element(identifier="Unnamed0", display_name="Unnamed 0", description="", data_type=String),
        }

    # Infers responses with tuple.
    def test_infer_responses_tuple(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> tuple[str, int]: ...

        # Infer responses
        with (
            pytest.warns(match=r"No name found for Responses 0 in .+\.handler, defaulting to 'Unnamed 0'\."),
            pytest.warns(match=r"No name found for Responses 1 in .+\.handler, defaulting to 'Unnamed 1'\."),
        ):
            responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {
            "Unnamed0": Element(identifier="Unnamed0", display_name="Unnamed 0", description="", data_type=String),
            "Unnamed1": Element(identifier="Unnamed1", display_name="Unnamed 1", description="", data_type=Integer),
        }

    # Infers responses with decorators.
    def test_infer_responses_decorator(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Response("Variable A")
        @Response("Variable B")
        def handler() -> tuple[str, int]:
            """
            .. return:: Explanation of variable a.
            .. return:: Explanation of variable b.
            """

            raise NotImplementedError

        # Infer responses
        responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {
            "VariableA": Element(
                identifier="VariableA",
                display_name="Variable A",
                description="Explanation of variable a.",
                data_type=String,
            ),
            "VariableB": Element(
                identifier="VariableB",
                display_name="Variable B",
                description="Explanation of variable b.",
                data_type=Integer,
            ),
        }

    # Infers responses with documentation.
    def test_infer_responses_documentation(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Response("Variable A")
        @Response("Variable B")
        def handler() -> tuple[str, int]:
            """
            .. return:: Explanation of variable a.
            .. return:: Explanation of variable b.
                :name: Override B
            """

            raise NotImplementedError

        # Infer responses
        responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {
            "VariableA": Element(
                identifier="VariableA",
                display_name="Variable A",
                description="Explanation of variable a.",
                data_type=String,
            ),
            "OverrideB": Element(
                identifier="OverrideB",
                display_name="Override B",
                description="Explanation of variable b.",
                data_type=Integer,
            ),
        }

    async def test_that_decorator_overrides_docs_description(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Response("Variable A", "Overriding explanation of variable a.")
        @Response("Variable B")
        def handler() -> tuple[str, int]:
            """
            .. return:: Explanation of variable a.
            .. return:: Explanation of variable b.
            """

            raise NotImplementedError

        # Infer responses
        responses = Responses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert responses.elements == {
            "VariableA": Element(
                identifier="VariableA",
                display_name="Variable A",
                description="Overriding explanation of variable a.",
                data_type=String,
            ),
            "VariableB": Element(
                identifier="VariableB",
                display_name="Variable B",
                description="Explanation of variable b.",
                data_type=Integer,
            ),
        }

    # Verify that the method warns when more documentations than arguments are provided.
    async def test_warns_when_more_documentations_than_arguments(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler() -> str:
            """
            .. return:: Explanation of variable a.
                :name: Override A
            .. return:: Explanation of variable b.
                :name: Override B
            """

            raise NotImplementedError

        # Infer parameters
        with pytest.warns(match=r"More documented items than annotations in .+\.handler, using only the first 1\."):
            Responses.from_signature(feature, handler)

    # Verify that the method warns when more decorators than arguments are provided.
    async def test_warns_when_more_decorators_than_arguments(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Response("Variable A")
        @Response("Variable B")
        def handler() -> str: ...

        # Infer parameters
        with pytest.warns(match=r"More decorators than annotations in .+\.handler, using only the first 1\."):
            Responses.from_signature(feature, handler)
