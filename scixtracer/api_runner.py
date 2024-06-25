"""Implements runner utilities"""
from typing import Callable
from datetime import datetime
import functools

import numpy as np
import pandas as pd

from .models import URI
from .models import DataInfo
from .models import Job
from .models import StorageTypes
from .models import Location
from .models import Dataset
from .models import GROUP_SET
from .models import BatchItem
from .models import Batch

from .api import read_data
from .api import new_data
from .api import new_location
from .api import query_data
from .api import __storage

from .runner import SxRunner
from .factory import Factory
from .config import config


__runner: SxRunner = Factory(
    "sxt_", "runner").get(config().value("runner", "name"))()
if __runner is not None:
    __runner.storage = __storage
    __runner.connect(**config().filtered_section("runner"))


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


def __filter_inputs(inputs: list) -> [list, dict]:
    """Filter a job inputs to keep only the query"""
    query_inputs = []
    inputs_filtered = {}
    for i, input_ in enumerate(inputs):
        if isinstance(input_, dict):
            query_inputs.append(input_)
            inputs_filtered[i] = {"type": "query", "value": input_}
        else:
            inputs_filtered[i] = {"type": "value", "value": input_}
    return query_inputs, inputs_filtered


def __extract_type(type_annotation) -> StorageTypes:
    if type_annotation == np.ndarray:
        return StorageTypes.ARRAY
    if type_annotation == pd.DataFrame:
        return StorageTypes.TABLE
    if type_annotation == int or type_annotation == float \
        or type_annotation == bool:
        return StorageTypes.VALUE
    if type_annotation == str:
        return StorageTypes.LABEL


def __extract_out_types(func: Callable):
    out_types = func.__annotations__['return']
    out_dtypes = []
    if isinstance(out_types, list) or isinstance(out_types, tuple):
        for out in out_types:
            out_dtypes.append(__extract_type(out))
    else:
        out_dtypes.append(__extract_type(out_types))
    return out_dtypes


def __output_location(data_info: list[DataInfo] | DataInfo, func: Callable) -> Location:

    if isinstance(data_info, DataInfo):
        return data_info.location
    if len(data_info) == 1:
        return data_info[0].location

    need_new_location = False
    dataset = data_info[0].dataset
    location_id = data_info[0].location.uuid
    for d_info in data_info:
        if d_info.location.uuid != location_id:
            need_new_location = True
    if need_new_location:
        return new_location(dataset, annotations={"origin": func.__name__})
    return data_info[0].location


def __values_inputs(args_inputs: dict,
                    data_info: list[DataInfo] | DataInfo
                    ) -> list:

    data_inf = data_info
    if isinstance(data_info, DataInfo):
        data_inf = [data_info]

    out = []
    next_idx = 0
    for i, value in args_inputs.items():
        if value["type"] == "query":
            out.append(data_inf[next_idx])
            next_idx += 1
        else:
            out.append(value["value"])
    return out


def __values_inputs_group(args_inputs: dict,
                          data_info: list[DataInfo]
                          ) -> list:
    out = []
    next_idx = 0
    for i, value in args_inputs.items():
        if value["type"] == "query":
            in_dat = []
            for data_i in data_info[next_idx]:
                in_dat.append(data_i)
            out.append(in_dat)
            next_idx += 1
        else:
            out.append(value["value"])
    return out


def __serialize_inputs(values_inputs):
    out = []
    for val in values_inputs:
        if isinstance(val, list):
            out.append(__serialize_inputs(val))
        elif isinstance(val, DataInfo):
            out.append(val.uri.value)
        else:
            out.append(val)
    return out


def __batch_job(dataset, job: Job, run_id: str, job_id: str):
    """Run a job query to extract the job batch commands

    :param job: Job to run
    :param run_id: Identifier of the run the job belongs to
    :param job_id: Identifier of the job in the run
    """
    query_inputs, args_inputs = __filter_inputs(job.inputs)
    print("RUN query with ", query_inputs)
    data_info = query_data(dataset, query_inputs, job.query_type, True)
    out_types = __extract_out_types(job.func)
    ann = {"run_id": run_id, "job_id": job_id}

    batch = Batch()
    if job.query_type == GROUP_SET:
        loc = new_location(dataset, annotations={"origin": job.func.__name__})
        values_inputs = __values_inputs_group(args_inputs, data_info)
        values_inputs_json = __serialize_inputs(values_inputs)
        print('values_inputs_json=', values_inputs_json)
        out_info_s = []
        for i, out_type in enumerate(out_types):
            out_info = new_data(loc, out_type,
                                data_annotate=dict(ann, **job.outputs[i]),
                                metadata={
                                    "func": job.func.__name__,
                                    "inputs": values_inputs_json,
                                    "output_id": 0
                                })
            out_info_s.append(out_info)
        batch.append(BatchItem(func=job.func,
                               inputs=values_inputs,
                               outputs=out_info_s))
    else:
        for d_info in data_info:
            location = __output_location(d_info, job.func)
            values_inputs = __values_inputs(args_inputs, d_info)
            values_inputs_json = __serialize_inputs(values_inputs)
            out_info_s = []

            print("values inputs=", values_inputs)
            print("out_types=", out_types)
            print("values inputs json=", values_inputs_json)
            for i, out_type in enumerate(out_types):
                out_info = new_data(location, out_type,
                                    data_annotate=dict(ann, **job.outputs[i]),
                                    metadata={
                                        "func": job.func.__name__,
                                        "inputs": values_inputs_json,
                                        "output_id": 0
                                    })
                out_info_s.append(out_info)
            batch.append(BatchItem(func=job.func,
                                   inputs=values_inputs,
                                   outputs=out_info_s))
    return batch


def run(dataset: Dataset, jobs: list[Job]):
    """Execute the jobs

    :param dataset: Dataset to run the job on,
    :param jobs: List of jobs to run
    """
    run_id = str(datetime.now())
    batch_jobs = []
    for i, job in enumerate(jobs):
        batch_jobs.append(__batch_job(dataset, job, run_id, job_id=str(i)))

    # print
    for bat in batch_jobs:
        print("New job")
        for item in bat.items:
            print(item.func.__name__)
            print(item.inputs)
            print(item.outputs)
    __runner.run(batch_jobs)
