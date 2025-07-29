import json
from typing import Any


def serialize_model_value(value: Any, to_json: bool) -> Any:
    if not to_json:
        return value
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)
