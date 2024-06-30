"""Definition of the main API methods"""
import pandas as pd

from .models import StorageTypes
from .models import URI
from .models import Dataset
from .models import Location
from .models import DataInfo
from .models import Data
from .models import DataInstance
from .models import Metadata
from .models import DataQueryType

from .logger import logger
from .config import config, config_file
from .factory import Factory
from .index import SxIndex
from .storage import SxStorage
from .metadata import SxMetadata


# Initialize the config and the backend plugins
cfile = config_file()
print('API cfile=', cfile)
logger().set_prefix("SciXtracer")
logger().info(f"use config file: {cfile}")
config(cfile)  # init singleton
__index: SxIndex = Factory(
    "sxt_", "index").get(config().value("index", "name"))()
if __index is not None:
    __index.connect(**config().filtered_section("index"))

__storage: SxStorage = Factory(
    "sxt_", "storage").get(config().value("storage", "name"))()
if __storage is not None:
    __storage.connect(**config().filtered_section("storage"))

__metadata: SxMetadata = Factory(
    "sxt_", "metadata").get(config().value("metadata", "name"))()
if __metadata is not None:
    __metadata.connect(**config().filtered_section("metadata"))


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
    __metadata.init_dataset(dataset_info)
    __storage.init_dataset(dataset_info)
    return dataset_info


def get_dataset(uri: URI) -> Dataset:
    """Read the information of a dataset
    
    :param uri: Unique identifier of the dataset
    """
    return __index.get_dataset(uri)


def set_description(dataset: Dataset, metadata: dict[str, any]):
    """Write metadata to a dataset
    
    :param dataset: Information of the dataset,
    :param metadata: Metadata to set
    """
    __index.set_description(dataset, metadata)


def get_description(dataset: Dataset) -> dict[str, any]:
    """Read the metadata of a dataset
    
    :param dataset: Information of the dataset,
    :return: The dataset metadata
    """
    return __index.get_description(dataset)


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


def __new_empty_data_uri(data: StorageTypes, loc: Location) -> URI:
    if data == StorageTypes.ARRAY:
        data_uri = __storage.create_tensor(loc.dataset, shape=(1, 1))
    elif data == StorageTypes.TABLE:
        data_uri = __storage.create_table(loc.dataset, None)
    elif data == StorageTypes.VALUE:
        data_uri = __storage.create_value(loc.dataset, None)
    elif data == StorageTypes.LABEL:
        data_uri = __storage.create_label(loc.dataset, "")
    else:
        raise ValueError(f'new_data: data type not recognized '
                         f'for {type(data)}')
    return data_uri


def __new_instance_data_uri(data: DataInstance,
                            loc: Location
                            ) -> [URI, StorageTypes]:
    if isinstance(data, __storage.array_types()):
        data_uri = __storage.create_tensor(loc.dataset, data)
        storage_type = StorageTypes.ARRAY
    elif isinstance(data, __storage.table_types()):
        data_uri = __storage.create_table(loc.dataset, data)
        storage_type = StorageTypes.TABLE
    elif isinstance(data, __storage.value_types()):
        data_uri = __storage.create_value(loc.dataset, data)
        storage_type = StorageTypes.VALUE
    elif isinstance(data, __storage.label_types()):
        data_uri = __storage.create_label(loc.dataset, data)
        storage_type = StorageTypes.LABEL
    else:
        raise ValueError(f'new_data: data type not recognized '
                         f'for {type(data)}')
    return data_uri, storage_type


def new_data(location: Dataset | Location,
             data: DataInstance,
             *,
             loc_annotate: dict[str, any] = None,
             data_annotate: dict[str, any] = None,
             metadata: dict[str, any] = None
             ) -> DataInfo:
    """Create new data

    :param location: Dataset or location to write,
    :param data: Data content,
    :param loc_annotate: Annotation attached to the location,
    :param data_annotate: Annotation attached to the data,
    :param metadata: Metadata attached to the data
    :return: The information of the created data
    """
    # create or get location
    loc = __get_location(location, loc_annotate)
    # Create data storage
    if isinstance(data, StorageTypes):
        __storage_type = data
        data_uri = __new_empty_data_uri(data, loc)

    else:
        data_uri, __storage_type = __new_instance_data_uri(data, loc)

    # create metadata
    metadata_uri = None
    if metadata is not None:
        metadata_uri = __metadata.create(loc.dataset, metadata)

    data_info = __index.create_data(loc, data_uri,
                                    __storage_type,
                                    data_annotate,
                                    metadata_uri)
    return data_info


def read_data(data_info: DataInfo
              ) -> DataInstance:
    """Read a tensor from the dataset storage

    :param data_info: Information of the data,
    :return: the read array
    """
    if data_info.storage_type == StorageTypes.ARRAY:
        return __storage.read_tensor(data_info.uri)
    if data_info.storage_type == StorageTypes.TABLE:
        return __storage.read_table(data_info.uri)
    if data_info.storage_type == StorageTypes.VALUE:
        return __storage.read_value(data_info.uri)
    if data_info.storage_type == StorageTypes.LABEL:
        return __storage.read_label(data_info.uri)
    raise ValueError('read_data: data type not recognized')


def write_data(data_info: DataInfo,
               data: DataInstance,
               ):
    """Write data to the storage

    :param data_info: Information of the data,
    :param data: The data to store
    """
    if data_info.storage_type == StorageTypes.ARRAY:
        return __storage.write_tensor(data_info.uri, data)
    if data_info.storage_type == StorageTypes.TABLE:
        return __storage.write_table(data_info.uri, data)
    if data_info.storage_type == StorageTypes.VALUE:
        return __storage.write_value(data_info.uri, data)
    if data_info.storage_type == StorageTypes.LABEL:
        return __storage.write_label(data_info.uri, data)
    raise ValueError('write_data: data type not recognized')


def set_metadata(data_info: DataInfo, content: Metadata):
    """Write metadata

    :param data_info: Information of the data,
    :param content: The metadata to store
    """
    __metadata.write(data_info.uri, content)


def get_metadata(data_info: DataInfo) -> Metadata:
    """Read metadata

    :param data_info: Information of the data,
    :return: The metadata to store
    """
    return __metadata.read(data_info.metadata_uri)


class DataIter:
    """Iterator on data info for data loading

    :param data_info: Information of data to load
    """
    def __init__(self, data_info: list[DataInfo] | list[list[DataInfo]]):
        self.__data_info = data_info

    def __len__(self):
        return len(self.__data_info)

    def __getitem__(self, idx) -> Data | list[Data]:
        info_s = self.__data_info[idx]
        if isinstance(info_s, DataInfo):
            return Data(info=info_s,
                        value=read_data(info_s),
                        metadata=get_metadata(info_s))
        out_data = []
        for info in info_s:
            out_data.append(Data(info=info,
                                 value=read_data(info),
                                 metadata=get_metadata(info)
                                 )
                            )
        return out_data


def query_data(dataset: Dataset,
               annotations: dict[str, any] | list[dict[str, any]],
               query_type: DataQueryType = DataQueryType.SINGLE,
               info_only: bool = True
               ) -> list[DataInfo] | list[list[DataInfo]] | DataIter:
    """Query data in a dataset

    :param dataset: Dataset to query,
    :param annotations: Query data that have the annotations,
    :param query_type: Type of query
    :param info_only: To return only data info (not data load)
    """
    data_info = None
    if query_type == DataQueryType.SINGLE:
        if isinstance(annotations, list):
            if len(annotations) > 1:
                raise ValueError("Cannot query single data with list")
            annotations = annotations[0]
        data_info = __index.query_data_single(dataset, annotations)
    elif query_type == DataQueryType.LOC_SET:
        data_info = __index.query_data_loc_set(dataset, annotations)
    elif query_type == DataQueryType.GROUP_SET:
        data_info = __index.query_data_group_set(dataset, annotations)
    if info_only:
        return data_info
    return DataIter(data_info)


def delete(data_info: DataInfo):
    """Delete a data

    :param data_info: Info of the data to delete
    """
    __metadata.delete(data_info.metadata_uri)
    __storage.delete(data_info.storage_type, data_info.uri)
    __index.delete(data_info)


def delete_query(dataset: Dataset, annotations: dict[str, any]):
    """Delete the data with a given set of annotations

    :param dataset: Dataset to query,
    :param annotations: Delete data that have the annotations,
    """
    data_list = query_data(dataset, annotations, DataQueryType.SINGLE, True)
    for data_info in data_list:
        delete(data_info)


def query_location(dataset: Dataset,
                   annotations: dict[str, any] = None,
                   ) -> list[Location]:
    """Retrieve locations from a dataset
    
    :param dataset: Dataset to query,
    :param annotations: query locations that have the annotations,
    :return: Locations that correspond to the query
    """
    return __index.query_location(dataset, annotations=annotations)


def query_data_annotation(dataset: Dataset) -> dict[str, list[any]]:
    """Get all the data annotations in the datasets with their values
    
    :param dataset: Dataset to query,
    :return: Available annotations with their values
    """
    return __index.query_data_annotation(dataset)


def query_location_annotation(dataset: Dataset) -> dict[str, list[any]]:
    """Get all the location annotations in the datasets with their values
    
    :param dataset: Dataset to be queried,
    :return: Available locations with their values
    """
    return __index.query_location_annotation(dataset)


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
