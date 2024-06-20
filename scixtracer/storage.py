"""Definition of the main API methods"""
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from .models import Dataset
from .models import URI
from .models import TensorRegion


class SxStorage(ABC):
    """Interface for storage interactions"""
    @abstractmethod
    def connect(self, **kwargs):
        """Initialize any needed connection to the database"""

    @abstractmethod
    def init_dataset(self, dataset: Dataset):
        """Initialize the storage for a new dataset

        :param dataset: Dataset information
        """

    @abstractmethod
    def create_tensor(self,
                      dataset: Dataset,
                      array: np.ndarray = None,
                      shape: tuple[str, ...] = None
                      ):
        """Create a new tensor

        :param dataset: Destination dataset,
        :param array: Data content,
        :param shape: Shape of the tensor,
        :return: The information of the created data
        """

    @abstractmethod
    def write_tensor(self,
                     uri: URI,
                     array: np.ndarray,
                     region: TensorRegion = None
                     ):
        """Write new tensor data

        :param uri: Unique identifier of the data,
        :param array: Data content,
        :param region: Region of the tensor to write
        """

    @abstractmethod
    def read_tensor(self,
                    uri: URI,
                    region: TensorRegion = None
                    ) -> np.ndarray:
        """Read a tensor from the dataset storage

        :param uri: Unique identifier of the data,
        :param region: Region of the tensor to write,
        :return: the read array
        """

    @abstractmethod
    def create_table(self, dataset: Dataset, table: pd.DataFrame):
        """Write table data into storage

        :param dataset: Destination dataset,
        :param table: Data table to write
        """

    @abstractmethod
    def write_table(self, uri: URI, table: pd.DataFrame):
        """Write table data into storage

        :param uri: Unique identifier of the data,
        :param table: Data table to write
        """

    @abstractmethod
    def read_table(self, uri: URI,) -> pd.DataFrame:
        """Read a table from the dataset storage

        :param uri: Unique identifier of the data,
        :return: the read table
        """

    @abstractmethod
    def create_value(self, dataset: Dataset, value: float):
        """Write a value into storage

        :param dataset: Destination dataset,
        :param value: Value to write
        """

    @abstractmethod
    def write_value(self, uri: URI, value: float):
        """Write a value into storage

        :param uri: Unique identifier of the data,
        :param value: Value to write
        """

    @abstractmethod
    def read_value(self, uri: URI) -> float:
        """Read a value from the dataset storage

        :param uri: Unique identifier of the data,
        :return: the read value
        """

    @abstractmethod
    def create_label(self, dataset: Dataset, value: str):
        """Write a value into storage

        :param dataset: Destination dataset,
        :param value: Value to write
        """

    @abstractmethod
    def write_label(self, uri: URI, value: str):
        """Write a label into storage

        :param uri: Unique identifier of the data,
        :param value: Value to write
        """

    @abstractmethod
    def read_label(self, uri: URI) -> str:
        """Read a label from the dataset storage

        :param uri: Unique identifier of the data,
        :return: the read value
        """