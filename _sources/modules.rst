API
===

Models
------

.. currentmodule:: scixtracer.models

.. autosummary::
    :toctree: generated
    :nosignatures:

    StorageTypes
    URI
    Dataset
    Location
    DataInfo
    DataInstance
    Metadata
    Data
    DataQueryType
    Job
    Batch
    BatchItem

Queries
-------

.. currentmodule:: scixtracer.api

.. autosummary::
    :toctree: generated
    :nosignatures:

    datasets
    new_dataset
    get_dataset
    set_description
    get_description
    new_location
    annotate_location
    annotate_data
    new_data_index
    new_data
    read_data
    write_data
    set_metadata
    get_metadata
    DataIter
    query_data
    delete
    delete_query
    query_location
    query_data_annotation
    query_location_annotation
    view_locations
    view_data


Runner
------

.. currentmodule:: scixtracer.api_runner

.. autosummary::
    :toctree: generated
    :nosignatures:

    call
    run