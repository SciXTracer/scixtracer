"""SciXTracer main module

usage:
import scixtracer as sx

sx.create_dataset("example")
...

"""
import importlib.metadata

from .config import config

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
from .api import new_tensor
from .api import write_tensor
from .api import read_tensor
from .api import new_table
from .api import write_table
from .api import read_table
from .api import new_value
from .api import write_value
from .api import read_value
from .api import new_label
from .api import write_label
from .api import read_label
from .api import query_data
from .api import query_location
from .api import data_annotations
from .api import location_annotations
from .api import view_locations
from .api import view_data

from .runner import call

from .models import URI, uri
from .models import Dataset
from .models import Metadata
from .models import Location
from .models import DataInfo
from .models import TensorRegion


__version__ = importlib.metadata.version("scixtracer")

__all__ = [
    "config",

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
    "new_tensor",
    "write_tensor",
    "read_tensor",
    "new_table",
    "write_table",
    "read_table",
    "new_value",
    "write_value",
    "read_value",
    "new_label",
    "write_label",
    "read_label",
    "query_data",
    "query_location",
    "data_annotations",
    "location_annotations",
    "view_locations",
    "view_data",

    "call",

    "URI",
    "uri",
    "Dataset",
    "Metadata",
    "Location",
    "DataInfo",
    "TensorRegion",
]
