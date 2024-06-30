"""Test importing the demo dataset"""
from pathlib import Path
from skimage.io import imread
import scixtracer as sx


def test_import_data(workspace):

    src_dir = Path(__file__).parent.resolve() / "synthetic_data"

    dataset = sx.new_dataset("Demo spots")
    sx.set_description(dataset, {"short": "fake description"})

    files = src_dir.glob('*.tif')
    for file in files:
        filename = str(file.name).replace('.tif', '')
        print("import filename = ", filename)
        population, idd = filename.split("_")
        array = imread(file)
        sx.new_data(dataset,
                    array,
                    loc_annotate={"population": population, "id": idd},
                    data_annotate={"image": "raw"},
                    metadata={"original_file": str(file)})

    desc = sx.get_description(dataset)
    assert desc == {"short": "fake description"}

    loc_ann = sx.query_location_annotation(dataset)
    assert len(loc_ann) == 2
    assert len(loc_ann["population"]) == 2
    assert len(loc_ann["id"]) == 20

    data_ann = sx.query_data_annotation(dataset)
    assert len(data_ann) == 1
    assert len(data_ann["image"]) == 1
    assert data_ann["image"] == ["raw"]

    locations = sx.query_location(dataset, {"population": "population1"})
    assert len(locations) == 20
    locations_1 = sx.query_location(dataset, {"population": "population1",
                                              "id": "001"})
    assert len(locations_1) == 1
    datainfo_1 = sx.query_data(dataset, annotations={"population": "population1",
                                                     "id": "001",
                                                     "image": "raw"})
    assert len(datainfo_1) == 1
    assert datainfo_1[0].storage_type == sx.StorageTypes.ARRAY
    datainfo_list = sx.query_data(dataset, annotations={"image": "raw"})
    assert len(datainfo_list) == 40

    data_1 = sx.read_data(datainfo_1[0])
    assert data_1.shape == (128, 128)
