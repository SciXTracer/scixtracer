"""Tests for the runners"""
import pytest
import scixtracer as sx
from .scripts_import import clean_dataset
from .scripts_import import import_data
from .scripts_run import pipeline_call
from .scripts_run import pipeline_runner


def do_assert(dataset: sx.Dataset, dataset_name: str, ann_count: int):
    """Assert the results for the synthetic dataset"""
    assert dataset.name == dataset_name

    loc_ann = sx.query_location_annotation(dataset)
    assert len(loc_ann) == 3
    assert len(loc_ann["population"]) == 2
    assert len(loc_ann["id"]) == 20

    data_ann = sx.query_data_annotation(dataset)
    assert len(data_ann) == ann_count
    assert "job_id" in data_ann

    result = sx.query_data(dataset,
                           annotations={"value": "t-stat", "metric": "count"},
                           info_only=False)
    assert result[0].value == pytest.approx(-3.89435849621, 0.000001)
    result = sx.query_data(dataset,
                           annotations={"value": "t-pvalue", "metric": "count"})
    assert sx.read_data(result[0]) == pytest.approx(0.000385836563, 0.000001)
    result = sx.query_data(dataset,
                           annotations={"value": "t-stat", "metric": "intensity_mean"})
    assert sx.read_data(result[0]) == pytest.approx(0.120797930521, 0.000001)
    result = sx.query_data(dataset,
                           annotations={"value": "t-pvalue", "metric": "intensity_mean"})
    assert sx.read_data(result[0]) == pytest.approx(0.904487572854, 0.000001)


def test_pipeline_call(workspace):
    """Run the runner test using the call decorator"""
    clean_dataset(workspace, "demo_spots_call")
    dataset = import_data("Demo spots call")
    pipeline_call(dataset)
    do_assert(dataset, "Demo spots call", 5)


def test_pipeline_runner(workspace):
    """Run the runner test using the job runner plugin"""
    clean_dataset(workspace, "demo_spots_runner")
    dataset = import_data("Demo spots runner")
    pipeline_runner(dataset)

    data_ann = sx.query_data_annotation(dataset)
    assert "run_id" in data_ann

    do_assert(dataset, "Demo spots runner", 6)
