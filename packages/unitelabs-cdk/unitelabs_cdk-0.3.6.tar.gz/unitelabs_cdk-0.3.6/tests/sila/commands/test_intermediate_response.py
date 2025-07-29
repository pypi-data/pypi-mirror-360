import unittest.mock

import pytest

from sila import Element, Integer, String
from unitelabs.cdk.sila.commands.intermediate import Intermediate
from unitelabs.cdk.sila.commands.intermediate_responses import IntermediateResponse, IntermediateResponses


class TestFromSignature:
    # Infers intermediate responses with no parameter.
    def test_infer_intermediate_responses_no_parameter(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(): ...

        # Infer intermediate responses
        intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {}

    # Verify that the method raises when typing annotations are unkown.
    async def test_raises_when_annotation_unknown(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(intermediate: Intermediate[complex]): ...

        # Infer intermediate responses
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'complex' in .+\.handler\."):
            IntermediateResponses.from_signature(feature, handler)

    # Verify that the method raises when typing annotations are invalid.
    async def test_raises_when_annotation_invalid(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(intermediate: Intermediate[list]): ...

        # Infer intermediate responses
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'list' in .+\.handler\."):
            IntermediateResponses.from_signature(feature, handler)

    # Verify that the method raises when typing annotations are missing.
    async def test_raises_when_annotation_missing(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(intermediate): ...

        # Infer intermediate responses
        with pytest.raises(TypeError, match=r"Missing type annotation for parameter 'intermediate' in .+\.handler\."):
            IntermediateResponses.from_signature(feature, handler)

    # Infers intermediate responses with signature.
    def test_infer_intermediate_responses_signature(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(intermediate: Intermediate[str]): ...

        # Infer intermediate responses
        with pytest.warns(
            match=r"No name found for IntermediateResponses 0 in .+\.handler, defaulting to 'Unnamed 0'\."
        ):
            intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {
            "Unnamed0": Element(identifier="Unnamed0", display_name="Unnamed 0", description="", data_type=String),
        }

    # Infers intermediate responses with tuple.
    def test_infer_intermediate_responses_tuple(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(intermediate: Intermediate[tuple[str, int]]): ...

        # Infer intermediate responses
        with (
            pytest.warns(
                match=r"No name found for IntermediateResponses 0 in .+\.handler, defaulting to 'Unnamed 0'\."
            ),
            pytest.warns(
                match=r"No name found for IntermediateResponses 1 in .+\.handler, defaulting to 'Unnamed 1'\."
            ),
        ):
            intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {
            "Unnamed0": Element(identifier="Unnamed0", display_name="Unnamed 0", description="", data_type=String),
            "Unnamed1": Element(identifier="Unnamed1", display_name="Unnamed 1", description="", data_type=Integer),
        }

    # Infers intermediate responses with decorators.
    def test_infer_intermediate_responses_decorator(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @IntermediateResponse("Variable A")
        @IntermediateResponse("Variable B")
        def handler(intermediate: Intermediate[tuple[str, int]]):
            """
            .. yield:: Explanation of variable a.
            .. yield:: Explanation of variable b.
            """

        # Infer intermediate responses
        intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {
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

    # Infers intermediate responses with documentation.
    def test_infer_intermediate_responses_documentation(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @IntermediateResponse("Variable A")
        @IntermediateResponse("Variable B")
        def handler(intermediate: Intermediate[tuple[str, int]]):
            """
            .. yield:: Explanation of variable a.
            .. yield:: Explanation of variable b.
                :name: Override B
            """

        # Infer intermediate responses
        intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {
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

        @IntermediateResponse("Variable A", "Overriding explanation of variable a.")
        @IntermediateResponse("Variable B")
        def handler(intermediate: Intermediate[tuple[str, int]]):
            """
            .. yield:: Explanation of variable a.
            .. yield:: Explanation of variable b.
            """

        # Infer intermediate responses
        intermediate_responses = IntermediateResponses.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert intermediate_responses.elements == {
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

        def handler(intermediate: Intermediate[str]):
            """
            .. yield:: Explanation of variable a.
                :name: Override A
            .. yield:: Explanation of variable b.
                :name: Override B
            """

        # Infer parameters
        with pytest.warns(match=r"More documented items than annotations in .+\.handler, using only the first 1\."):
            IntermediateResponses.from_signature(feature, handler)

    # Verify that the method warns when more decorators than arguments are provided.
    async def test_warns_when_more_decorators_than_arguments(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @IntermediateResponse("Variable A")
        @IntermediateResponse("Variable B")
        def handler(intermediate: Intermediate[str]): ...

        # Infer parameters
        with pytest.warns(match=r"More decorators than annotations in .+\.handler, using only the first 1\."):
            IntermediateResponses.from_signature(feature, handler)
