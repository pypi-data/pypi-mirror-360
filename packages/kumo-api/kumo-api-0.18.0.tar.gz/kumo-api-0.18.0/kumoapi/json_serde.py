import json
from typing import Any, Dict, Type, TypeVar

from pydantic import SecretStr, parse_obj_as
from pydantic.json import pydantic_encoder

T = TypeVar('T')


def trusted_custom_pydantic_encoder(obj: Any) -> Any:
    if isinstance(obj, SecretStr):
        return obj.get_secret_value()
    return pydantic_encoder(obj)


def to_json(pydantic_obj: Any, insecure: bool = False) -> str:
    r"""Encodes a pydantic object into JSON.

    The `insecure` flag should only be used by trusted internal code where the
    output of the JSON is not accessible to any users and `SecretStr`s are
    hidden in some other fashion."""
    encoder = trusted_custom_pydantic_encoder if insecure else pydantic_encoder
    return json.dumps(
        pydantic_obj,
        default=encoder,
        allow_nan=True,
        indent=2,
    )


def to_json_dict(pydantic_obj: Any, insecure: bool = False) -> Dict[str, Any]:
    return json.loads(to_json(pydantic_obj, insecure=insecure))


def from_json(obj: Any, cls: Type[T]) -> T:
    if isinstance(obj, str):
        obj = json.loads(obj)
    return parse_obj_as(cls, obj)
