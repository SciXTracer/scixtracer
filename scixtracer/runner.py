"""Implements runner utilities"""
from typing import Callable
import functools

from .models import DataInfo
from .models import Dataset
from .models import Job
from .models import DataQueryType
from .api import read_data
from .api import new_data
from .api import new_location


def call(func: Callable):
    """Decorator to facilitate the data processing function call"""

    @functools.wraps(func)
    def wrapper_call(annotations: list[dict[str, any]],
                     *args):
        # Before
        arg_vals = []
        out_new_location = False
        ref_data = None
        metadata_inputs = []
        for value in args:
            if isinstance(value, DataInfo):
                metadata_inputs.append(value.uri.value)
                arg_vals.append(read_data(value))
                if ref_data is not None:
                    if ref_data.location.uuid != value.location.uuid:
                        out_new_location = True
                ref_data = value

            elif isinstance(value, list) and isinstance(value[0], DataInfo):
                metadata_list_inputs = []
                out_new_location = True
                ref_data = value[0]
                arg_val = []
                for dat in value:
                    arg_val.append(read_data(dat))
                    metadata_list_inputs.append(dat.uri.value)
                arg_vals.append(arg_val)
                metadata_inputs.append(metadata_list_inputs)
            else:
                arg_vals.append(value)
                metadata_inputs.append(str(value))

        # Call
        outputs = func(*arg_vals)

        # After
        if out_new_location:
            location = new_location(ref_data.location.dataset,
                                    annotations={"origin": func.__name__})
        else:
            location = ref_data.location
        if isinstance(outputs, list) or isinstance(outputs, tuple):
            for i, value in enumerate(outputs):
                ann = annotations[i]
                new_data(location,
                         value,
                         data_annotate=ann,
                         metadata={
                             "func": func.__name__,
                             "inputs": metadata_inputs,
                             "output_id": i
                         })
        else:
            if isinstance(annotations, list):
                ann = annotations[0]
            else:
                ann = annotations
            new_data(location,
                     outputs,
                     data_annotate=ann,
                     metadata={
                         "func": func.__name__,
                         "inputs": metadata_inputs,
                         "output_id": 0
                     })

    return wrapper_call


def run(jobs: list[Job]):
    """Execute the jobs

    :param jobs: List of jobs to run
    """