"""Module with scripts to import the synthetic dataset"""
from pathlib import Path
import shutil
from skimage.io import imread

import scixtracer as sx


def import_data(dataset_name: str):
    """Script to import data in the synthetic dataset example"""
    src_dir = Path(__file__).parent.resolve() / "synthetic_data"

    dataset = sx.new_dataset(dataset_name)
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
    return dataset


def clean_dataset(workspace: Path, dir_name: str = "demo_spots"):
    """Remove a dataset from the workspace"""
    dataset_dir = workspace / dir_name
    if Path(dataset_dir).exists():
        shutil.rmtree(dataset_dir)
