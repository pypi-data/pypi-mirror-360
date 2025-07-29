"""Constants"""

import json
from typing import Dict, Tuple, Any
from datetime import date
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from swifty.expressionator.manager import ExpressionatorManager
from swifty.utils.helpers import validation_error_detail, json_handler
from swifty.serializers.constants import EMPTY_VALUES
from swifty.sqldb.core import Base


class BasicFieldSerializer:
    """
    _summary_

    Args:
        object (_type_): _description_
    """

    static_args = (
        "read_only",
        "write_only",
        "required",
        "default",
        "initial",
        "source",
        "label",
        "help_text",
        "style",
        "error_messages",
        "validators",
        "allow_null",
    )
    extra_args: Tuple[str, ...] = tuple()
    default: Any = None
    data = None
    default_empty_html = None

    def __init__(self, *args, extra_kwargs=None, required=None, **kwargs):
        self.extra_kwargs = extra_kwargs
        # Set the default value based on the presence of 'required'
        default = (
            kwargs.pop("default", self.default)
            if required
            else kwargs.get("default", self.default)
        )

        # Initialize the parent class with required
        super().__init__(*args, required=required, **kwargs)

        # Update the default if it was empty
        if self.default is empty:
            self.default = default

    def bind(self, field_name, parent):
        """_summary_

        Args:
            field_name (_type_): _description_
            parent (_type_): _description_
        """
        super().bind(field_name, parent)
        self.initiate_kwargs()

    @property
    def expressionator(self) -> ExpressionatorManager:
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """

        expressionator = (
            ExpressionatorManager
            if isinstance(self.root, BasicFieldSerializer)
            else getattr(self.root, "expressionator", ExpressionatorManager)
        )
        if callable(expressionator):
            return expressionator(data=getattr(self.root, "initial_data", {}))
        return expressionator

    def initiate_kwargs(self):
        """_summary_

        Args:
            data (_type_): _description_
        """
        initialator = self.extra_kwargs.get("initialator")
        if initialator:
            initial_attrs = (
                self.expressionator.initialator(initialization_data=initialator) or {}
            )
            field_args = self.static_args + self.extra_args
            for attr, value in initial_attrs.items():
                if attr in field_args:
                    setattr(self, attr, value)
                else:
                    self.extra_kwargs[attr] = value

    def is_disabled_by_rules(self, enabled_rules, value=empty):
        """_summary_

        Args:
            enabled_rules (_type_): _description_

        Returns:
            _type_: _description_
        """
        is_disabled = (
            self.extra_kwargs.get("disabled")
            or (enabled_rules and value in [None, empty])
            or False
        )
        if not is_disabled and isinstance(enabled_rules, (list, tuple)):
            for rule in enabled_rules:
                valid_values = rule.get("values")
                field_value = self.expressionator.get_value(rule.get("field_name"))
                if valid_values and field_value not in valid_values or not field_value:
                    return True
        return is_disabled

    def trigger_validator(self, validator, value):
        """_summary_

        Args:
            validator (_type_): _description_
            value (_type_): _description_

        Raises:
            ValidationError: _description_
        """
        is_valid = self.expressionator.validator(validation_data=validator, value=value)
        if not is_valid:
            raise ValidationError(detail=validator.get("default"))

        return value

    def validate_empty_value(self, value):
        """_summary_

        Args:
            value (_type_): _description_
        """

        if value in EMPTY_VALUES:
            return self.default

        return value

    def run_validation(self, value=empty):
        """_summary_

        Args:
            value (_type_, optional): _description_. Defaults to empty.

        Returns:
            _type_: _description_
        """

        if self.is_disabled_by_rules(
            enabled_rules=self.extra_kwargs.get("enabled_rules"), value=value
        ):
            return self.validate_empty_value(value=value)

        if (validator := self.extra_kwargs.get("validator")) and not (
            self.root.is_update
            and self.extra_kwargs.get("field_name") == self.root.pk_field
        ):
            self.trigger_validator(
                validator=validator,
                value=value,
            )

        return super().run_validation(self.validate_empty_value(value))

    def get_value(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.validate_empty_value(super().get_value(data))

    def to_representation(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        return super().to_representation(self.validate_empty_value(data))


class CharField(BasicFieldSerializer, serializers.CharField):
    """
    A serializer field for handling character (string) data.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "allow_blank",
        "trim_whitespace",
        "max_length",
        "min_length",
    )
    default: Any = ""

    def __init__(self, *args, required=None, **kwargs):
        super(CharField, self).__init__(
            *args, required=required, allow_blank=not required, **kwargs
        )


class EmailField(BasicFieldSerializer, serializers.EmailField):
    """
    A serializer field for handling email addresses.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "allow_blank",
        "trim_whitespace",
        "max_length",
        "min_length",
    )
    default: Any = ""


class URLField(BasicFieldSerializer, serializers.URLField):
    """
    A serializer field for handling URLs.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "allow_blank",
        "trim_whitespace",
        "max_length",
        "min_length",
    )
    default: Any = ""


class UUIDField(BasicFieldSerializer, serializers.UUIDField):
    """
    A serializer field for handling UUIDs.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "allow_blank",
        "trim_whitespace",
        "max_length",
        "min_length",
        "format",
        "hex_verbose",
    )
    default: Any = ""


class IntegerField(BasicFieldSerializer, serializers.IntegerField):
    """
    A serializer field for handling integers.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("max_value", "min_value")
    default: Any = 0


class FloatField(BasicFieldSerializer, serializers.FloatField):
    """
    A serializer field for handling floats.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("max_value", "min_value")
    default: Any = 0.0


class DecimalField(BasicFieldSerializer, serializers.DecimalField):
    """
    A serializer field for handling decimals.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "max_digits",
        "decimal_places",
        "coerce_to_string",
        "max_value",
        "min_value",
        "normalize_output",
        "localize",
        "rounding",
    )
    default: Any = 0.0


class BooleanField(BasicFieldSerializer, serializers.BooleanField):
    """
    A serializer field for handling booleans.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("allow_null",)
    default: Any = False


class DateField(BasicFieldSerializer, serializers.DateField):
    """
    A serializer field for handling dates.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("format", "input_formats")

    def __init__(self, *args, input_formats=None, **kwargs):
        input_formats = input_formats or ["iso-8601", "%Y-%m-%dT%H:%M:%S.%fZ"]
        self.initial = self.initial if self.initial is not None else date.today()
        super().__init__(*args, input_formats=input_formats, **kwargs)


class DateTimeField(BasicFieldSerializer, serializers.DateTimeField):
    """
    A serializer field for handling date-times.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("format", "input_formats", "default_timezone")


class DateRangeField(BasicFieldSerializer, serializers.DateTimeField):
    """
    A custom serializer field to handle a range of dates as a list with two items.
    Expects input in the format: ["YYYY-MM-DD", "YYYY-MM-DD"]
    Outputs a list of Python date objects: [start_date, end_date]
    """

    extra_args: Tuple[str, ...] = ("format", "input_formats", "default_timezone")

    def to_internal_value(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Raises:
            serializers.ValidationError: _description_

        Returns:
            _type_: _description_
        """
        if not isinstance(data, list) or len(data) != 2:
            raise serializers.ValidationError(
                detail="Date range must be a list with two dates: [start_date, end_date]."
            )

        start_date, end_date = data
        start_date = super().to_internal_value(start_date)
        end_date = super().to_internal_value(end_date)
        return [start_date, end_date]

    def to_representation(self, value):
        """_summary_

        Args:
            value (_type_): _description_

        Raises:
            TypeError: _description_

        Returns:
            _type_: _description_
        """
        if (
            not isinstance(value, list)
            or len(value) != 2
            or not all(isinstance(d, date) for d in value)
        ):
            raise TypeError("Value must be a list with two date objects.")

        start_date, end_date = value
        start_date = super().to_representation(start_date)
        end_date = super().to_representation(end_date)
        return [start_date, end_date]


class TimeField(BasicFieldSerializer, serializers.TimeField):
    """
    A serializer field for handling time values.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("format", "input_formats")


class DurationField(BasicFieldSerializer, serializers.DurationField):
    """
    A serializer field for handling duration values.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args = ("max_value", "min_value")


class ListField(BasicFieldSerializer, serializers.ListField):
    """
    A serializer field for handling lists.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("child", "allow_empty", "max_length", "min_length")
    default: Any = []


class DictField(BasicFieldSerializer, serializers.DictField):
    """
    A serializer field for handling dictionaries.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("child", "allow_empty")
    default: Any = {}


class ChoiceField(BasicFieldSerializer, serializers.ChoiceField):
    """
    A serializer field for handling choices.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "choices",
        "html_cutoff",
        "html_cutoff_text",
        "allow_blank",
    )

    def __init__(self, choices=None, **kwargs):
        choices = choices or ()
        super().__init__(choices=choices, **kwargs)


class MultipleChoiceField(BasicFieldSerializer, serializers.MultipleChoiceField):
    """
    A serializer field for handling ultiple choices.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args = (
        "choices",
        "html_cutoff",
        "html_cutoff_text",
        "allow_blank",
        "allow_empty",
    )
    default = []

    def __init__(self, choices=None, **kwargs):
        choices = choices or ()
        super().__init__(choices=choices, **kwargs)

    def to_internal_value(self, data):
        return list(super().to_internal_value(data))


class SlugField(BasicFieldSerializer, serializers.SlugField):
    """
    A serializer field for handling slugs.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("allow_unicode",)
    default: Any = ""


class FileField(BasicFieldSerializer, serializers.FileField):
    """
    A serializer field for handling file uploads.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("allow_empty_file", "use_url", "max_length")


class ImageField(BasicFieldSerializer, serializers.ImageField):
    """
    A serializer field for handling image uploads.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "allow_empty_file",
        "use_url",
        "max_length",
        "_DjangoImageField",
    )


class SerializerMethodField(BasicFieldSerializer, serializers.SerializerMethodField):
    """
    A serializer field for handling method-based fields.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("method_name", "source", "read_only")

    def to_internal_value(self, data):
        return data


class HyperlinkedIdentityField(
    BasicFieldSerializer, serializers.HyperlinkedIdentityField
):
    """
    A serializer field for handling hyperlinked identity.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "view_name",
        "lookup_field",
        "lookup_url_kwarg",
        "format",
        "read_only",
        "source",
    )


class HyperlinkedRelatedField(
    BasicFieldSerializer, serializers.HyperlinkedRelatedField
):
    """
    A serializer field for handling hyperlinked relations.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "view_name",
        "lookup_field",
        "lookup_url_kwarg",
        "format",
    )


class PrimaryKeyRelatedField(BasicFieldSerializer, serializers.PrimaryKeyRelatedField):
    """
    A serializer field for handling primary key relations.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "pk_field",
        "queryset",
        "many",
        "read_only",
        "html_cutoff",
        "html_cutoff_text",
    )


class RelatedField(BasicFieldSerializer, serializers.RelatedField):
    """
    A serializer field for handling related objects.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = (
        "queryset",
        "many",
        "read_only",
        "html_cutoff",
        "html_cutoff_text",
    )

    def to_internal_value(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        return data

    def to_representation(self, value):
        """_summary_

        Args:
            value (_type_): _description_

        Returns:
            _type_: _description_
        """
        return value


class JSONField(BasicFieldSerializer, serializers.JSONField):
    """
    A serializer field for handling JSON objects.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    extra_args: Tuple[str, ...] = ("binary", "encoder", "decoder")
    default: Any = {}


class ReadOnlyField(BasicFieldSerializer, serializers.ReadOnlyField):
    """
    A serializer field for read-only data.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    def to_internal_value(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        return data


class HiddenField(BasicFieldSerializer, serializers.HiddenField):
    """
    A serializer field for hidden data.

    Attributes:
        extra_args (Tuple[str, ...]): Extra arguments for the field configuration.
        default (Any): Default value for an empty field.
    """

    def to_representation(self, value):
        """_summary_

        Args:
            value (_type_): _description_

        Returns:
            _type_: _description_
        """
        return value


class SectionFieldException(Exception):
    """_summary_

    Args:
        Exception (_type_): _description_
    """

    def __init__(self, *args, field_path=None, error=None, **kwargs) -> None:
        self.field_path = field_path
        self.error = error
        super().__init__(*args, **kwargs)


class BaseSectionField(serializers.JSONField):
    """
    _summary_

    Args:
        JSONField (_type_): _description_
    """

    extra_args = ("binary", "encoder", "decoder", "section")
    extra_kwargs = None
    section = {}
    fields = {}

    def bind(self, field_name, parent):
        """_summary_

        Args:
            field_name (_type_): _description_
            parent (_type_): _description_
        """

        super().bind(field_name, parent)

        from swifty.serializers.manager import create_field_kwargs

        self.section = self.extra_kwargs and self.extra_kwargs.get("section", {})
        self.fields = {}
        for field_props in self.section.get("fields", []):
            field_name = field_props["field_name"]
            field_base, field_kwargs = create_field_kwargs(field_props)
            field_serializer = field_base(**field_kwargs)
            field_serializer.bind(parent=self, field_name=field_name)
            self.fields[field_name] = field_serializer

    def to_internal_value(self, data):
        """_summary_

        Args:
            data (_type_): _description_

        Raises:
            ValidationError: _description_

        Returns:
            _type_: _description_
        """
        # Recursively validate nested fields
        errors = {}
        if isinstance(data, dict) and isinstance(self.fields, dict):
            for key, value in data.items():
                try:
                    data[key] = self.fields[key].run_validation(value)
                except (ValidationError, DjangoValidationError) as error:
                    errors.update(
                        {key: ValidationError(detail=validation_error_detail(error))}
                    )
                except KeyError:
                    pass

        if errors:
            raise ValidationError(detail=validation_error_detail(errors))
        return json.loads(
            super().to_internal_value(json.dumps(data, default=json_handler))
        )

    def to_representation(self, data):
        if isinstance(data, Base):
            data = json.loads(json.dumps(data, default=json_handler))

        if isinstance(data, dict) and isinstance(self.fields, dict):
            for key, value in data.items():
                if key not in self.fields:
                    continue
                data[key] = self.fields[key].to_representation(value)

        return super().to_representation(data)


class SectionField(BasicFieldSerializer, BaseSectionField):
    """
    _summary_

    Args:
        JSONField (_type_): _description_
    """

    default = {}


class SectionManyField(BasicFieldSerializer, BaseSectionField):
    """
    _summary_

    Args:
        JSONField (_type_): _description_
    """

    default = []

    def to_internal_value(self, data_list):
        """_summary_

        Args:
            data_list (_type_): _description_

        Raises:
            ValidationError: _description_

        Returns:
            _type_: _description_
        """
        # Recursively validate nested fields
        cleaned_data = []
        errors = {}
        for data in data_list:
            if isinstance(data, dict):
                try:
                    cleaned_data.append(super().to_internal_value(data))
                except (ValidationError, DjangoValidationError) as error:
                    errors.update(
                        {
                            data_list.index(data): ValidationError(
                                detail=validation_error_detail(error)
                            )
                        }
                    )

        if errors:
            raise ValidationError(detail=validation_error_detail(errors))
        return cleaned_data

    def to_representation(self, data_list):
        """_summary_

        Args:
            data_list (_type_): _description_

        Returns:
            _type_: _description_
        """
        return [
            super(SectionManyField, self).to_representation(data) for data in data_list
        ]


FIELD_TYPE_MAP: Dict[str, BasicFieldSerializer] = {
    field_serializer.__name__: field_serializer
    for field_serializer in BasicFieldSerializer.__subclasses__()
}
