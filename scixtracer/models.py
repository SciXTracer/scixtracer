"""Module to define the data models used by sciXtracer"""
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel
import numpy as np


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
    doc_uri: URI = None


class Metadata(BaseModel):
    """Container for any metadata (doc)"""
    value: dict[str, str]


class Location(BaseModel):
    """Information of a dataset location"""
    dataset: Dataset
    uuid: int


class DataInfo(BaseModel):
    """Information about one data in a project"""
    location: Location
    storage_type: StorageTypes
    uri: URI

    @property
    def dataset(self) -> Dataset:
        """Get the project"""
        return self.location.dataset


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
