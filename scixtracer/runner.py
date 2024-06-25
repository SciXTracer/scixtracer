"""Definition of the main API methods"""
from abc import ABC, abstractmethod

from .models import Batch
from .storage import SxStorage


class SxRunner(ABC):
    """Interface for storage interactions"""
    def __init__(self, storage: SxStorage = None):
        self.storage = storage

    @abstractmethod
    def connect(self, **kwargs):
        """Initialize any needed connection to the database"""

    @abstractmethod
    def run(self, batches: list[Batch]):
        """Execute a run defined as a list of batch

        :param batches: List of batches to run
        """