# -*- coding: utf-8 -*-
from RestrictedPython import compile_restricted, safe_globals
from swifty.expressionator.namespace import (
    ExpressionatorNamespace,
    ExpressionatorException,
    ALLOWED_BUILTINS,
    ALLOWED_NAMES,
)
from swifty.logging.logger import SwiftyLoggerMixin
from swifty.utils.objects import DictObject


class ExpressionatorManager(SwiftyLoggerMixin):
    """_summary_

    Raises:
        error: _description_
        ExpressionatorException: _description_

    Returns:
        _type_: _description_
    """

    expressionator_namespace = None
    data = None
    __expr_data = None

    def __init__(self, data=None, namespace=ExpressionatorNamespace) -> None:
        """_summary_

        Args:
            data (_type_, optional): _description_. Defaults to None.
        """
        self.expr_data = data or {}
        self.safe_expr_namespace = namespace().safe_expr_namespace or {}
        self.safe_locals = {
            **ALLOWED_NAMES,
            **ALLOWED_BUILTINS,
            **self.expr_data,
            **self.safe_expr_namespace,
        }

    @property
    def expr_data(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.__expr_data

    @expr_data.setter
    def expr_data(self, data):
        if isinstance(data, DictObject):
            self.__expr_data = data
        elif isinstance(data, dict):
            self.__expr_data = DictObject(dict_data=data)
        else:
            raise ExpressionatorException("Invalid formatted data")

    def __expressionator(self, expression, default=None, strict=False):
        """
        _summary_

        Args:
            expression (_type_): _description_

        Raises:
            error: _description_

        Returns:
            _type_: _description_
        """
        try:
            default = self.evaluate(expression)
        except (ExpressionatorException, NameError) as error:
            self.logger.error(
                "An error occurred before evaluating the expression",
                expression=expression,
                default=default,
                error=error,
            )
        except Exception as error:
            self.logger.error(
                "An error occurred when evaluating the expression",
                expression=expression,
                default=default,
                error=error,
            )
            if strict:
                raise error
        return default

    def get_value(self, field_name):
        """
        _summary_

        Args:
            field_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        return self.__expressionator(expression=field_name)

    def initialator(
        self,
        initialization_data,
    ):
        """
        _summary_

        Args:
            initialization_data (_type_): _description_

        Returns:
            _type_: _description_
        """
        expression = initialization_data.get("expression")
        default = initialization_data.get("default")
        return self.__expressionator(expression=expression, default=default)

    def calculator(self, calculation_data, data=None):
        """_summary_

        Args:
            calculation_data (_type_): _description_
            data (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if data is not None:
            self.expr_data = data
            self.safe_locals.update(self.expr_data)
        expression = calculation_data.get("expression")
        default = calculation_data.get("default")
        return self.__expressionator(expression=expression, default=default)

    def validator(self, validation_data, value):
        """_summary_

        Args:
            validation_data (_type_): _description_
            value (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.safe_locals.update({"value": value})
        expression = validation_data.get("expression")
        return self.__expressionator(expression=expression, default=False)

    def evaluate(self, expression):
        """
        Evaluate a math expression.

        Args:
            expression (_type_): _description_

        Raises:
            ExpressionatorException: _description_

        Returns:
            _type_: _description_
        """
        # Compile the expression
        code = compile_restricted(expression, "<string>", "eval")

        # Validate allowed names
        for name in code.co_names:
            if name not in self.safe_locals:
                raise ExpressionatorException(f"The use of '{name}' is not allowed")

        return eval(code, safe_globals, self.safe_locals)
