"""
This module provides a monkey patch for the inspect module to replace
the deprecated getargspec function with a compatible alternative using
signature.
"""

import inspect
from collections import namedtuple

# Save the original getargspec function
original_getargspec = inspect.getargspec

# Define a custom named tuple to mimic the FullArgSpec structure
FullArgSpec = namedtuple(
    "FullArgSpec",
    [
        "args",
        "varargs",
        "varkw",
        "defaults",
        "kwonlyargs",
        "kwonlydefaults",
        "annotations",
    ],
)


# Create a replacement function for getargspec
def patched_getargspec(func):
    """Return a FullArgSpec for the given function."""
    signature = inspect.signature(func)

    # Extract the positional arguments and keyword-only arguments
    args = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect.Parameter.empty
    ]
    kwonlyargs = [
        param.name
        for param in signature.parameters.values()
        if param.default != inspect.Parameter.empty
        and param.kind == inspect.Parameter.KEYWORD_ONLY
    ]

    # Build the FullArgSpec object with the necessary information
    return FullArgSpec(
        args=args,
        varargs=None,
        varkw=None,
        defaults=None,
        kwonlyargs=kwonlyargs,
        kwonlydefaults=None,
        annotations={
            param.name: param.annotation
            for param in signature.parameters.values()
            if param.annotation is not inspect.Parameter.empty
        },
    )


# Apply the monkey patch
inspect.getargspec = patched_getargspec
print("Monkey patch applied: getargspec is now using signature.")
