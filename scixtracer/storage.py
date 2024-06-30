"""Definition of the main API methods"""
from abc import ABC, abstractmethod

from .models import Dataset
from .models import DataInfo
from .models import URI
from .models import StorageTypes
from .models import DataInstance


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

    @staticmethod
    @abstractmethod
    def array_types() -> tuple:
        """Array data types that the plugin can store

        :return: The list of types
        """

    @staticmethod
    @abstractmethod
    def table_types() -> tuple:
        """Table data types that the plugin can store

        :return: The list of types
        """

    @staticmethod
    @abstractmethod
    def value_types() -> tuple:
        """Value data types that the plugin can store

        :return: The list of types
        """

    @staticmethod
    @abstractmethod
    def label_types() -> tuple:
        """Label data types that the plugin can store

        :return: The list of types
        """

    @abstractmethod
    def create_tensor(self,
                      dataset: Dataset,
                      array: DataInstance = None,
                      shape: tuple[int, ...] = None
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
                     array: DataInstance
                     ):
        """Write new tensor data

        :param uri: Unique identifier of the data,
        :param array: Data content
        """

    @abstractmethod
    def read_tensor(self,
                    uri: URI
                    ) -> DataInstance:
        """Read a tensor from the dataset storage

        :param uri: Unique identifier of the data,
        :return: the read array
        """

    @abstractmethod
    def create_table(self, dataset: Dataset, table: DataInstance):
        """Write table data into storage

        :param dataset: Destination dataset,
        :param table: Data table to write
        """

    @abstractmethod
    def write_table(self, uri: URI, table: DataInstance):
        """Write table data into storage

        :param uri: Unique identifier of the data,
        :param table: Data table to write
        """

    @abstractmethod
    def read_table(self, uri: URI,) -> DataInstance:
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

    def delete(self, storage_type: StorageTypes, uri: URI):
        """Delete a data

        :param storage_type: Data storage type
        :param uri: Unique identifier of the data,
        """

    def read_data(self, data_info: DataInfo) -> DataInstance:
        """Read a tensor from the dataset storage

        :param data_info: Information of the data,
        :return: the read array
        """
        if data_info.storage_type == StorageTypes.ARRAY:
            return self.read_tensor(data_info.uri)
        if data_info.storage_type == StorageTypes.TABLE:
            return self.read_table(data_info.uri)
        if data_info.storage_type == StorageTypes.VALUE:
            return self.read_value(data_info.uri)
        if data_info.storage_type == StorageTypes.LABEL:
            return self.read_label(data_info.uri)
        raise ValueError('read_data: data type not recognized')

    def write_data(self,
                   data_info: DataInfo,
                   data: DataInstance,
                   ):
        """Write data to the storage

        :param data_info: Information of the data,
        :param data: The data to store
        """
        if data_info.storage_type == StorageTypes.ARRAY:
            return self.write_tensor(data_info.uri, data)
        if data_info.storage_type == StorageTypes.TABLE:
            return self.write_table(data_info.uri, data)
        if data_info.storage_type == StorageTypes.VALUE:
            return self.write_value(data_info.uri, data)
        if data_info.storage_type == StorageTypes.LABEL:
            return self.write_label(data_info.uri, data)
        raise ValueError('write_data: data type not recognized')
