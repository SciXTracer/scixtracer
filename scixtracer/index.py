"""Definition of the main API methods"""
from abc import abstractmethod, ABC

import pandas as pd

from .models import StorageTypes
from .models import URI
from .models import Dataset
from .models import Location
from .models import DataInfo


class SxIndex(ABC):
    """Interface for dataset data indexation"""
    @abstractmethod
    def connect(self, **kwargs):
        """Initialize any needed connection to the database"""

    @abstractmethod
    def datasets(self) -> pd.DataFrame:
        """Get the list of available datasets

        :return: The info of available dataset in the workspace
        """

    @abstractmethod
    def new_dataset(self, name: str) -> Dataset:
        """Create a new dataset

        :param name: Title of the dataset
        """

    @abstractmethod
    def get_dataset(self, uri: URI) -> Dataset:
        """Read the information of a dataset

        :param uri: Unique identifier of the dataset
        """

    @abstractmethod
    def new_location(self,
                     dataset: Dataset,
                     annotations: dict[str, str | int | float | bool] = None
                     ) -> Location:
        """Create a new data location in the dataset

        :param dataset: Dataset to be edited,
        :param annotations: Annotations associated to the location,
        :return: The newly created location
        """

    @abstractmethod
    def annotate_location(self,
                          location: Location,
                          key: str,
                          value: str | int | float | bool):
        """Annotate a location with akey value pair

        :param location: Location to annotate,
        :param key: Annotation key,
        :param value: Annotation value
        """

    @abstractmethod
    def annotate_data(self,
                      data_info: DataInfo,
                      key: str,
                      value: str | int | float | bool):
        """Annotate a data

        :param data_info: Information of the data,
        :param key: Annotation key,
        :param value: Annotation value
        """

    @abstractmethod
    def create_data(self,
                    location: Dataset | Location,
                    uri: URI,
                    storage_type: StorageTypes,
                    annotations: dict[str, any] = None
                    ) -> DataInfo:
        """Create new data to a location

        :param location: Location where to save the data,
        :param uri: URI of the data,
        :param storage_type: Type of data to store,
        :param annotations: Annotations of the data with key value pairs,
        :return: The data information
        """

    @abstractmethod
    def query_data(self,
                   dataset: Dataset, *,
                   annotations: dict[str, any] = None,
                   locations: list[Location] = None
                   ) -> list[DataInfo]:
        """Retrieve data from a dataset

        :param dataset: Dataset to query,
        :param annotations: Query data that have the annotations,
        :param locations: Data at these locations
        """

    @abstractmethod
    def query_location(self,
                       dataset: Dataset,
                       annotations: dict[str, any] = None,
                       ) -> list[Location]:
        """Retrieve locations from a dataset

        :param dataset: Dataset to query,
        :param annotations: query locations that have the annotations,
        :return: Locations that correspond to the query
        """

    @abstractmethod
    def data_annotations(self, dataset: Dataset) -> dict[str, list[any]]:
        """Get all the data annotations in the datasets with their values

        :param dataset: Dataset to query,
        :return: Available annotations with their values
        """

    @abstractmethod
    def location_annotations(self, dataset: Dataset) -> dict[str, list[any]]:
        """Get all the location annotations in the datasets with their values

        :param dataset: Dataset to be queried,
        :return: Available locations with their values
        """

    @abstractmethod
    def view_locations(self, dataset: Dataset) -> pd.DataFrame:
        """Create a table to visualize the dataset locations structure

        :param dataset: Dataset to visualize
        :return: The data view as a table
        """

    @abstractmethod
    def view_data(self,
                  dataset: Dataset,
                  locations: list[Location] = None,
                  ) -> pd.DataFrame:
        """Create a table to visualize the dataset data structure

        :param dataset: Dataset to visualize
        :param locations: Locations to filter
        :return: The data view as a table
        """
