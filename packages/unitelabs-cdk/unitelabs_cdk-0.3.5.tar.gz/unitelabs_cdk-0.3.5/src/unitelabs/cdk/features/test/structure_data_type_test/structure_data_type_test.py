# ruff: noqa: D205, D401, E501

import dataclasses

from unitelabs.cdk import sila


@dataclasses.dataclass
class TestStructure(sila.CustomDataType):
    """
    An example Structure data type containing all SiLA basic types.

    .. parameter:: A value of SiLA data type String.
    .. parameter:: A value of SiLA data type Integer.
    .. parameter:: A value of SiLA data type Real.
    .. parameter:: A value of SiLA data type Boolean.
    .. parameter:: A value of SiLA data type Binary.
    .. parameter:: A value of SiLA data type Date.
    .. parameter:: A value of SiLA data type Time.
    .. parameter:: A value of SiLA data type Timestamp
    .. parameter:: A value of SiLA data type Any.
    """

    string_type_value: str
    integer_type_value: int
    real_type_value: float
    boolean_type_value: bool
    binary_type_value: bytes
    date_type_value: sila.datetime.date
    time_type_value: sila.datetime.time
    timestamp_type_value: sila.datetime.datetime
    any_type_value: sila.Any


@dataclasses.dataclass
class InnerStructure:
    """
    A structure type that is part of the middle structure.

    .. parameter:: A value of SiLA data type String contained in the innermost structure.
    .. parameter:: A value of SiLA data type Integer contained in the innermost structure.
    """

    inner_string_type_value: str
    inner_integer_type_value: int


@dataclasses.dataclass
class MiddleStructure:
    """
    Another structure type that is part of the outer structure.

    .. parameter:: A value of SiLA data type String contained in the middle structure.
    .. parameter:: A value of SiLA data type Integer contained in the middle structure.
    .. parameter:: A structure type that is part of the middle structure.
    """

    middle_string_type_value: str
    middle_integer_type_value: int
    inner_structure: InnerStructure


@dataclasses.dataclass
class DeepStructure(sila.CustomDataType):
    """
    An example Structure data type that contains other structures within.

    .. parameter:: A value of SiLA data type String contained in the topmost structure.
    .. parameter:: A value of SiLA data type Integer contained in the topmost structure.
    .. parameter:: Another structure type that is part of the outer structure.
    """

    outer_string_type_value: str
    outer_integer_type_value: int
    middle_structure: MiddleStructure


class StructureDataTypeTest(sila.Feature):
    """Provides commands and properties to set or respectively get SiLA Structure Data Type values via command parameters or property responses respectively."""

    def __init__(self):
        super().__init__(originator="org.silastandard", category="test")

    # Simple Structure type

    @sila.UnobservableCommand()
    @sila.Response(name="ReceivedValues", description="The structure that has been received.")
    def echo_structure_value(self, structure_value: TestStructure) -> TestStructure:
        """
        Receives a structure value and returns the structure that has been received (binary value is expected to be an embedded value, any typer value is expected to be a Basic type).

        .. parameter:: The Structure value to be returned.
        .. return:: The structure that has been received.
        """

        return structure_value

    @sila.UnobservableProperty()
    def structure_value(self) -> TestStructure:
        """
        Returns a structure with the following elements values:
        - String value = 'SiLA2_Test_String_Value'
        - Integer value = 5124
        - Real value = 3.1415926
        - Boolean value = true
        - Binary value = embedded string 'SiLA2_Binary_String_Value'
        - Date value = 05.08.2022 respective 08/05/2022
        - Time value = 12:34:56.789
        - Timestamp value = 2022-08-05 12:34:56.789
        - Any type value = string 'SiLA2_Any_Type_String_Value'.
        """

        return TestStructure(
            string_type_value="SiLA2_Test_String_Value",
            integer_type_value=5124,
            real_type_value=3.1415926,
            boolean_type_value=True,
            binary_type_value=b"SiLA2_Binary_String_Value",
            date_type_value=sila.datetime.date(
                year=2022, month=8, day=5, tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2))
            ),
            time_type_value=sila.datetime.time(
                hour=12,
                minute=34,
                second=56,
                microsecond=789000,
                tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2)),
            ),
            timestamp_type_value=sila.datetime.datetime(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                microsecond=789000,
                tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2)),
            ),
            any_type_value="SiLA2_Any_Type_String_Value",
        )

    # Deep Structure type

    @sila.UnobservableCommand()
    @sila.Response(name="Received Values", description="The structure that has been received.")
    def echo_deep_structure_value(self, deep_structure_value: DeepStructure) -> DeepStructure:
        """
        Receives a multilevel structure value and returns the structure that has been received.

        .. parameter:: The deep Structure value to be set.
        """
        return deep_structure_value

    @sila.UnobservableProperty()
    def deep_structure_value(self) -> DeepStructure:
        """
        Returns a multilevel structure with the following values:
        - string value = 'Outer_Test_String'
        - integer value = 1111
        - middle structure value =
          - string value = 'Middle_Test_String'
          - integer value = 2222
          - inner structure value =
            - string value = 'Inner_Test_String'
            - integer value = 3333.
        """

        return DeepStructure(
            outer_string_type_value="Outer_Test_String",
            outer_integer_type_value=1111,
            middle_structure=MiddleStructure(
                middle_string_type_value="Middle_Test_String",
                middle_integer_type_value=2222,
                inner_structure=InnerStructure(
                    inner_string_type_value="Inner_Test_String", inner_integer_type_value=3333
                ),
            ),
        )
