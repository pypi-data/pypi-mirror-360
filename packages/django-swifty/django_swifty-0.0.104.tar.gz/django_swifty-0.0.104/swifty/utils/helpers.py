from collections.abc import Callable, Mapping
import json
from datetime import date, datetime, time
from decimal import Decimal
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.functional import Promise
from sqlalchemy.engine.row import Row

from swifty.sqldb.core import Base

ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def json_handler(obj):
    """
    Custom JSON serializer for handling various data types.

    Args:
        obj (any): The object to serialize.

    Returns:
        any: Serialized representation of the object.
    """

    try:
        # Handle callable objects
        if isinstance(obj, Callable):
            obj = obj()

        # Custom serialization for specific types
        handlers = [
            (lambda x: callable(getattr(x, "to_json", None)), lambda x: x.to_json()),
            (lambda x: isinstance(x, set), list),
            (lambda x: isinstance(x, Row), dict),
            (lambda x: isinstance(x, Base), lambda x: x.as_dict()),
            (
                lambda x: isinstance(x, datetime),
                lambda x: x.strftime(ISO_DATETIME_FORMAT),
            ),
            (lambda x: isinstance(x, date), lambda x: x.isoformat()),
            (lambda x: isinstance(x, time), lambda x: x.strftime("%H:%M:%S")),
            (lambda x: isinstance(x, Decimal), float),  # Warning: Precision loss
            (lambda x: isinstance(x, Promise), force_str),  # For lazy translations
        ]

        for condition, action in handlers:
            if condition(obj):
                return action(obj)

        # Fallback to the default JSONEncoder
        return json.JSONEncoder().default(obj)

    except Exception:
        return None


def is_any_nested_item_in_list(items, check_list):
    """_summary_

    Args:
        items (_type_): _description_
        check_list (_type_): _description_
    """
    for item in items:
        if item in check_list:
            return True
    return False


def to_raw_dict(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    return (
        json.loads(json.dumps(data, default=json_handler))
        if not isinstance(data, dict)
        else data
    )


def map_calculated_data(path, result, data, many=False):
    """_summary_

    Args:
        path (_type_): _description_
        result (_type_): _description_
        data (_type_): _description_
        many (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    primary_path, *secondary_path = path.split(".")
    if not secondary_path:
        data[primary_path] = result
    else:
        secondary_path = secondary_path[0]
        if many and isinstance(result, dict):
            for index, sub_result in result.items():
                data[primary_path][index][secondary_path] = sub_result
        else:
            data[primary_path][secondary_path] = result
    return data


def validation_error_detail(exc):
    """_summary_

    Args:
        exc (_type_): _description_

    Returns:
        _type_: _description_
    """
    if isinstance(exc, ValidationError):
        return exc.detail

    if isinstance(exc, DjangoValidationError):
        return get_error_detail(exc)

    if isinstance(exc, Mapping):
        # If errors may be a dict we use the standard {key: list of values}.
        # Here we ensure that all the values are *lists* of errors.
        return {key: validation_error_detail(value) for key, value in exc.items()}
    elif isinstance(exc, list):
        # Errors raised as a list are non-field errors.
        return {exc.index(value): validation_error_detail(value) for value in exc}
    # Errors raised as a string are non-field errors.
    return {api_settings.NON_FIELD_ERRORS_KEY: [exc]}


def get_fields_config(fields):
    """Return the fields configuration as a dictionary.

    Returns:
        Dict[str, Any]: A dictionary representation of the fields configuration.
    """
    fields_config = {}
    for field_name, field in (fields or {}).items():
        allowed_args = getattr(field, "static_args", ()) + getattr(
            field, "extra_args", ()
        )
        allowed_kwargs = {
            attr: getattr(field, attr) for attr in dir(field) if attr in allowed_args
        }
        fields_config[field_name] = {
            "field_name": field_name,
            "type": field.__class__.__name__,
            **allowed_kwargs,
            **getattr(field, "extra_kwargs", {}),
        }

        if hasattr(field, "fields"):
            fields_config[field_name]["section"].update(
                {"fields": get_fields_config(field.fields)}
            )

    return fields_config
