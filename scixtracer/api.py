"""Definition of the main API methods"""

import numpy as np
import pandas as pd

from .models import StorageTypes
from .models import URI
from .models import Dataset
from .models import Metadata
from .models import Location
from .models import DataInfo
from .models import TensorRegion

from .logger import logger
from .config import config, config_file
from .factory import Factory
from .index import SxIndex
from .storage import SxStorage


# Initialize the config and the backend plugins
cfile = config_file()
logger().set_prefix("SciXtracer")
logger().info(f"use config file: {cfile}")
config(cfile)  # init singleton
__index: SxIndex = Factory("sxt_", "index").get(config().value("index",
                                                               "name"))()
if __index is not None:
    __index.connect(**config().filtered_section("index"))

__storage: SxStorage = Factory("sxt_", "storage").get(config().value("storage",
                                                                     "name"))()
if __storage is not None:
    __storage.connect(**config().filtered_section("storage"))


def datasets() -> pd.DataFrame:
    """Get the list of available datasets

    :return: The info of available dataset in the workspace
    """
    return __index.datasets()


def new_dataset(name: str) -> Dataset:
    """Create a new dataset

    :param name: Title of the dataset
    """
    dataset_info = __index.new_dataset(name)
    __storage.init_dataset(dataset_info)
    return dataset_info


def get_dataset(uri: URI) -> Dataset:
    """Read the information of a dataset
    
    :param uri: Unique identifier of the dataset
    """
    return __index.get_dataset(uri)


def set_description(dataset: Dataset, metadata: Metadata):
    """Write metadata to a dataset
    
    :param dataset: Information of the dataset,
    :param metadata: Metadata to set
    """
    raise NotImplementedError()


def get_description(dataset: Dataset) -> Metadata:
    """Read the metadata of a dataset
    
    :param dataset: Information of the dataset,
    :return: The dataset metadata
    """
    raise NotImplementedError()


def new_location(dataset: Dataset,
                 annotations: dict[str, str | int | float | bool] = None
                 ) -> Location:
    """Create a new data location in the dataset
    
    :param dataset: Dataset to be edited,
    :param annotations: Annotations associated to the location
    :return: The newly created location
    """
    return __index.new_location(dataset, annotations)


def annotate_location(location: Location,
                      key: str,
                      value: str | int | float | bool):
    """Annotate a location with akey value pair
    
    :param location: Location to annotate,
    :param key: Annotation key,
    :param value: Annotation value
    """
    return __index.annotate_location(location, key, value)


def annotate_data(data_info: DataInfo,
                  key: str,
                  value: str | int | float | bool):
    """Annotate a data
    
    :param data_info: Information of the data,
    :param key: Annotation key,
    :param value: Annotation value
    """
    return __index.annotate_data(data_info, key, value)


def new_data_index(location: Dataset | Location,
                   uri: URI,
                   storage_type: StorageTypes,
                   annotations: dict[str, any] = None
                   ) -> DataInfo:
    """Create new data index to a location
    
    :param location: Location where to save the data,
    :param uri: URI of the data,
    :param storage_type: Type of data to store,
    :param annotations: Annotations of the data with key value pairs,
    :return: The data information
    """
    return __index.create_data(location, uri, storage_type, annotations)


def __get_location(location: Dataset | Location,
                   annotations: dict[str, any] = None) -> Location:
    """Create a location if location is dataset

    :param location: Dataset or location to write,
    :return: The data location
    """
    if isinstance(location, Dataset):
        return new_location(location, annotations)
    return location


def new_data(location: Dataset | Location,
             data: np.ndarray | pd.DataFrame | float | str,
             *,
             loc_annotate: dict[str, any] = None,
             data_annotate: dict[str, any] = None
             ) -> DataInfo:
    """Create new data

    :param location: Dataset or location to write,
    :param data: Data content,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :return: The information of the created data
    """
    if isinstance(data, np.ndarray):
        return new_tensor(location, array=data,
                          loc_annotate=loc_annotate,
                          data_annotate=data_annotate)
    if isinstance(data, pd.DataFrame):
        return new_table(location, data,
                         loc_annotate=loc_annotate,
                         data_annotate=data_annotate)
    if isinstance(data, float):
        return new_value(location, data,
                         loc_annotate=loc_annotate,
                         data_annotate=data_annotate)
    if isinstance(data, str):
        return new_label(location, data,
                         loc_annotate=loc_annotate,
                         data_annotate=data_annotate)
    raise ValueError('new_data: data type not recognized')


def read_data(data_info: DataInfo
              ) -> np.ndarray | pd.DataFrame | float | str:
    """Read a tensor from the dataset storage

    :param data_info: Information of the data,
    :return: the read array
    """
    if data_info.storage_type == StorageTypes.ARRAY:
        return read_tensor(data_info)
    if data_info.storage_type == StorageTypes.TABLE:
        return read_table(data_info)
    if data_info.storage_type == StorageTypes.VALUE:
        return read_value(data_info)
    if data_info.storage_type == StorageTypes.LABEL:
        return read_label(data_info)
    raise ValueError('read_data: data type not recognized')


def new_tensor(location: Dataset | Location, *,
               array: np.ndarray = None,
               shape: tuple[str, ...] = None,
               loc_annotate: dict[str, any] = None,
               data_annotate: dict[str, any] = None
               ) -> DataInfo:
    """Create a new tensor

    :param location: Dataset or location to write,
    :param array: Data content,
    :param shape: Shape of the tensor,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :return: The information of the created data
    """
    loc = __get_location(location, loc_annotate)
    data_uri = __storage.create_tensor(loc.dataset, array, shape)
    data_info = __index.create_data(loc, data_uri, StorageTypes.ARRAY,
                                    data_annotate)
    return data_info


def write_tensor(data_info: DataInfo,
                 array: np.ndarray,
                 region: TensorRegion = None
                 ) -> DataInfo:
    """Write new tensor data
    
    :param data_info: Information of the data,
    :param array: Data content,
    :param region: Region of the tensor to write
    """
    return __storage.write_tensor(data_info.uri, array, region)


def read_tensor(data_info: DataInfo,
                region: TensorRegion = None
                ) -> np.ndarray:
    """Read a tensor from the dataset storage
    
    :param data_info: Information of the data,
    :param region: Region of the tensor to write,
    :return: the read array
    """
    return __storage.read_tensor(data_info.uri, region)


def new_table(location: Dataset | Location,
              table: pd.DataFrame, *,
              loc_annotate: dict[str, any] = None,
              data_annotate: dict[str, any] = None
              ) -> DataInfo:
    """Write new table data
    
    :param location: Dataset or location to write,
    :param table: Data content,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :return: The data information
    """
    loc = __get_location(location, loc_annotate)
    data_uri = __storage.create_table(loc.dataset, table)
    data_info = __index.create_data(loc, data_uri, StorageTypes.TABLE,
                                    data_annotate)
    return data_info


def write_table(data_info: DataInfo, table: pd.DataFrame):
    """Write table data into storage
    
    :param data_info: Information of the data,
    :param table: Data table to write
    """
    __storage.write_table(data_info.uri, table)


def read_table(data_info: DataInfo) -> pd.DataFrame:
    """Read a table from the dataset storage
    
    :param data_info: Information of the table to read,
    :return: the read table
    """
    return __storage.read_table(data_info.uri)


def new_value(location: Dataset | Location,
              value: float,
              loc_annotate: dict[str, any] = None,
              data_annotate: dict[str, any] = None
              ) -> DataInfo:
    """Write value data
    
    :param location: Dataset or location to write,
    :param value: Value to set,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :return: The data information
    """
    loc = __get_location(location, loc_annotate)
    data_uri = __storage.create_value(loc.dataset, value)
    data_info = __index.create_data(loc, data_uri, StorageTypes.VALUE,
                                    data_annotate)
    return data_info


def write_value(data_info: DataInfo, value: float):
    """Write a value into storage
    
    :param data_info: Information of the data,
    :param value: Value to write
    """
    __storage.write_value(data_info.uri, value)


def read_value(data_info: DataInfo) -> float:
    """Read a value from the dataset storage
    
    :param data_info: Information of the table to read,
    :return: the read value
    """
    return __storage.read_value(data_info.uri)


def new_label(location: Dataset | Location,
              value: str,
              loc_annotate: dict[str, any] = None,
              data_annotate: dict[str, any] = None
              ) -> DataInfo:
    """Create a new label
    
    :param location: Dataset or location to write,
    :param value: Value to set,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :return: The data information
    """
    loc = __get_location(location, loc_annotate)
    data_uri = __storage.create_label(loc.dataset, value)
    data_info = __index.create_data(loc, data_uri, StorageTypes.LABEL,
                                    data_annotate)
    return data_info


def write_label(data_info: DataInfo, value: str):
    """Write a label into storage
    
    :param data_info: Information of the data,
    :param value: Value to write
    """
    __storage.write_label(data_info.uri, value)


def read_label(data_info: DataInfo) -> str:
    """Read a label from the dataset storage
    
    :param data_info: Information of the table to read,
    :return: the read value
    """
    return __storage.read_label(data_info.uri)


def query_data(dataset: Dataset, *,
               annotations: dict[str, any] = None,
               locations: list[Location] = None
               ) -> list[DataInfo]:
    """Retrieve data from a dataset
    
    :param dataset: Dataset to query,
    :param annotations: Query data that have the annotations,
    :param locations: Data at these locations
    """
    return __index.query_data(dataset,
                              annotations=annotations,
                              locations=locations)


def query_location(dataset: Dataset,
                   annotations: dict[str, any] = None,
                   ) -> list[Location]:
    """Retrieve locations from a dataset
    
    :param dataset: Dataset to query,
    :param annotations: query locations that have the annotations,
    :return: Locations that correspond to the query
    """
    return __index.query_location(dataset, annotations=annotations)


def data_annotations(dataset: Dataset) -> dict[str, list[any]]:
    """Get all the data annotations in the datasets with their values
    
    :param dataset: Dataset to query,
    :return: Available annotations with their values
    """
    return __index.data_annotations(dataset)


def location_annotations(dataset: Dataset) -> dict[str, list[any]]:
    """Get all the location annotations in the datasets with their values
    
    :param dataset: Dataset to be queried,
    :return: Available locations with their values
    """
    return __index.location_annotations(dataset)


def view_locations(dataset: Dataset
                   ) -> pd.DataFrame:
    """Create a table to visualize the dataset locations structure

    :param dataset: Dataset to visualize
    :return: The data view as a table
    """
    return __index.view_locations(dataset)


def view_data(dataset: Dataset,
              locations: list[Location] = None,
              ) -> pd.DataFrame:
    """Create a table to visualize the dataset data structure

    :param dataset: Dataset to visualize
    :param locations: Locations to filter
    :return: The data view as a table
    """
    return __index.view_data(dataset, locations)
