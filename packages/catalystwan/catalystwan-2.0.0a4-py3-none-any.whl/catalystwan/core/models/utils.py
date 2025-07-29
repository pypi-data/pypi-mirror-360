from dataclasses import is_dataclass
from typing import TypeVar, cast

from catalystwan.core.types import DataclassInstance

DataclassType = TypeVar("DataclassType", bound=DataclassInstance)


def count_matching_keys(model: DataclassType, model_payload: dict):
    matched_keys = 0
    for key, value in model_payload.items():
        try:
            model_value = getattr(model, key)
            matched_keys += 1
            if is_dataclass(model_value) and isinstance(value, dict):
                matched_keys += count_matching_keys(cast(DataclassType, model_value), value)
            elif (
                isinstance(model_value, list)
                and all([is_dataclass(element) for element in model_value])
                and isinstance(value, list)
            ):
                for model_v, input_v in zip(model_value, value):
                    matched_keys += count_matching_keys(model_v, input_v)
        except AttributeError:
            continue

    return matched_keys
