from copy import deepcopy
from typing import Any, Dict, List, Type
from rest_framework import serializers
from swifty.serializers.dynamic_serializer import DynamicSerializer
from swifty.serializers.fields import (
    BasicFieldSerializer,
    FIELD_TYPE_MAP,
)


def create_field_kwargs(
    field_info,
    field_type_map: Dict[str, BasicFieldSerializer] = deepcopy(FIELD_TYPE_MAP),
):
    """_summary_

    Args:
        field_info (_type_): _description_
        field_type_map (_type_): _description_

    Returns:
        _type_: _description_
    """
    field_base = field_type_map.get(field_info.get("type", "CharField"))

    if not issubclass(field_base, BasicFieldSerializer):
        return field_base, field_info

    allowed_args = field_base.static_args + field_base.extra_args
    allowed_kwargs = {}
    extra_kwargs = {}
    for k, v in field_info.items():
        if k in allowed_args:
            allowed_kwargs.update({k: v})
        else:
            extra_kwargs.update({k: v})

    return field_base, {"extra_kwargs": extra_kwargs, **allowed_kwargs}


def create_dynamic_serializer(
    fields_config: List[Dict[str, Any]],
    base_class: Type[DynamicSerializer] = DynamicSerializer,
    field_type_map: Dict[str, BasicFieldSerializer] = deepcopy(FIELD_TYPE_MAP),
) -> Type[DynamicSerializer]:
    """Create a dynamic serializer class based on field configuration.

    Args:
        field_config (List[Dict[str, Any]]): A list of dictionaries defining the fields.

    Returns:
        Type[DynamicSerializer]: A dynamically created serializer class.
    """
    fields: Dict[str, serializers.Field] = {}

    for field_info in fields_config:
        field_base, field_kwargs = create_field_kwargs(field_info, field_type_map)
        fields[field_info["field_name"]] = field_base(**field_kwargs)

    return type("DynamicSerializer", (base_class,), fields)
