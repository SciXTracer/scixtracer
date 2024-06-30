"""Module to define the data models used by sciXtracer"""
from typing import Callable
from enum import StrEnum
from pathlib import Path

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
        """Data info property"""
        return self.__info.info

    @property
    def metadata(self) -> Metadata:
        """Metadata property"""
        return self.__metadata

    @property
    def value(self) -> DataInstance:
        """Data instance property"""
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


class BatchItem:
    """Container for one function run"""
    def __init__(self,
                 func: Callable,
                 inputs: list[DataInfo | float | int | str | bool],
                 outputs: list[DataInfo]):
        self.__func = func
        self.__inputs = inputs
        self.__outputs = outputs

    @property
    def func(self):
        """Function property"""
        return self.__func

    @property
    def inputs(self):
        """Inputs property"""
        return self.__inputs

    @property
    def outputs(self):
        """Outputs property"""
        return self.__outputs


class Batch:
    """Container for a batch run"""
    def __init__(self):
        self.items = []

    def append(self, item: BatchItem):
        """Add a batch item

        :param item: Item to add
        """
        self.items.append(item)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]
