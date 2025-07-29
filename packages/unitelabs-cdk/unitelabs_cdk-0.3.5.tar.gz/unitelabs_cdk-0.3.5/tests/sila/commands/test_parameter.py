import unittest.mock

import pytest

from sila import Element, Integer, String
from unitelabs.cdk.sila.commands.parameters import Parameter, Parameters


class TestFromSignature:
    # Infers parameters with no parameter.
    def test_infer_parameters_no_parameter(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(): ...

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {}

    # Infers parameters with self parameter.
    def test_infer_parameters_self_parameter(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(self): ...

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {}

    # Verify that the method raises when typing annotations are missing.
    async def test_raises_when_annotation_missing(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(self, variable_a, variable_b): ...

        # Infer parameters
        with pytest.raises(TypeError, match=r"Missing type annotation for parameter 'variable_a' in .+\.handler\."):
            Parameters.from_signature(feature, handler)

    # Verify that the method raises when typing annotations are unkown.
    async def test_raises_when_annotation_unknown(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(self, variable_a: int, variable_b: complex): ...

        # Infer parameters
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'complex' in .+\.handler\."):
            Parameters.from_signature(feature, handler)

    # Verify that the method raises when typing annotations are invalid.
    async def test_raises_when_annotation_invalid(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(self, variable_a: list, variable_b: str): ...

        # Infer parameters
        with pytest.raises(TypeError, match=r"Unable to identify SiLA type from annotation 'list' in .+\.handler\."):
            Parameters.from_signature(feature, handler)

    # Infers parameters with signature.
    def test_infer_parameters_signature(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        def handler(self, variable_a: str, variable_b: int): ...

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {
            "variable_a": Element(identifier="VariableA", display_name="Variable A", description="", data_type=String),
            "variable_b": Element(identifier="VariableB", display_name="Variable B", description="", data_type=Integer),
        }

    # Infers parameters with decorators.
    def test_infer_parameters_decorator(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Parameter("Override A")
        @Parameter("Override B")
        def handler(self, variable_a: str, variable_b: int): ...

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {
            "variable_a": Element(
                identifier="OverrideA",
                display_name="Override A",
                description="",
                data_type=String,
            ),
            "variable_b": Element(
                identifier="OverrideB",
                display_name="Override B",
                description="",
                data_type=Integer,
            ),
        }

    # Infers parameters with documentation.
    def test_infer_parameters_documentation(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Parameter("Variable A")
        @Parameter("Variable B")
        def handler(self, variable_a: str, variable_b: int):
            """
            .. parameter:: Explanation of variable a.
            .. parameter:: Explanation of variable b.
                :name: Override B
            """

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {
            "variable_a": Element(
                identifier="VariableA",
                display_name="Variable A",
                description="Explanation of variable a.",
                data_type=String,
            ),
            "variable_b": Element(
                identifier="OverrideB",
                display_name="Override B",
                description="Explanation of variable b.",
                data_type=Integer,
            ),
        }

    async def test_that_decorator_overrides_docs_description(self):
        # Initialize the method
        feature = unittest.mock.Mock()

        @Parameter("Variable A", "Overriding explanation of variable a.")
        @Parameter("Variable B")
        def handler(self, variable_a: str, variable_b: int):
            """
            .. parameter:: Explanation of variable a.
            .. parameter:: Explanation of variable b.
            """

        # Infer parameters
        parameters = Parameters.from_signature(feature, handler)

        # Assert that the method returns the correct value
        assert parameters.elements == {
            "variable_a": Element(
                identifier="VariableA",
                display_name="Variable A",
                description="Overriding explanation of variable a.",
                data_type=String,
            ),
            "variable_b": Element(
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

        def handler(self, variable_a: str):
            """
            .. parameter:: Explanation of variable a.
            .. parameter:: Explanation of variable b.
                :name: Override B
            """

        # Infer parameters
        with pytest.warns(match=r"More documented items than annotations in .+\.handler, using only the first 1\."):
            Parameters.from_signature(feature, handler)
