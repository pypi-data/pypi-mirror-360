import inspect
import json

import pytest

from datetime import datetime
from hashlib import md5
from typing import Optional, Type, Union

from dasl_api.models import *
from pydantic import BaseModel
from pydantic.fields import FieldInfo


checked_dasl_types = {
    # Resources
    WorkspaceV1AdminConfig: "admin_config.json",
    CoreV1DataSource: "data_source.json",
    CoreV1Rule: "rule.json",
    WorkspaceV1WorkspaceConfig: "workspace_config.json",
    ContentV1DatasourcePreset: "datasource_preset.json",
    # Data
    DbuiV1ObservableEventsList: "observable_events_list.json",
}


simple_types = [
    bool,
    int,
    float,
    str,
    datetime,
]


def is_simple_type(tpe: Type) -> bool:
    return tpe in simple_types


def is_dasl_api_type(tpe: Type) -> bool:
    if tpe.__name__ in globals():
        return "dasl_api" in globals()[tpe.__name__].__module__
    return False


def dasl_model_to_dict(tpe: Type[BaseModel]) -> dict:
    decorators = getattr(
        getattr(tpe, "__pydantic_decorators__", None), "field_validators", {}
    )
    return {
        "name": tpe.__name__,
        "fields": [
            field_to_dict(name, field, decorators)
            for name, field in tpe.model_fields.items()
        ],
    }


def field_to_dict(name: str, field: FieldInfo, validators: dict) -> dict:
    d = {
        "name": name,
        "alias": field.alias,
        "is_required": field.is_required(),
        "is_nullable": is_nullable(field.annotation),
        "is_sequence": is_sequence(field.annotation),
        "validation_hash": field_validation_hash(name, validators),
    }
    field_type: Union[*simple_types, BaseModel] = inner_type(field.annotation)
    if is_simple_type(field_type):
        d["type"] = field_type.__name__
    elif is_dasl_api_type(field_type):
        d["type"] = dasl_model_to_dict(field_type)
    else:
        raise Exception(
            f"unsupported field type {field_type} encountered while converting field - {name}: {field}"
        )
    return d


def is_sequence(tpe: Type) -> bool:
    seq_types = [list, set, frozenset, tuple]
    if tpe in seq_types:
        return True
    if hasattr(tpe, "__origin__"):
        if tpe.__origin__ in seq_types:
            return True
    if hasattr(tpe, "__args__"):
        return is_sequence(tpe.__args__[0])
    return False


def is_nullable(tpe: Type) -> bool:
    return hasattr(tpe, "__args__") and type(None) in tpe.__args__


def field_validation_hash(field_name: str, validators: dict) -> Optional[str]:
    for validator in validators.values():
        if hasattr(validator, "info") and hasattr(validator.info, "fields"):
            if field_name in validator.info.fields:
                return md5(
                    inspect.getsource(validator.func).encode("utf-8")
                ).hexdigest()
    return None


def inner_type(tpe: Type) -> Type:
    if hasattr(tpe, "__args__"):
        return inner_type(tpe.__args__[0])
    return tpe


def dasl_model_to_string(tpe: Type[BaseModel]) -> str:
    d = dasl_model_to_dict(tpe)
    return json.dumps(d, indent=2, sort_keys=True)


@pytest.mark.parametrize(
    "tpe",
    checked_dasl_types.keys(),
    ids=[f"{tpe.__name__} model is unchanged" for tpe in checked_dasl_types.keys()],
)
def test_api_model_for_changes(tpe):
    with open(f"test/expected_api_models/{checked_dasl_types[tpe]}", "r") as f:
        expected_val = f.read()
    assert dasl_model_to_string(tpe) == expected_val


@pytest.mark.update
@pytest.mark.parametrize(
    "tpe",
    checked_dasl_types.keys(),
    ids=[f"updating {tpe.__name__} model" for tpe in checked_dasl_types.keys()],
)
def test_apply_api_model_changes(tpe):
    model_ser = dasl_model_to_string(tpe)
    with open(f"test/expected_api_models/{checked_dasl_types[tpe]}", "w") as f:
        f.write(model_ser)
