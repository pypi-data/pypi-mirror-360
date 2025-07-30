from collections.abc import Mapping, Sequence
from typing import Any, TypeVar, overload

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")

@overload
def parse_args(
    arg_classes: type[_T1],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4, _T5]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5], type[_T6]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4, _T5, _T6]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1]],
    argv: Sequence[str],
) -> tuple[_T1]: ...
@overload
def parse_args(
    arg_classes: type[_T1],
    argv: Sequence[str],
) -> tuple[_T1]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2]],
    argv: Sequence[str],
) -> tuple[_T1, _T2]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4, _T5]: ...
@overload
def parse_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5], type[_T6]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4, _T5, _T6]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: type[_T1],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4, _T5, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5], type[_T6]],
    argv: Sequence[str],
    default_values: Mapping[str, Any] | None,
) -> tuple[_T1, _T2, _T3, _T4, _T5, _T6, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1]],
    argv: Sequence[str],
) -> tuple[_T1, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: type[_T1],
    argv: Sequence[str],
) -> tuple[_T1, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4, _T5, list[str]]: ...
@overload
def parse_known_args(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5], type[_T6]],
    argv: Sequence[str],
) -> tuple[_T1, _T2, _T3, _T4, _T5, _T6, list[str]]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1]: ...
@overload
def parse_dict(
    arg_classes: type[_T1],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1], type[_T2]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1, _T2]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1, _T2, _T3]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1, _T2, _T3, _T4]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1, _T2, _T3, _T4, _T5]: ...
@overload
def parse_dict(
    arg_classes: tuple[type[_T1], type[_T2], type[_T3], type[_T4], type[_T5], type[_T6]],
    argv: Mapping[str, Any],
    *,
    allow_extra_keys: bool = False,
) -> tuple[_T1, _T2, _T3, _T4, _T5, _T6]: ...
