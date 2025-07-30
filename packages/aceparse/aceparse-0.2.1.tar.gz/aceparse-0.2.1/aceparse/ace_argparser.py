# Copied from transformers master branch on 20231114, updated with changes from huggingface 20241202

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

import dataclasses
import datetime
import json
import sys
import types
from argparse import (
    Action,
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    _ArgumentGroup,
)
from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import copy
from enum import Enum
from inspect import isclass
from os import PathLike
from pathlib import Path
from typing import (
    Any,
    Generic,
    Literal,
    TypeVar,
    Union,
    get_type_hints,
)

import yaml

DataClass = TypeVar("DataClass")
DataClassType = TypeVar("DataClassType", bound=type)
EnumType = TypeVar("EnumType", bound=Enum)

if sys.version_info >= (3, 11):  # Python 3.11+
    from .py311 import ReturnType  # noqa: TID252
else:  # Python 3.10 and below
    ReturnType = Any  # Fallback for versions without TypeVarTuple support


# From https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def string_to_bool(v: str | bool) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    msg = f"Truthy value expected: got {v!r} but expected one of yes/no, true/false, t/f, y/n, 1/0 (case insensitive)."
    raise ArgumentTypeError(msg)


def make_choice_type_function(choices: list[EnumType]) -> Callable[[str], EnumType]:
    """
    Creates a mapping function from each choices string representation to the actual value. Used to support multiple
    value types for a single argument.

    Args:
        choices (list): List of choices.

    Returns:
        Callable[[str], Any]: Mapping function from string representation to actual value for each choice.
    """
    str_to_choice = {str(choice): choice for choice in choices}

    def choice_func(arg: str) -> EnumType:
        return str_to_choice.get(arg, arg)  # type: ignore[arg-type]

    return choice_func


class CommaSeparatedList:
    """Marker class to indicate a value came from comma/semicolon separated input"""

    def __init__(self, items: list):
        self.items = items


def make_comma_separated_list_type_function(element_type: type) -> Callable[[str], Any]:
    """
    Creates a function that parses comma-separated or semicolon-separated values,
    but also handles individual elements for backward compatibility.

    Args:
        element_type: The type of elements in the list (e.g., int, str, float)

    Returns:
        Callable[[str], any]: Function that parses comma/semicolon-separated string to element_type
    """

    def parse_element_or_list(value: str) -> Any:
        if not value.strip():
            msg = f"Empty value for {element_type.__name__} list"
            raise ArgumentTypeError(msg)

        # Handle comma and semicolon separators
        if "," in value:
            items = value.split(",")
        elif ";" in value:
            items = value.split(";")
        else:
            # Single item
            try:
                return element_type(value.strip())
            except (ValueError, TypeError) as e:
                msg = f"Invalid {element_type.__name__}: '{value}' ({e})"
                raise ArgumentTypeError(msg) from e

        # Parse separated items
        parsed_items = []
        failed_items = []
        empty_items = []

        for item in items:
            item_stripped = item.strip()
            if not item_stripped:
                empty_items.append(True)
                continue
            try:
                parsed_items.append(element_type(item_stripped))
            except (ValueError, TypeError):
                failed_items.append(item_stripped)

        # Build clear error message
        if empty_items or failed_items:
            error_parts = []
            if empty_items:
                count = len(empty_items)
                item_word = "item" if count == 1 else "items"
                error_parts.append(f"contains {count} empty {item_word}")
            if failed_items:
                error_parts.append(f"invalid values: {failed_items}")
            error_msg = " and ".join(error_parts)
            msg = f"List '{value}' {error_msg}"
            raise ArgumentTypeError(msg)

        if not parsed_items:
            msg = f"No valid {element_type.__name__} items in '{value}'"
            raise ArgumentTypeError(msg)

        return CommaSeparatedList(parsed_items)

    return parse_element_or_list


class CommaSeparatedListAction(Action):
    """Custom argparse action that handles comma/semicolon separated lists and flattens results."""

    def __init__(self, option_strings: list[str], dest: str, element_type: type, **kwargs: Any) -> None:
        self.element_type = element_type
        self.parse_func = make_comma_separated_list_type_function(element_type)
        self._initialized_destinations: set[str] = set()
        super().__init__(option_strings, dest, nargs="+", **kwargs)

    def __call__(
        self,
        _parser: ArgumentParser,
        namespace: Any,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        # Check if this destination has been initialized in this parse session
        if self.dest in self._initialized_destinations:
            # This is a subsequent call, extend the existing list
            result = getattr(namespace, self.dest, [])[:]
        else:
            # First call, start fresh
            result = []
            self._initialized_destinations.add(self.dest)

        # Process each value with better error context
        values_list = values if isinstance(values, list) else [values] if values is not None else []
        for value in values_list:
            try:
                parsed = self.parse_func(value)
                if isinstance(parsed, CommaSeparatedList):
                    # Flatten comma-separated values
                    result.extend(parsed.items)
                else:
                    # Regular individual value
                    result.append(parsed)
            except ArgumentTypeError as e:
                # Re-raise with option context for clearer error messages
                msg = f"argument {option_string}: {e}"
                raise ArgumentTypeError(msg) from e

        setattr(namespace, self.dest, result)


def AceArg(  # noqa: N802
    *,
    aliases: str | list[str] | None = None,
    help: str | None = None,  # noqa: A002
    default: Any = dataclasses.MISSING,
    default_factory: Callable[[], Any] | dataclasses._MISSING_TYPE = dataclasses.MISSING,
    metadata: dict | None = None,
    **kwargs: Any,
) -> dataclasses.Field:
    """Argument helper enabling a concise syntax to create dataclass fields for parsing with `AceParser`.

    Example comparing the use of `AceArg` and `dataclasses.field`:
    ```
    @dataclass
    class Args:
        regular_arg: str = dataclasses.field(
            default="unknown",
            metadata={
                "aliases": ["--example", "-e"],
                "help": "This syntax could be better!",
            },
        )
        arg: str = AceArg(
            default="unknown",
            aliases=["--example", "-e"],
            help="What a nice syntax!",
        )
    ```

    Args:
        aliases (Union[str, List[str]], optional):
            Single string or list of strings of aliases to pass on to argparse, e.g. `aliases=["--example", "-e"]`.
            Defaults to None.
        help (str, optional): Help string to pass on to argparse that can be displayed with --help. Defaults to None.
        default (Any, optional):
            Default value for the argument. If not default or default_factory is specified, the argument is required.
            Defaults to dataclasses.MISSING.
        default_factory (Callable[[], Any], optional):
            The default_factory is a 0-argument function called to initialize a field's value. It is useful to provide
            default values for mutable types, e.g. lists: `default_factory=list`. Mutually exclusive with `default=`.
            Defaults to dataclasses.MISSING.
        metadata (dict, optional): Further metadata to pass on to `dataclasses.field`. Defaults to None.

    Returns:
        Field: A `dataclasses.Field` with the desired properties.
    """
    if metadata is None:
        # Important, don't use as default param in function signature because dict is mutable and shared across function calls
        metadata = {}
    if aliases is not None:
        metadata["aliases"] = aliases
    if help is not None:
        metadata["help"] = help

    if default != dataclasses.MISSING:
        return dataclasses.field(default=default, metadata=metadata, **kwargs)
    if default_factory != dataclasses.MISSING:
        return dataclasses.field(default_factory=default_factory, metadata=metadata, **kwargs)
    return dataclasses.field(metadata=metadata, **kwargs)


class AceParser(ArgumentParser, Generic[DataClassType]):
    """
    This subclass of `argparse.ArgumentParser` uses type hints on dataclasses to generate arguments.

    The class is designed to play well with the native argparse. In particular, you can add more (non-dataclass backed)
    arguments to the parser after initialization and you'll get the output back after parsing as an additional
    namespace. Optional: To create sub argument groups use the `_argument_group_name` attribute in the dataclass.
    """

    dataclass_types: Iterable[DataClassType]

    def _reset_comma_separated_actions(self) -> None:
        """Reset state in CommaSeparatedListAction instances for a fresh parse."""
        for action in self._actions:
            if isinstance(action, CommaSeparatedListAction):
                action._initialized_destinations.clear()  # noqa: SLF001

    def __init__(
        self,
        dataclass_types: DataClassType | Iterable[DataClassType],
        *,
        add_hyphenated_options: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            dataclass_types:
                Dataclass type, or list of dataclass types for which we will "fill" instances with the parsed args.
            kwargs (`Dict[str, Any]`, *optional*):
                Passed to `argparse.ArgumentParser()` in the regular way.
        """
        # To make the default appear when using --help
        if "formatter_class" not in kwargs:
            kwargs["formatter_class"] = ArgumentDefaultsHelpFormatter
        if "allow_abbrev" not in kwargs:
            kwargs["allow_abbrev"] = False
        self._add_hyphenated_options = add_hyphenated_options
        super().__init__(**kwargs)
        dataclass_types_tuple = tuple(dataclass_types) if isinstance(dataclass_types, Iterable) else (dataclass_types,)
        self.dataclass_types = dataclass_types_tuple
        self.register("type", datetime.date, datetime.date.fromisoformat)
        self.register("type", datetime.datetime, datetime.datetime.fromisoformat)
        for dtype in self.dataclass_types:
            self._add_dataclass_arguments(dtype)

    @staticmethod
    def _parse_dataclass_field(
        parser: ArgumentParser | _ArgumentGroup,
        field: dataclasses.Field,
        *,
        add_hyphenated_options: bool,
    ) -> None:
        # Long-option strings are conventionally separated by hyphens rather
        # than underscores, e.g., "--long-format" rather than "--long_format".
        # Argparse converts hyphens to underscores so that the destination
        # string is a valid attribute name. AceParser should do the same.
        long_options = [f"--{field.name}"]
        if "_" in field.name and add_hyphenated_options:
            long_options.append(f"--{field.name.replace('_', '-')}")

        kwargs = field.metadata.copy()
        # field.metadata is not used at all by Data Classes,
        # it is provided as a third-party extension mechanism.
        if isinstance(field.type, str):
            msg = (
                "Unresolved type detected, which should have been done with the help of "
                "`typing.get_type_hints` method by default"
            )
            raise TypeError(msg)

        aliases = kwargs.pop("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]

        origin_type = getattr(field.type, "__origin__", field.type)
        if origin_type is Union or (hasattr(types, "UnionType") and isinstance(origin_type, types.UnionType)):
            if str not in field.type.__args__ and (
                len(field.type.__args__) != 2 or type(None) not in field.type.__args__  # noqa: PLR2004
            ):
                msg = (
                    "Only `Union[X, NoneType]` (i.e., `Optional[X]`) is allowed for `Union` because"
                    " the argument parser only supports one type per argument."
                    f" Problem encountered in field '{field.name}'."
                )
                raise ValueError(msg)
            if type(None) not in field.type.__args__:
                # filter `str` in Union
                field.type = (
                    field.type.__args__[0] if isinstance(field.type.__args__[1], str) else field.type.__args__[1]
                )
                origin_type = getattr(field.type, "__origin__", field.type)
            elif bool not in field.type.__args__:
                # filter `NoneType` in Union (except for `Union[bool, NoneType]`)
                field.type = (
                    field.type.__args__[0] if isinstance(None, field.type.__args__[1]) else field.type.__args__[1]
                )
                origin_type = getattr(field.type, "__origin__", field.type)

        # A variable to store kwargs for a boolean field, if needed
        # so that we can init a `no_*` complement argument (see below)
        bool_kwargs = {}
        if origin_type is Literal or (isinstance(field.type, type) and issubclass(field.type, Enum)):
            if origin_type is Literal:
                kwargs["choices"] = field.type.__args__
            else:
                kwargs["choices"] = [x.value for x in field.type]

            kwargs["type"] = make_choice_type_function(kwargs["choices"])

            if field.default is not dataclasses.MISSING:
                kwargs["default"] = field.default
            else:
                kwargs["required"] = True
        elif field.type is bool or field.type == bool | None:
            # Copy the correct kwargs to use to instantiate a `no_*` complement argument below.
            # We do not initialize it here because the `no_*` alternative must be instantiated after the real argument
            bool_kwargs = copy(kwargs)

            # Hack because type=bool in argparse does not behave as we want.
            kwargs["type"] = string_to_bool
            if field.type is bool or (field.default is not None and field.default is not dataclasses.MISSING):
                # Default value is False if we have no default when of type bool.
                default = False if field.default is dataclasses.MISSING else field.default
                # This is the value that will get picked if we don't include --field_name in any way
                kwargs["default"] = string_to_bool(default)
                # This tells argparse we accept 0 or 1 value after --field_name
                kwargs["nargs"] = "?"
                # This is the value that will get picked if we do --field_name (without value)
                kwargs["const"] = True
        elif isclass(origin_type) and issubclass(origin_type, list):
            element_type = field.type.__args__[0]
            # Use comma/semicolon separated parsing with backward compatibility
            kwargs["action"] = CommaSeparatedListAction
            kwargs["element_type"] = element_type
            if field.default_factory is not dataclasses.MISSING:
                kwargs["default"] = field.default_factory()
            elif field.default is dataclasses.MISSING:
                kwargs["required"] = True
        else:
            kwargs["type"] = field.type
            if field.default is not dataclasses.MISSING:
                kwargs["default"] = field.default
            elif field.default_factory is not dataclasses.MISSING:
                kwargs["default"] = field.default_factory()
            else:
                kwargs["required"] = True
        parser.add_argument(*long_options, *aliases, **kwargs)

        # Add a complement `no_*` argument for a boolean field AFTER the initial field has already been added.
        # Order is important for arguments with the same destination!
        # We use a copy of earlier kwargs because the original kwargs have changed a lot before reaching down
        # here and we do not need those changes/additional keys.
        if field.default is True and (field.type is bool or field.type == bool | None):
            bool_kwargs["default"] = False
            long_options = [f"--no_{field.name}"]
            if add_hyphenated_options:
                long_options.append(f"--no-{field.name.replace('_', '-')}")
            parser.add_argument(
                *long_options,
                action="store_false",
                dest=field.name,
                **bool_kwargs,
            )

    def _add_dataclass_arguments(self, dtype: DataClassType) -> None:
        parser = (
            self.add_argument_group(dtype._argument_group_name)  # noqa: SLF001
            if hasattr(dtype, "_argument_group_name")
            else self
        )

        try:
            type_hints: dict[str, type] = get_type_hints(dtype)
        except NameError:
            msg = (
                f"Type resolution failed for {dtype}. Try declaring the class in global scope or "
                "removing line of `from __future__ import annotations` which opts in Postponed "
                "Evaluation of Annotations (PEP 563)"
            )
            raise RuntimeError(msg)  # noqa: B904

        for field in dataclasses.fields(dtype):
            if not field.init:
                continue
            field.type = type_hints[field.name]
            self._parse_dataclass_field(parser, field, add_hyphenated_options=self._add_hyphenated_options)

    @property
    def class_names(self) -> list[str]:
        return [c.__name__ for c in self.dataclass_types]

    def parse_args(self, args: Sequence[str] | None = None, namespace: Any = None) -> Any:
        """Override to reset action state before parsing."""
        self._reset_comma_separated_actions()
        return super().parse_args(args, namespace)

    def parse_known_args(self, args: Sequence[str] | None = None, namespace: Any = None) -> tuple[Any, list[str]]:
        """Override to reset action state before parsing."""
        self._reset_comma_separated_actions()
        return super().parse_known_args(args, namespace)

    def parse_args_into_dataclasses(
        self,
        args: Sequence[str] | None = None,
        return_remaining_strings: bool = False,  # noqa: FBT001, FBT002
        look_for_args_file: bool = True,  # noqa: FBT001, FBT002
        args_filename: str | Path | None = None,
        args_file_flag: str | None = None,
        default_values: dict[str, Any] | None = None,
    ) -> ReturnType:
        """
        Parse command-line args into instances of the specified dataclass types.

        This relies on argparse's `ArgumentParser.parse_known_args`. See the doc at:
        docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser.parse_args

        Args:
            args:
                List of strings to parse. The default is taken from sys.argv. (same as argparse.ArgumentParser)
            return_remaining_strings:
                If true, also return a list of remaining argument strings.
            look_for_args_file:
                If true, will look for a ".args" file with the same base name as the entry point script for this
                process, and will append its potential content to the command line args.
            args_filename:
                If not None, will use this file instead of the ".args" file specified in the previous argument.
            args_file_flag:
                If not None, will look for a file in the command-line args specified with this flag. The flag can be
                specified multiple times and precedence is determined by the order (last one wins).
            default_values:
                Default values for parameters not specified on the command line.
                Order of precedence command line > default value here > default on class

        Returns:
            Tuple consisting of:
                - the dataclass instances in the same order as they were passed to the initializer.
                - if applicable, an additional namespace for more (non-dataclass backed) arguments added to the parser
                  after initialization.
                - The potential list of remaining argument strings. (same as argparse.ArgumentParser.parse_known_args)
        """
        args = list(args) if args is not None else sys.argv[1:]

        file_args = []
        if args_file_flag or args_filename or (look_for_args_file and len(sys.argv)):
            args_files = []

            if args_filename is not None:
                args_file_path = Path(args_filename)
                if not args_file_path.is_file():
                    msg = f"Args file {args_file_path.as_posix()} does not exist"
                    raise ValueError(msg)
                args_files.append(args_file_path)
            elif look_for_args_file and len(sys.argv):
                potential_args_file = Path(sys.argv[0]).with_suffix(".args")
                if potential_args_file.is_file():
                    args_files.append(potential_args_file)

            # args files specified via command line flag should overwrite default args files so we add them last
            if args_file_flag:
                # Create special parser just to extract the args_file_flag values
                args_file_parser = ArgumentParser()
                args_file_parser.add_argument(args_file_flag, type=str, action="append")

                # Use only remaining args for further parsing (remove the args_file_flag)
                cfg, args = args_file_parser.parse_known_args(args=args)
                cmd_args_file_paths = vars(cfg).get(args_file_flag.lstrip("-"), None)

                if cmd_args_file_paths:
                    args_files = [Path(p) for p in cmd_args_file_paths]
                    # we expect all specified arguments files to exist
                    non_existent_args_files = [
                        args_file.as_posix() for args_file in args_files if not args_file.is_file()
                    ]
                    if len(non_existent_args_files) > 0:
                        msg = f"Missing arguments files specified by args file flag '{args_file_flag}': {non_existent_args_files}"
                        raise ValueError(msg)

                    args_files.extend(args_files)

            for args_file in args_files:
                file_args += args_file.read_text().split()

        default_arg_pairs = (
            [(f"--{k}", str(v)) for k, v in default_values.items()] if default_values is not None else []
        )
        default_args = [a for pair in default_arg_pairs for a in pair]

        # in case of duplicate arguments the last one has precedence
        # args specified via the command line should overwrite args from files, so we add them last
        args = default_args + file_args + args

        namespace, remaining_args = self.parse_known_args(args=args)
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}
            inputs = {k: v for k, v in vars(namespace).items() if k in keys}
            for k in keys:
                delattr(namespace, k)
            obj = dtype(**inputs)
            outputs.append(obj)
        if len(namespace.__dict__) > 0:
            # additional namespace.
            outputs.append(namespace)
        if return_remaining_strings:
            return *outputs, remaining_args
        if remaining_args:
            msg = f"Some arguments are not used by the AceParser with data classes {self.class_names}: {remaining_args}"
            raise ValueError(msg)

        return (*outputs,)

    def parse_dict(self, args: Mapping[str, Any], *, allow_extra_keys: bool = False) -> ReturnType:
        """
        Alternative helper method that does not use `argparse` at all, instead uses a dict and populating the dataclass
        types.

        Args:
            args (`Mapping`):
                mapping/dict containing config values
            allow_extra_keys (`bool`, *optional*, defaults to `False`):
                Defaults to False. If False, will raise an exception if the dict contains keys that are not parsed.

        Returns:
            Tuple consisting of:
                - the dataclass instances in the same order as they were passed to the initializer.
        """
        unused_keys = set(args.keys())
        outputs = []
        for dtype in self.dataclass_types:
            keys = {f.name for f in dataclasses.fields(dtype) if f.init}
            inputs = {k: v for k, v in args.items() if k in keys}
            unused_keys.difference_update(inputs.keys())
            obj = dtype(**inputs)
            outputs.append(obj)
        if not allow_extra_keys and unused_keys:
            msg = f"Some keys are not used by the AceParser with data classes {self.class_names}: {sorted(unused_keys)}"
            raise ValueError(msg)
        return tuple(outputs)

    def parse_json_file(self, json_file: str | PathLike, *, allow_extra_keys: bool = False) -> ReturnType:
        """
        Alternative helper method that does not use `argparse` at all, instead loading a json file and populating the
        dataclass types.

        Args:
            json_file (`str` or `os.PathLike`):
                File name of the json file to parse
            allow_extra_keys (`bool`, *optional*, defaults to `False`):
                Defaults to False. If False, will raise an exception if the json file contains keys that are not
                parsed.

        Returns:
            Tuple consisting of:
                - the dataclass instances in the same order as they were passed to the initializer.
        """
        outputs: ReturnType = self.parse_dict(
            json.loads(Path(json_file).read_bytes()), allow_extra_keys=allow_extra_keys
        )
        return outputs

    def parse_yaml_file(self, yaml_file: str | PathLike, *, allow_extra_keys: bool = False) -> ReturnType:
        """
        Alternative helper method that does not use `argparse` at all, instead loading a yaml file and populating the
        dataclass types.

        Args:
            yaml_file (`str` or `os.PathLike`):
                File name of the yaml file to parse
            allow_extra_keys (`bool`, *optional*, defaults to `False`):
                Defaults to False. If False, will raise an exception if the yaml file contains keys that are not
                parsed.

        Returns:
            Tuple consisting of:
                - the dataclass instances in the same order as they were passed to the initializer.
        """
        outputs: ReturnType = self.parse_dict(
            yaml.safe_load(Path(yaml_file).read_text()),
            allow_extra_keys=allow_extra_keys,
        )
        return outputs
