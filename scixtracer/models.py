"""Module to define the data models used by sciXtracer"""
from typing import Callable
from enum import StrEnum
from pathlib import Path
import json

from pydantic import BaseModel


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


DataInstance = any


class Metadata:
    """Store the metadata of a single data"""
    def __init__(self, value: dict[str, any]):
        self.value = value

    def __getitem__(self, item):
        if item in self.value:
            return self.value[item]
        raise ValueError(f"Key {item} not found in metadata")

    def items(self) -> list[str]:
        """Get the keys available in the metadata"""
        return list(self.value.keys())


class Data:
    """Container for both the data info and value"""
    def __init__(self,
                 info: DataInfo,
                 metadata: Metadata,
                 value: DataInstance):
        self.__info = info
        self.__metadata = metadata
        self.__value = value

    @property
    def info(self) -> DataInfo:
        return self.__info.info

    @property
    def metadata(self) -> Metadata:
        return self.__metadata

    @property
    def value(self) -> DataInstance:
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
    func: Callable
    inputs: list[dict[str, str] | float | int | bool | str]
    outputs: list[dict[str, str] | float | int | bool | str]
    query_type: DataQueryType = DataQueryType.SINGLE


def job(func: Callable,
        inputs: list[dict[str, str] | float | int | bool] | str,
        outputs: list[dict[str, str] | float | int | bool | str],
        query_type: DataQueryType = DataQueryType.SINGLE
        ) -> Job:
    """Create new job info

    :param func: Function to run,
    :param inputs: Queries for each input,
    :param outputs: Annotations for each output,
    :param query_type: Type of query to apply for the inputs
    """
    return Job(func=func,
               inputs=inputs,
               outputs=outputs,
               query_type=query_type)
