# -*- coding: utf-8 -*-
import math


ALLOWED_NAMES = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
ALLOWED_BUILTINS = {
    "_getattr_": getattr,
    "_getiter_": iter,
    "max": max,
    "min": min,
    "abs": abs,
    "len": len,
    "sum": sum,
    "any": any,
    "all": all,
    "sorted": sorted,
    "round": round,
}


class ExpressionatorException(Exception):
    """
    _summary_

    Args:
        Exception (_type_): _description_
    """


class ExpressionatorNamespace:
    """
    _summary_

    Raises:
        ExpressionatorException: _description_

    Returns:
        _type_: _description_
    """

    name = "_expr_"

    @property
    def safe_expr_namespace(self):
        """
        _summary_
        """
        return {
            func_name.replace(self.name, ""): getattr(self, func_name)
            for func_name in dir(self)
            if func_name.startswith(self.name)
        }
