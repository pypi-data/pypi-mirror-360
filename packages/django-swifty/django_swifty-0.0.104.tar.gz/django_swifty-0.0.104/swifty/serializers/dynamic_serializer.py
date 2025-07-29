"""Module for dynamic serializers using Django REST Framework."""

import json
from copy import deepcopy
from typing import Any, Dict

from rest_framework import serializers

from swifty.expressionator.manager import ExpressionatorManager
from swifty.expressionator.namespace import ExpressionatorNamespace
from swifty.utils.helpers import (
    is_any_nested_item_in_list,
    map_calculated_data,
    get_fields_config,
    json_handler,
)


class DynamicSerializer(serializers.Serializer):
    """Base class for dynamic serializers."""

    namespace = ExpressionatorNamespace
    calculators = None
    pk_field = None
    is_update = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_calcualtors()
        data = kwargs.get("data")
        if isinstance(data, dict) and "pk_field" in data:
            self.pk_field = kwargs.get("data").get("pk_field")

    def expressionator(self, data=None):
        """_summary_

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
        return ExpressionatorManager(data=data, namespace=self.namespace)

    def create(self, *args, **kwargs) -> Any:
        """Create an instance based on validated data."""

    def update(self, *args, **kwargs) -> Any:
        """Update an instance based on validated data."""

    def _get_calculators(
        self,
        field,
        path,
        parent_path=None,
        many=False,
    ):
        """_summary_

        Args:
            field (_type_): _description_
            path (_type_): _description_
            parent_path (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        field_calculator = field.extra_kwargs.get("calculator")
        return (
            field_calculator
            and {
                str(path if not parent_path else f"{parent_path}.{path}"): many
                and field_calculator.update({"many": many})
                or field_calculator
            }
            or {}
        )

    def set_calcualtors(self):
        """_summary_

        Args:
            field_serializer (_type_): _description_
            input_type (_type_): _description_
        """
        self.calculators = {}
        for field_name, field in self.fields.items():

            if field.__class__.__name__ in ["SectionField", "SectionManyField"]:
                for sub_field in field.fields.values():
                    self.calculators.update(
                        self._get_calculators(
                            sub_field,
                            path=sub_field.field_name,
                            parent_path=field_name,
                            many=field.__class__.__name__ == "SectionManyField",
                        )
                    )
            else:
                self.calculators.update(self._get_calculators(field, path=field_name))

    def is_valid(self, *, raise_exception=False):
        """_summary_

        Args:
            raise_exception (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if self.initial_data and self.calculators:
            self.initial_data = self.calculate_data(initial_data=self.initial_data)
        return super().is_valid(raise_exception=raise_exception)

    def to_representation(self, instance):
        """_summary_

        Args:
            instance (_type_): _description_

        Returns:
            _type_: _description_
        """
        data = super().to_representation(instance)
        if self.calculators:
            data = self.calculate_data(
                initial_data=json.loads(json.dumps(data, default=json_handler))
            )
        return data

    def calculate_data(self, initial_data):
        """
        Calculates and returns processed data.

        Returns:
            dict: Processed data with calculations applied.
        """
        data = deepcopy(initial_data)
        expressionator = self.expressionator(data=data)
        calculators = deepcopy(self.calculators or {})
        temp_calculators = deepcopy(calculators)
        force_calculation = False

        while temp_calculators:
            for field_path, calculator in list(calculators.items()):
                triggered_fields = calculator.get("triggers_on", [])
                if force_calculation or not is_any_nested_item_in_list(
                    triggered_fields, calculators.keys()
                ):
                    result = expressionator.calculator(calculator, data=data)
                    data = map_calculated_data(
                        path=field_path,
                        result=result,
                        data=data,
                        many=calculator.get("many"),
                    )
                    temp_calculators.pop(field_path)

            if len(calculators) == len(temp_calculators):
                force_calculation = True
            else:
                calculators = deepcopy(temp_calculators)

        return data

    def get_fields_config(self) -> Dict[str, Any]:
        """Return the fields configuration as a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the fields configuration.
        """
        return get_fields_config(self.fields)
