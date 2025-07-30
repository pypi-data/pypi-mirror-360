import dataclasses
from argparse import ArgumentError
from enum import Enum

import pytest
from pydantic.dataclasses import dataclass

from aceparse.extensions import parse_dict, parse_known_args


@dataclass
class A1:
    key1: str


@dataclass
class A2:
    key2: str


@dataclass
class A3:
    key3: str = dataclasses.field(default="unset3")


def test_parse_known_single_class_no_default() -> None:
    a1, _ = parse_known_args((A1,), ["--key1", "val1"])
    assert a1.key1 == "val1"


def test_parse_known_single_class_command_overrides_default() -> None:
    a1, _ = parse_known_args((A1,), ["--key1", "val1"], default_values={"key1": "unset"})
    assert a1.key1 == "val1"


def test_parse_known_single_class_command_with_default() -> None:
    a1, _ = parse_known_args((A1,), [], default_values={"key1": "unset"})
    assert a1.key1 == "unset"


def test_parse_known_single_default_on_class() -> None:
    a3, _ = parse_known_args((A3,), [])
    assert a3.key3 == "unset3"


def test_parse_known_single_class_default_arg_overrides_default_on_class() -> None:
    a3, _ = parse_known_args((A3,), [], default_values={"key3": "default3"})
    assert a3.key3 == "default3"


def test_parse_known_single_class_command_line_overrides_all() -> None:
    a1, _ = parse_known_args((A3,), ["--key3", "val3"], default_values={"key3": "default3"})
    assert a1.key3 == "val3"


def test_parse_known_multi_class_no_default() -> None:
    a1, a2, _ = parse_known_args((A1, A2), ["--key1", "val1", "--key2", "val2"], default_values=None)
    assert a1.key1 == "val1"
    assert a2.key2 == "val2"


def test_parse_known_multi_class_command_overrides_default() -> None:
    a1, a2, _ = parse_known_args(
        (A1, A2), ["--key1", "val1", "--key2", "val2"], default_values={"key1": "unset1", "key2": "unset2"}
    )
    assert a1.key1 == "val1"
    assert a2.key2 == "val2"


def test_parse_known_multi_class_command_with_default() -> None:
    a1, a2, _ = parse_known_args((A1, A2), [], default_values={"key1": "unset1", "key2": "unset2"})
    assert a1.key1 == "unset1"
    assert a2.key2 == "unset2"


@dataclass
class ABool:
    b: bool
    b_true: bool = dataclasses.field(default=True)
    b_false: bool = dataclasses.field(default=False)
    b_opt: bool | None = dataclasses.field(default=None)
    b_opt_true: bool | None = dataclasses.field(default=True)
    b_opt_false: bool | None = dataclasses.field(default=False)


def test_parse_bool_unset() -> None:
    a, _ = parse_known_args((ABool,), ["--b", "True"])
    assert a == ABool(True, True, False, None, True, False)


_default_values_bools = {
    "b": True,
    "b_true": False,
    "b_false": True,
    "b_opt": True,
    "b_opt_true": False,
    "b_opt_false": True,
}


def test_parse_bool_default_strings() -> None:
    default_values_str = {k: str(v) for k, v in _default_values_bools.items()}
    a, _ = parse_known_args((ABool,), [], default_values_str)
    assert a == ABool(True, False, True, True, False, True)


def test_parse_bool_defaults() -> None:
    a, _ = parse_known_args((ABool,), [], _default_values_bools)
    assert a == ABool(True, False, True, True, False, True)


class ExampleEnum(str, Enum):
    Val1 = "Val1"
    Val2 = "Val2"


@dataclass
class AEnum:
    e: ExampleEnum


def test_parse_enum_default() -> None:
    a, _ = parse_known_args((AEnum,), ["--e", "Val2"])
    assert a == AEnum(e=ExampleEnum("Val2"))


def test_parse_enum_default_actual_type() -> None:
    # check that specifying the actual value works rather than a string
    a, _ = parse_known_args((AEnum,), ["--e", ExampleEnum.Val2])
    assert a == AEnum(e=ExampleEnum("Val2"))


@dataclass
class AOptionalInt:
    val: int | None = 1


@pytest.mark.parametrize("value", ["None", "", "null"])
def test_parse_none_to_optional_int(value: str) -> None:
    # it is currently impossible to set an Optional with non-None default value to None: this test documents that.
    with pytest.raises(ArgumentError) as e:
        _, __ = parse_known_args((AOptionalInt,), ["--val", value])
    e.match("invalid int value")


def test_parse_dict_for_optional_int() -> None:
    # check that we do indeed get the correct default value if we don't pass a dictionary
    (a,) = parse_dict((AOptionalInt,), {})
    assert a.val == 1

    # but the same thing does work for parsing a dict
    (a,) = parse_dict((AOptionalInt,), {"val": None})
    assert a.val is None
