"""Definition of the main API methods"""
from abc import ABC, abstractmethod

from .models import Dataset
from .models import URI


class SxMetadata(ABC):
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
    def create(self,
               dataset: Dataset,
               content: dict[str, any] = None,
               ) -> URI:
        """Create a new data metadata

        :param dataset: Destination dataset,
        :param content: Metadata content
        :return: The new data URI
        """

    @abstractmethod
    def read(self, uri: URI) -> dict[str, any]:
        """Read a data metadata

        :param uri: Unique identifier of the data,
        :return: the read content
        """

    @abstractmethod
    def write(self, uri: URI, content: dict[str, any]):
        """Write a data metadata into storage

        :param uri: Unique identifier of the data,
        :param content: Metadata to write
        """

    def delete(self, uri: URI):
        """Delete a data

        :param uri: Unique identifier of the data,
        """