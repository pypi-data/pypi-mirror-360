import json
from argparse import ArgumentTypeError
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from aceparse import AceParser


@dataclass
class StringListExample:
    items: list[str] = field(default_factory=list)


@dataclass
class IntListExample:
    numbers: list[int] = field(default_factory=list)


@dataclass
class FloatListExample:
    values: list[float] = field(default_factory=list)


@dataclass
class RequiredListExample:
    required_items: list[str] = field()


def test_comma_separated_strings() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple,banana,cherry"])
    assert args.items == ["apple", "banana", "cherry"]


def test_semicolon_separated_strings() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple;banana;cherry"])
    assert args.items == ["apple", "banana", "cherry"]


def test_comma_separated_with_spaces() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple, banana, cherry"])
    assert args.items == ["apple", "banana", "cherry"]


def test_semicolon_separated_with_spaces() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple ; banana ; cherry"])
    assert args.items == ["apple", "banana", "cherry"]


def test_single_item() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple"])
    assert args.items == ["apple"]


def test_multiple_flags_accumulate() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple,banana", "--items", "cherry"])
    assert args.items == ["apple", "banana", "cherry"]


def test_mixed_separators_and_flags() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple,banana", "--items", "cherry;date"])
    assert args.items == ["apple", "banana", "cherry", "date"]


def test_comma_separated_integers() -> None:
    parser = AceParser(IntListExample)
    (args,) = parser.parse_args_into_dataclasses(["--numbers", "1,2,3,4,5"])
    assert args.numbers == [1, 2, 3, 4, 5]


def test_semicolon_separated_integers() -> None:
    parser = AceParser(IntListExample)
    (args,) = parser.parse_args_into_dataclasses(["--numbers", "1;2;3;4;5"])
    assert args.numbers == [1, 2, 3, 4, 5]


def test_comma_separated_floats() -> None:
    parser = AceParser(FloatListExample)
    (args,) = parser.parse_args_into_dataclasses(["--values", "1.1,2.2,3.3"])
    assert args.values == [1.1, 2.2, 3.3]


def test_empty_items_error() -> None:
    parser = AceParser(StringListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):
        parser.parse_args_into_dataclasses(["--items", "apple,,banana,"])


def test_whitespace_only_items_error() -> None:
    parser = AceParser(StringListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):
        parser.parse_args_into_dataclasses(["--items", "apple, , banana,   "])


def test_invalid_integer_conversion() -> None:
    parser = AceParser(IntListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):  # argparse exits on error
        parser.parse_args_into_dataclasses(["--numbers", "1,abc,3"])


def test_empty_string_error() -> None:
    parser = AceParser(StringListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):
        parser.parse_args_into_dataclasses(["--items", ""])


def test_multiple_invalid_items_error() -> None:
    parser = AceParser(IntListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):
        parser.parse_args_into_dataclasses(["--numbers", "1,abc,3,def,5"])


def test_all_empty_items_error() -> None:
    parser = AceParser(StringListExample)
    with pytest.raises((SystemExit, ArgumentTypeError)):
        parser.parse_args_into_dataclasses(["--items", ", , ,"])


def test_default_factory_preserved() -> None:
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses([])
    assert args.items == []


def test_required_list_with_comma_separated() -> None:
    parser = AceParser(RequiredListExample)
    (args,) = parser.parse_args_into_dataclasses(["--required_items", "a,b,c"])
    assert args.required_items == ["a", "b", "c"]


def test_required_list_missing_raises_error() -> None:
    parser = AceParser(RequiredListExample)
    with pytest.raises(SystemExit):  # argparse exits on missing required arg
        parser.parse_args_into_dataclasses([])


def test_comma_and_semicolon_in_same_string() -> None:
    """Test that comma takes precedence when both separators are present"""
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "apple,banana;cherry"])
    # Should split on comma, so "banana;cherry" becomes one item
    assert args.items == ["apple", "banana;cherry"]


def test_no_separators() -> None:
    """Test that single items without separators work correctly"""
    parser = AceParser(StringListExample)
    (args,) = parser.parse_args_into_dataclasses(["--items", "single_item"])
    assert args.items == ["single_item"]


def test_parse_dict_with_lists() -> None:
    """Test that parse_dict works correctly with list fields"""
    parser = AceParser(StringListExample)
    (args,) = parser.parse_dict({"items": ["apple", "banana", "cherry"]})
    assert args.items == ["apple", "banana", "cherry"]


def test_parse_dict_with_int_lists() -> None:
    """Test that parse_dict works correctly with int list fields"""
    parser = AceParser(IntListExample)
    (args,) = parser.parse_dict({"numbers": [1, 2, 3, 4, 5]})
    assert args.numbers == [1, 2, 3, 4, 5]


def test_parse_dict_empty_list() -> None:
    """Test that parse_dict works with empty lists"""
    parser = AceParser(StringListExample)
    (args,) = parser.parse_dict({"items": []})
    assert args.items == []


def test_parse_dict_missing_list() -> None:
    """Test that parse_dict works when list field is missing (uses default)"""
    parser = AceParser(StringListExample)
    (args,) = parser.parse_dict({})
    assert args.items == []


def test_parse_json_file_with_lists(tmp_path: Path) -> None:
    """Test that parse_json_file works correctly with list fields"""
    json_file = tmp_path / "test.json"
    data = {"items": ["apple", "banana", "cherry"]}
    json_file.write_text(json.dumps(data))

    parser = AceParser(StringListExample)
    (args,) = parser.parse_json_file(json_file)
    assert args.items == ["apple", "banana", "cherry"]


def test_parse_yaml_file_with_lists(tmp_path: Path) -> None:
    """Test that parse_yaml_file works correctly with list fields"""
    yaml_file = tmp_path / "test.yaml"
    yaml_content = """
items:
  - apple
  - banana
  - cherry
"""
    yaml_file.write_text(yaml_content)

    parser = AceParser(StringListExample)
    (args,) = parser.parse_yaml_file(yaml_file)
    assert args.items == ["apple", "banana", "cherry"]


def test_parse_dict_with_string_for_list_field() -> None:
    """Test that dict parsing doesn't do comma-parsing on strings (only command line does)"""
    parser = AceParser(StringListExample)
    # When passed from dict/json/yaml, strings are passed through as-is
    (args,) = parser.parse_dict({"items": "apple,banana,cherry"})
    # This should NOT be split by commas - dict parsing bypasses argparse logic entirely
    assert args.items == "apple,banana,cherry"
