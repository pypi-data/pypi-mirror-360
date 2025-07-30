import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest
from pydantic.dataclasses import dataclass

from aceparse import AceParser


@dataclass
class A:
    fit_on_data: bool


def test_abbreviations_not_allowed_by_default() -> None:
    # We want to make sure the arg parsing is as predictable as possible, so we disallow abbreviations for
    # the command line options by default.
    parser = AceParser((A,))
    a, _ = parser.parse_args_into_dataclasses(["--fit", "l"], return_remaining_strings=True)
    assert a.fit_on_data is False


def test_abbreviations_explicitly_allowed() -> None:
    parser = AceParser((A,), allow_abbrev=True)
    a, _ = parser.parse_args_into_dataclasses(["--fit", "1"], return_remaining_strings=True)
    assert a.fit_on_data is True


def test_abbreviations_invalid_value() -> None:
    parser = AceParser((A,), allow_abbrev=True, exit_on_error=False)
    with pytest.raises(argparse.ArgumentError) as e:
        a, _ = parser.parse_args_into_dataclasses(["--fit", "l"], return_remaining_strings=True)
    e.match("Truthy value expected: got 'l' but expected one of yes/no, true/false, t/f, y/n, 1/0")


@dataclass
class OptWithBool:
    value: bool


@dataclass
class OptWithBoolDefaultTrue:
    value: bool = True


@pytest.mark.parametrize(
    "args",
    [
        ["--value", "true"],
        ["--value", "True"],
        ["--value", "T"],
        ["--value"],
        ["--value=True"],
    ],
)
def test_bool_option_true(args: Sequence[str]) -> None:
    parser = AceParser([OptWithBool])
    (opt,) = parser.parse_args_into_dataclasses(args)
    assert opt.value is True


@pytest.mark.parametrize(
    "args",
    [
        ["--value", "False"],
        [],
        ["--value=False"],
        ["--value=f"],
    ],
)
def test_bool_option_false(args: Sequence[str]) -> None:
    parser = AceParser([OptWithBool])
    (opt,) = parser.parse_args_into_dataclasses(args)
    assert opt.value is False


@pytest.mark.parametrize(
    "args",
    [
        ["--value", "True"],
        [],
        ["--value=True"],
        ["--value=t"],
        ["--value"],
    ],
)
def test_bool_option_default_true_true(args: Sequence[str]) -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    (opt,) = parser.parse_args_into_dataclasses(args)
    assert opt.value is True


@pytest.mark.parametrize(
    "args",
    [
        ["--value", "False"],
        ["--value=False"],
        ["--value=f"],
        ["--no_value"],
    ],
)
def test_bool_option_default_true_false(args: Sequence[str]) -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    (opt,) = parser.parse_args_into_dataclasses(args)
    assert opt.value is False


@dataclass
class OptWithBoolDefaultString:
    value: bool = "false"  # type: ignore[assignment]


@dataclass
class OptWithBoolDefaultBad:
    value: bool = "truue"  # type: ignore[assignment]


@pytest.mark.skipif(sys.version_info < (3, 10), reason="exit_on_error doesn't work with python 3.8")
def test_bool_option_bad_default() -> None:
    with pytest.raises(argparse.ArgumentTypeError) as e:
        _ = AceParser([OptWithBoolDefaultBad])
    assert e.match("Truthy value expected: got 'truue'")


def test_bool_option_string_default() -> None:
    parser = AceParser([OptWithBoolDefaultString])
    (opt,) = parser.parse_args_into_dataclasses([])
    assert opt.value is False


def test_code_args_file_does_not_exist() -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    with pytest.raises(ValueError, match="does not exist"):
        parser.parse_args_into_dataclasses(["--value"], args_filename="not_a_file.args")


def test_command_line_args_file_does_not_exist() -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    with pytest.raises(ValueError, match="does not exist"):
        parser.parse_args_into_dataclasses(args_filename="not_a_file.args")


def test_command_line_args_file_from_flag_does_not_exist() -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    with pytest.raises(ValueError, match="Missing arguments files"):
        parser.parse_args_into_dataclasses(args_file_flag="--argies", args=["--argies", "badfile.args"])


def test_command_line_args_file(tmp_path: Path) -> None:
    args_file = tmp_path / "stuff.args"
    args_file.write_text("--value=true")
    parser = AceParser([OptWithBool])
    (opts,) = parser.parse_args_into_dataclasses([], args_filename=args_file)
    assert opts.value is True


def test_command_line_args_file_command_line_takes_precedence(tmp_path: Path) -> None:
    args_file = tmp_path / "stuff.args"
    args_file.write_text("--value=true")
    parser = AceParser([OptWithBool])
    (opts,) = parser.parse_args_into_dataclasses(["--value=False"], args_filename=args_file)
    assert opts.value is False


def test_args_file_specified_wrong() -> None:
    parser = AceParser([OptWithBoolDefaultTrue])
    with pytest.raises(ValueError, match="Some arguments are not used"):
        parser.parse_args_into_dataclasses(["--value", "true", "not_a_file.args"])
