"""Implements runner utilities"""
from typing import Callable
import functools

from .models import DataInfo
from .api import read_data
from .api import new_data


def call(func: Callable):
    """Decorator to facilitate the data processing function call"""
    @functools.wraps(func)
    def wrapper_call(annotations: list[dict[str, any]],
                     *args):
        arg_vals = []
        ref_data = None
        for value in args:
            if isinstance(value, DataInfo):
                arg_vals.append(read_data(value))
                if ref_data is None:
                    ref_data = value
            else:
                arg_vals.append(value)
        outputs = func(*arg_vals)
        if isinstance(outputs, list):
            for i, value in enumerate(outputs):
                new_data(ref_data.location, value,
                         data_annotate=annotations[i])
        else:
            new_data(ref_data.location, outputs,
                     data_annotate=annotations[0])
    return wrapper_call
