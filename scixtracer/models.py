"""Module to define the data models used by sciXtracer"""
from typing import Callable
from enum import StrEnum
from pathlib import Path

import pandas as pd
from pydantic import BaseModel
import numpy as np


DataValue = np.ndarray | pd.DataFrame | float | str


class StorageTypes(StrEnum):
    """Available data type in the storage"""
    ARRAY = "Array"
    TABLE = "Table"
    VALUE = "Value"
    LABEL = "Label"


class URI(BaseModel):
    """Unique identifier of a data (eg path)"""
    value: str

    def __str__(self):
        return self.value


def uri(value: str | Path):
    """Utility to create a URI

    :param value: Value of the URI
    """
    return URI(value=str(value))


class Dataset(BaseModel):
    """Information about a dataset"""
    name: str
    uri: URI
    metadata_uri: URI = None


class Location(BaseModel):
    """Information of a dataset location"""
    dataset: Dataset
    uuid: int


class DataInfo(BaseModel):
    """Information about one data in a project"""
    location: Location
    storage_type: StorageTypes
    uri: URI
    metadata_uri: URI

    @property
    def dataset(self) -> Dataset:
        """Get the project"""
        return self.location.dataset


class Data:
    """Container for both the data info and value"""
    def __init__(self, info: DataInfo, value: DataValue):
        self.__info = info
        self.__value = value

    @property
    def info(self) -> DataInfo:
        return self.__info

    @property
    def value(self) -> DataValue:
        return self.__value


SINGLE = "single"
LOC_SET = "loc_set"
GROUP_SET = "group_set"


class DataQueryType(StrEnum):
    """Define the possible types of a query"""
    SINGLE = "single"
    LOC_SET = "loc_set"
    GROUP_SET = "group_set"


class Job(BaseModel):
    """Container for a job description"""
    dataset: Dataset
    func: Callable
    inputs: list[dict[str, str | float | int | bool]]
    outputs: list[dict[str, str | float | int | bool]]
    query_type: DataQueryType


def job(dataset: Dataset,
        func: Callable,
        inputs: list[dict[str, str | float | int | bool]],
        outputs: list[dict[str, str | float | int | bool]],
        query_type: DataQueryType = DataQueryType.SINGLE
        ) -> Job:
    """Create new job info

    :param dataset: Dataset to query
    :param func: Function to run,
    :param inputs: Queries for each input,
    :param outputs: Annotations for each output,
    :param query_type: Type of query to apply for the inputs
    """
    return Job(dataset=dataset,
               func=func,
               inputs=inputs,
               outputs=outputs,
               query_type=query_type)


class TensorRegion:
    """Definition of a tensor region"""
    def __init__(self, *,
                 indexes: list[tuple[int, int] | None] = None,
                 ):
        self.__indexes = indexes

    @property
    def indexes(self) -> list[tuple[int, int] | None]:
        """Get the region indexes"""
        return self.__indexes

    @staticmethod
    def __format_range(range_value: tuple[int, int] | None,
                       shape: int) -> tuple[int, int]:
        if range_value is None:
            return 0, shape
        return range_value

    def extract_region(self, array: np.array) -> np.array:
        """Extract the region from an array

        :param array: Array to process,
        :return: a processed array
        """
        if array.ndim != len(self.__indexes):
            raise ValueError('Indexes are not coherent with tensor dim')
        if array.ndim == 2:
            min_x, max_x = self.__format_range(self.__indexes[0],
                                               array.shape[0])
            min_y, max_y = self.__format_range(self.__indexes[0],
                                               array.shape[0])
            return array[min_x:max_x, min_y:max_y]
        raise ValueError(f'Not yet implemented for array dim!=2, '
                         f'dim={array.ndim}')
