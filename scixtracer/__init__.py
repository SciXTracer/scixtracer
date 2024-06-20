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
from .api import new_data_index
from .api import query_data
from .api import query_data_tuples
from .api import query_data_sets
from .api import query_location
from .api import data_annotations
from .api import location_annotations
from .api import view_locations
from .api import view_data

from .runner import call

from .models import URI, uri
from .models import Dataset
from .models import Location
from .models import DataInfo
from .models import TensorRegion


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
    "query_data",
    "query_data_tuples",
    "query_data_sets",
    "query_location",
    "data_annotations",
    "location_annotations",
    "view_locations",
    "view_data",

    "call",

    "URI",
    "uri",
    "Dataset",
    "Location",
    "DataInfo",
    "TensorRegion",
]
