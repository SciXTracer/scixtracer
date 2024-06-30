"""SciXTracer main module

usage:
import scixtracer as sx

sx.create_dataset("example")
...

"""
import importlib.metadata

from .config import config

from .api import datasets
from .api import new_dataset
from .api import get_dataset
from .api import set_description
from .api import get_description
from .api import new_location
from .api import annotate_location
from .api import annotate_data
from .api import new_data
from .api import read_data
from .api import write_data
from .api import new_data_index
from .api import query_data
from .api import query_location
from .api import query_data_annotation
from .api import query_location_annotation
from .api import view_locations
from .api import view_data
from .api import delete
from .api import delete_query

from .api_runner import call
from .api_runner import run

from .models import StorageTypes
from .models import URI, uri
from .models import Dataset
from .models import Location
from .models import DataInfo
from .models import DataInstance
from .models import Data
from .models import DataQueryType
from .models import SINGLE
from .models import LOC_SET
from .models import GROUP_SET
from .models import Job
from .models import job
from .models import BatchItem
from .models import Batch


__version__ = importlib.metadata.version("scixtracer")

__all__ = [
    "config",

    "datasets",
    "new_dataset",
    "get_dataset",
    "set_description",
    "get_description",
    "new_location",
    "annotate_location",
    "annotate_data",
    "new_data_index",
    "new_data",
    "read_data",
    "write_data",
    "DataQueryType",
    "query_data",
    "query_location",
    "query_data_annotation",
    "query_location_annotation",
    "view_locations",
    "view_data",
    "delete",
    "delete_query",

    "call",
    "run",

    "SorageTypes"
    "URI",
    "uri",
    "Dataset",
    "Location",
    "DataInfo",
    "DataInstance",
    "Data",
    "SINGLE",
    "LOC_SET",
    "GROUP_SET",
    "Job",
    "job",
    "BatchItem",
    "Batch"
]
