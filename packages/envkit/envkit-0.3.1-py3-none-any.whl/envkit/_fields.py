from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING, Protocol, final, overload

from envkit._utils import pipeline
from envkit.error import MissingEnvVarError, ValidationError

if TYPE_CHECKING:
    from enum import Enum
    from types import EllipsisType
    from typing import Callable, LiteralString

type Unset = EllipsisType


class ParserFactory[T, **P](Protocol):
    def __call__(
        self, name: str, raw_value: str, *args: P.args, **kwargs: P.kwargs
    ) -> T: ...


@final
class EnvField[T, **P]:
    __slots__ = ("factory",)

    def __init__(self, factory: ParserFactory[T, P]) -> None:
        self.factory = factory

    @overload
    def __call__(
        self,
        name: str,
        default: T | Unset = ...,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T: ...

    @overload
    def __call__(
        self, name: str, default: None, *args: P.args, **kwargs: P.kwargs
    ) -> T | None: ...

    def __call__(
        self,
        name: str,
        default: T | None | Unset = ...,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T | None:
        """Parse an environment variable.

        Args:
            name: Environment variable name
            default: Default value if variable is not set. Let unset
                    to require the variable. Use None to allow None return.
            *args: Additional arguments passed to the factory
            **kwargs: Validation constraints passed to the factory

        Returns:
            The parsed and validated value, or the default if variable is unset

        Raises:
            MissingEnvVarError: If required but not set.
            ValidationError: If the value does not meet validation constraints.
        """
        raw_value = getenv(name)
        if raw_value is None:
            if default is ...:
                raise MissingEnvVarError(
                    f"Environment variable {name!r} is required but not set."
                )
            return default

        return self.factory(name, raw_value, *args, **kwargs)


def parse_str(
    name: str,
    raw_value: str,
    *,
    min_length: int | None = None,
    max_length: int | None = None,
) -> str:
    if min_length is not None and len(raw_value) < min_length:
        raise ValidationError(
            f"Environment variable {name!r} is shorter than the minimum length {min_length}."
        )
    if max_length is not None and len(raw_value) > max_length:
        raise ValidationError(
            f"Environment variable {name!r} is longer than the maximum length {max_length}."
        )
    return raw_value


def parse_literal[T: LiteralString](
    name: str, raw_value: str, *, choices: tuple[T, ...]
) -> T:
    if raw_value not in choices:
        raise ValidationError(
            f"Environment variable {name!r} must be one of {choices!r}, got {raw_value!r}."
        )
    return raw_value


def parse_int(
    name: str,
    raw_value: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    if min_value is not None and max_value is not None and min_value > max_value:
        raise ValidationError("min_value cannot be greater than max_value")

    try:
        value = int(raw_value.strip())
    except ValidationError as error:
        raise ValidationError(
            f"Environment variable {name!r} must be an integer, got {raw_value!r}."
        ) from error

    if min_value is not None and value < min_value:
        raise ValidationError(
            f"Environment variable {name!r} is less than the minimum value {min_value}."
        )
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"Environment variable {name!r} is greater than the maximum value {max_value}."
        )
    return value


def parse_bool(name: str, raw_value: str) -> bool:
    match raw_value.strip().lower():
        case "true" | "1" | "yes" | "on":
            return True
        case "false" | "0" | "no" | "off":
            return False
        case _:
            raise ValidationError(
                f"Environment variable {name!r} must be a boolean, got {raw_value!r}."
            )


def parse_enum[T: Enum](
    name: str, raw_value: str, *, enum: type[T], case_sensitive: bool = False
) -> T:
    raw_value_transforms: list[Callable[[str], str]] = [str.strip]
    if not case_sensitive:
        raw_value_transforms.append(str.lower)
    normalize_raw_value = pipeline(*raw_value_transforms)

    enum_member_transforms: list[Callable[[str], str]] = []
    if not case_sensitive:
        enum_member_transforms.append(str.lower)
    normalize_enum_member = pipeline(*enum_member_transforms)

    lookup = {normalize_enum_member(member.name): member for member in enum}

    key = normalize_raw_value(raw_value)
    if member := lookup.get(key):
        return member

    valid = [member.name for member in enum]
    raise ValidationError(
        f"Environment variable {name!r} must be one of {valid!r}, got {raw_value!r}"
    )


@final
class Fields:
    """Public interface for parsing environment variables with type safety.

    This class provides pre-configured field parsers for common data types.
    Each field type supports validation constraints and proper error handling.

    Attributes:
        str: Parser for string values with length validation
        literal: Parser for literal values matching a fixed set
        int: Parser for integer values with range validation
        bool: Parser for boolean values (supports multiple formats)
        enum: Parser for enum values by member name
    """

    str = EnvField(parse_str)
    """String field parser with optional length validation.

    Args:
        name (str): Environment variable name.
        default (str | None, optional): Default value if the variable is unset.
        min_length (int, optional): Minimum allowed length of the string.
        max_length (int, optional): Maximum allowed length of the string.

    Returns:
        str | None: Parsed and validated string, or the `default` value if unset.

    Raises:
        MissingEnvVarError: If required but not set.
    """

    literal = EnvField(parse_literal)
    """Literal field parser that matches against a set of allowed values.

    Args:
        name (str): Environment variable name.
        default (T | None, optional): Default value if the variable is unset.
        choices (tuple[T, ...]): Allowed literal values to match against.

    Returns:
        T | None: Parsed literal value, or the `default` if unset.

    Raises:
        MissingEnvVarError: If required but not set.
    """

    int = EnvField(parse_int)
    """Integer field parser with optional range validation.

    Args:
        name (str): Environment variable name.
        default (int | None, optional): Default value if the variable is unset.
        min_value (int, optional): Minimum allowed integer value.
        max_value (int, optional): Maximum allowed integer value.

    Returns:
        int | None: Parsed integer, or the `default` if unset.

    Raises:
        MissingEnvVarError: If required but not set.
        ValidationError:
            - If parsing to `int` fails.
            - If the parsed value is outside the specified range.
    """

    bool = EnvField(parse_bool)
    """Boolean field parser supporting multiple formats.

    Accepts (case-insensitive): `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`.

    Args:
        name (str): Environment variable name.
        default (bool | None, optional): Default value if the variable is unset.

    Returns:
        bool | None: Parsed boolean, or the `default` if unset.

    Raises:
        MissingEnvVarError: If required but not set.
        ValidationError: If the value is not a recognizable boolean.
    """

    enum = EnvField(parse_enum)
    """Enum field parser that matches by member name.

    Args:
        name (str): Environment variable name.
        default (T | None, optional): Default value if the variable is unset.
        enum (type[T]): The `Enum` class to parse against.
        case_sensitive (bool, optional): Whether member-name matching is case-sensitive.
            Defaults to `False` (case-insensitive).

    Returns:
        T | None: Parsed enum member, or the `default` if unset.

    Raises:
        MissingEnvVarError: If required but not set.
        ValidationError: If the value does not match any enum member.
    """
