import dataclasses
import types
import typing
from dataclasses import Field, field

from typing import Any, TypeVar

from .exceptions import MissingEnvVarError, InvalidTypeError
from loguru import logger

T = TypeVar("T")





def env_field(env_var: str, *, default: Any = dataclasses.MISSING) -> Field:
    """Creates a field that loads its value from a single environment variable."""
    metadata = {"env": env_var}
    if default is not dataclasses.MISSING:
        return field(default=default, metadata=metadata)
    return field(metadata=metadata)


def prefix_field(prefix: str) -> Field:
    """Creates a nested config field that uses the given string as a prefix."""
    # This field must be a dataclass, so it doesn't need a default value here.
    # The loader will instantiate it.
    return field(metadata={"prefix": prefix})


def cast_var(
    ftype: types, name: str, raw_value: Any, config_kwargs: dict, full_env_var_name: str
):
    try:
        if ftype is bool:
            match raw_value.lower():
                case "true" | "1" | "t" | "yes":
                    config_kwargs[name] = True
                case "false" | "0" | "f" | "no":
                    config_kwargs[name] = False
                case _:
                    raise InvalidTypeError(
                        f"Failed to cast env var '{full_env_var_name}' (value: '{raw_value}') to type {ftype.__name__} for attribute '{name}'."
                    )
        elif typing.get_origin(ftype) is typing.Literal:
            if raw_value in typing.get_args(ftype):
                config_kwargs[name] = raw_value
            else:
                raise InvalidTypeError(
                    f"Failed to cast env var '{full_env_var_name}' (value: '{raw_value}') to Literral for attribute '{name}'. Allowed values are {','.join(typing.get_args(ftype))}"
                )
        elif typing.get_origin(ftype) is types.UnionType:
            union_types = typing.get_args(ftype)
            if len(union_types) == 2 and types.NoneType in union_types:
                if raw_value in ("None", "none", None):
                    logger.debug(f"field {name} detected as none")
                    config_kwargs[name] = None
                else:
                    non_none_type = next(t for t in union_types if t is not type(None))
                    config_kwargs = cast_var(
                        non_none_type, name, raw_value, config_kwargs, full_env_var_name
                    )
            else:
                raise InvalidTypeError(
                    f"'{name}' is invalid. Union type is only allowed for exactly 2 types, one of both being None"
                )
        else:
            config_kwargs[name] = ftype(raw_value)
    except (ValueError, TypeError) as exc:
        raise InvalidTypeError(
            f"Failed to cast env var '{full_env_var_name}' (value from env var: '{raw_value}') to type {ftype.__name__} for attribute '{name}'. | {str(exc)} "
        )

    return config_kwargs


