# something very like the huggingface test file, minus the bits that test transformers-specific things
# and compatibility with python < 3.10

# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ruff: noqa: RUF009

import argparse
import json
import os
import tempfile
from argparse import Namespace
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal

import pytest
import yaml

from aceparse import AceParser, make_choice_type_function, string_to_bool


@dataclass
class BasicExample:
    foo: int
    bar: float
    baz: str
    flag: bool


@dataclass
class WithDefaultExample:
    foo: int = 42
    baz: str = field(default="toto", metadata={"help": "help message"})


@dataclass
class WithDefaultBoolExample:
    foo: bool = False
    baz: bool = True
    opt: bool | None = None


class BasicEnum(Enum):
    titi = "titi"
    toto = "toto"


class MixedTypeEnum(Enum):
    titi = "titi"
    toto = "toto"
    fortytwo = 42


@dataclass
class EnumExample:
    foo: BasicEnum = "toto"  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.foo = BasicEnum(self.foo)


@dataclass
class MixedTypeEnumExample:
    foo: MixedTypeEnum = "toto"  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.foo = MixedTypeEnum(self.foo)


@dataclass
class OptionalExample:
    foo: int | None = None
    bar: float | None = field(default=None, metadata={"help": "help message"})
    baz: str | None = None
    ces: list[str] | None = field(default_factory=list)
    des: list[int] | None = field(default_factory=list)


@dataclass
class ListExample:
    foo_int: list[int] = field(default_factory=list)
    bar_int: list[int] = field(default_factory=lambda: [1, 2, 3])
    foo_str: list[str] = field(default_factory=lambda: ["Hallo", "Bonjour", "Hello"])
    foo_float: list[float] = field(default_factory=lambda: [0.1, 0.2, 0.3])


@dataclass
class RequiredExample:
    required_list: list[int] = field()
    required_str: str = field()
    required_enum: BasicEnum = field()

    def __post_init__(self) -> None:
        self.required_enum = BasicEnum(self.required_enum)


@dataclass
class StringLiteralAnnotationExample:
    foo: int
    required_enum: "BasicEnum" = field()
    opt: "bool | None" = None
    baz: "str" = field(default="toto", metadata={"help": "help message"})
    foo_str: "list[str]" = field(default_factory=lambda: ["Hallo", "Bonjour", "Hello"])


@dataclass
class WithDefaultBoolExamplePep604:
    foo: bool = False
    baz: bool = True
    opt: bool | None = None


@dataclass
class OptionalExamplePep604:
    foo: int | None = None
    bar: float | None = field(default=None, metadata={"help": "help message"})
    baz: str | None = None
    ces: list[str] | None = field(default_factory=list)
    des: list[int] | None = field(default_factory=list)


def assert_argparsers_equal(a: argparse.ArgumentParser, b: argparse.ArgumentParser) -> None:
    """
    Small helper to check pseudo-equality of parsed arguments on `ArgumentParser` instances.
    """
    assert len(a._actions) == len(b._actions)  # noqa: SLF001
    for x, y in zip(a._actions, b._actions, strict=False):  # noqa: SLF001
        xx = {k: v for k, v in vars(x).items() if k != "container"}
        yy = {k: v for k, v in vars(y).items() if k != "container"}

        # Choices with mixed type have custom function as "type"
        # So we need to compare results directly for equality
        if xx.get("choices") and yy.get("choices"):
            for expected_choice in yy["choices"] + xx["choices"]:
                assert xx["type"](expected_choice) == yy["type"](expected_choice)
            del xx["type"], yy["type"]

        assert xx == yy


def test_basic() -> None:
    parser = AceParser(BasicExample)

    expected = argparse.ArgumentParser()
    expected.add_argument("--foo", type=int, required=True)
    expected.add_argument("--bar", type=float, required=True)
    expected.add_argument("--baz", type=str, required=True)
    expected.add_argument("--flag", type=string_to_bool, default=False, const=True, nargs="?")
    assert_argparsers_equal(parser, expected)

    args = ["--foo", "1", "--baz", "quux", "--bar", "0.5"]
    (example,) = parser.parse_args_into_dataclasses(args, look_for_args_file=False)
    assert not example.flag


def test_with_default() -> None:
    parser = AceParser(WithDefaultExample)

    expected = argparse.ArgumentParser()
    expected.add_argument("--foo", default=42, type=int)
    expected.add_argument("--baz", default="toto", type=str, help="help message")
    assert_argparsers_equal(parser, expected)


def test_with_default_bool() -> None:
    expected = argparse.ArgumentParser()
    expected.add_argument("--foo", type=string_to_bool, default=False, const=True, nargs="?")
    expected.add_argument("--baz", type=string_to_bool, default=True, const=True, nargs="?")
    # A boolean no_* argument always has to come after its "default: True" regular counter-part
    # and its default must be set to False
    expected.add_argument("--no_baz", "--no-baz", action="store_false", default=False, dest="baz")
    expected.add_argument("--opt", type=string_to_bool, default=None)

    dataclass_types: list[type] = [WithDefaultBoolExample]
    dataclass_types.append(WithDefaultBoolExamplePep604)

    for dataclass_type in dataclass_types:
        parser = AceParser(dataclass_type, add_hyphenated_options=True)
        assert_argparsers_equal(parser, expected)

        args = parser.parse_args([])
        assert args == Namespace(foo=False, baz=True, opt=None)

        args = parser.parse_args(["--foo", "--no_baz"])
        assert args == Namespace(foo=True, baz=False, opt=None)

        args = parser.parse_args(["--foo", "--no-baz"])
        assert args == Namespace(foo=True, baz=False, opt=None)

        args = parser.parse_args(["--foo", "--baz"])
        assert args == Namespace(foo=True, baz=True, opt=None)

        args = parser.parse_args(["--foo", "True", "--baz", "True", "--opt", "True"])
        assert args == Namespace(foo=True, baz=True, opt=True)

        args = parser.parse_args(["--foo", "False", "--baz", "False", "--opt", "False"])
        assert args == Namespace(foo=False, baz=False, opt=False)


def test_with_enum() -> None:
    parser = AceParser(MixedTypeEnumExample)

    expected = argparse.ArgumentParser()
    expected.add_argument(
        "--foo",
        default="toto",
        choices=["titi", "toto", 42],
        type=make_choice_type_function(["titi", "toto", 42]),
    )
    assert_argparsers_equal(parser, expected)

    args = parser.parse_args([])
    assert args.foo == "toto"
    enum_ex = parser.parse_args_into_dataclasses([])[0]
    assert enum_ex.foo == MixedTypeEnum.toto

    args = parser.parse_args(["--foo", "titi"])
    assert args.foo == "titi"
    enum_ex = parser.parse_args_into_dataclasses(["--foo", "titi"])[0]
    assert enum_ex.foo == MixedTypeEnum.titi

    args = parser.parse_args(["--foo", "42"])
    assert args.foo == 42
    enum_ex = parser.parse_args_into_dataclasses(["--foo", "42"])[0]
    assert enum_ex.foo == MixedTypeEnum.fortytwo


def test_with_literal() -> None:
    @dataclass
    class LiteralExample:
        foo: Literal["titi", "toto", 42] = "toto"

    parser = AceParser(LiteralExample)

    expected = argparse.ArgumentParser()
    expected.add_argument(
        "--foo",
        default="toto",
        choices=("titi", "toto", 42),
        type=make_choice_type_function(["titi", "toto", 42]),
    )
    assert_argparsers_equal(parser, expected)

    args = parser.parse_args([])
    assert args.foo == "toto"

    args = parser.parse_args(["--foo", "titi"])
    assert args.foo == "titi"

    args = parser.parse_args(["--foo", "42"])
    assert args.foo == 42


def test_with_list() -> None:
    parser = AceParser(ListExample, add_hyphenated_options=True)

    expected = argparse.ArgumentParser()
    expected.add_argument("--foo_int", "--foo-int", nargs="+", default=[], type=int)
    expected.add_argument("--bar_int", "--bar-int", nargs="+", default=[1, 2, 3], type=int)
    expected.add_argument("--foo_str", "--foo-str", nargs="+", default=["Hallo", "Bonjour", "Hello"], type=str)
    expected.add_argument("--foo_float", "--foo-float", nargs="+", default=[0.1, 0.2, 0.3], type=float)

    assert_argparsers_equal(parser, expected)

    args = parser.parse_args([])
    assert args == Namespace(
        foo_int=[], bar_int=[1, 2, 3], foo_str=["Hallo", "Bonjour", "Hello"], foo_float=[0.1, 0.2, 0.3]
    )

    args = parser.parse_args("--foo_int 1 --bar_int 2 3 --foo_str a b c --foo_float 0.1 0.7".split())
    assert args == Namespace(foo_int=[1], bar_int=[2, 3], foo_str=["a", "b", "c"], foo_float=[0.1, 0.7])

    args = parser.parse_args("--foo-int 1 --bar-int 2 3 --foo-str a b c --foo-float 0.1 0.7".split())
    assert args == Namespace(foo_int=[1], bar_int=[2, 3], foo_str=["a", "b", "c"], foo_float=[0.1, 0.7])


def test_with_optional() -> None:
    expected = argparse.ArgumentParser()
    expected.add_argument("--foo", default=None, type=int)
    expected.add_argument("--bar", default=None, type=float, help="help message")
    expected.add_argument("--baz", default=None, type=str)
    expected.add_argument("--ces", nargs="+", default=[], type=str)
    expected.add_argument("--des", nargs="+", default=[], type=int)

    dataclass_types: list[type] = [OptionalExample]
    dataclass_types.append(OptionalExamplePep604)

    for dataclass_type in dataclass_types:
        parser = AceParser(dataclass_type)

        assert_argparsers_equal(parser, expected)

        args = parser.parse_args([])
        assert args == Namespace(foo=None, bar=None, baz=None, ces=[], des=[])

        args = parser.parse_args("--foo 12 --bar 3.14 --baz 42 --ces a b c --des 1 2 3".split())
        assert args == Namespace(foo=12, bar=3.14, baz="42", ces=["a", "b", "c"], des=[1, 2, 3])


def test_with_required() -> None:
    parser = AceParser(RequiredExample, add_hyphenated_options=True)

    expected = argparse.ArgumentParser()
    expected.add_argument("--required_list", "--required-list", nargs="+", type=int, required=True)
    expected.add_argument("--required_str", "--required-str", type=str, required=True)
    expected.add_argument(
        "--required_enum",
        "--required-enum",
        type=make_choice_type_function(["titi", "toto"]),
        choices=["titi", "toto"],
        required=True,
    )
    assert_argparsers_equal(parser, expected)


def test_with_string_literal_annotation() -> None:
    parser = AceParser(StringLiteralAnnotationExample, add_hyphenated_options=True)

    expected = argparse.ArgumentParser()
    expected.add_argument("--foo", type=int, required=True)
    expected.add_argument(
        "--required_enum",
        "--required-enum",
        type=make_choice_type_function(["titi", "toto"]),
        choices=["titi", "toto"],
        required=True,
    )
    expected.add_argument("--opt", type=string_to_bool, default=None)
    expected.add_argument("--baz", default="toto", type=str, help="help message")
    expected.add_argument("--foo_str", "--foo-str", nargs="+", default=["Hallo", "Bonjour", "Hello"], type=str)
    assert_argparsers_equal(parser, expected)


def test_parse_dict() -> None:
    parser = AceParser(BasicExample)

    args_dict = {
        "foo": 12,
        "bar": 3.14,
        "baz": "42",
        "flag": True,
    }

    parsed_args: BasicExample = parser.parse_dict(args_dict)[0]
    args = BasicExample(**args_dict)  # type: ignore[arg-type]
    assert parsed_args == args


def test_parse_dict_extra_key() -> None:
    parser = AceParser(BasicExample)

    args_dict = {
        "foo": 12,
        "bar": 3.14,
        "baz": "42",
        "flag": True,
        "extra": 42,
    }

    with pytest.raises(ValueError, match="Some keys are not used") as err:
        parser.parse_dict(args_dict, allow_extra_keys=False)
    err.match("extra")


def test_parse_json() -> None:
    parser = AceParser(BasicExample)

    args_dict_for_json = {
        "foo": 12,
        "bar": 3.14,
        "baz": "42",
        "flag": True,
    }
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_local_path = os.path.join(tmp_dir, "temp_json")
        with open(temp_local_path + ".json", "w+") as f:
            json.dump(args_dict_for_json, f)
        parsed_args: BasicExample = parser.parse_json_file(temp_local_path + ".json")[0]

    args = BasicExample(**args_dict_for_json)  # type: ignore[arg-type]
    assert parsed_args == args


def test_parse_yaml() -> None:
    parser = AceParser(BasicExample)

    args_dict_for_yaml = {
        "foo": 12,
        "bar": 3.14,
        "baz": "42",
        "flag": True,
    }
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_local_path = os.path.join(tmp_dir, "temp_yaml")
        with open(temp_local_path + ".yaml", "w+") as f:
            yaml.dump(args_dict_for_yaml, f)
        parsed_args: BasicExample = parser.parse_yaml_file(Path(temp_local_path + ".yaml"))[0]
    args = BasicExample(**args_dict_for_yaml)  # type: ignore[arg-type]
    assert parsed_args == args
