from collections.abc import Mapping, Sequence
from typing import Any

from aceparse import AceParser


def parse_args(arg_classes, argv: Sequence[str], default_values: Mapping[str, Any] | None = None):
    parser = AceParser(arg_classes)
    return parser.parse_args_into_dataclasses(argv, return_remaining_strings=False, default_values=default_values)


def parse_dict(arg_classes, args: Mapping[str, Any], *, allow_extra_keys: bool = False):
    parser = AceParser(arg_classes)
    return parser.parse_dict(args, allow_extra_keys=allow_extra_keys)


def parse_known_args(arg_classes, argv: Sequence[str], default_values: Mapping[str, Any] | None = None):
    parser = AceParser(arg_classes)
    # wanted to specify this as arg to AceParser but it doesn't work with python 3.8/Jenkins plan
    parser.exit_on_error = False
    *args, remaining = parser.parse_args_into_dataclasses(
        argv, return_remaining_strings=True, default_values=default_values
    )
    return *args, remaining
