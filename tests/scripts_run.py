"""Scripts to run analysis on synthetic dataset for testing"""
import numpy as np
import pandas as pd

from scipy.ndimage import gaussian_filter
from scipy.stats import ttest_ind

from skimage.restoration import wiener
from skimage.feature import blob_dog
from skimage.measure import regionprops_table
from skimage.draw import disk

import scixtracer as sx


def wiener_filter(image: np.ndarray,
                  sigma=1.5,
                  balance=0.01) -> np.ndarray:
    """Apply a wiener deconvolution with a Gaussian PSF

    :param image: Image to deblur,
    :param sigma: Size of the gaussian PSF,
    :param balance: Regularization parameter of the Wiener filter
    :return: The filtered image
    """
    psf = np.zeros(image.shape)
    psf[int(image.shape[0]/2), int(image.shape[1]/2)] = 1
    psf = gaussian_filter(psf, sigma)
    return wiener(image/np.max(image[:]), psf, balance)


def spot_detection(image: np.ndarray,
                   max_sigma=3,
                   threshold=0.1
                   ) -> [pd.DataFrame, int]:
    """Detect spots in an image

    :param image: Image to process,
    :param max_sigma: Radius of the spots,
    :param threshold: Threshold on spot intensity,
    :return: A table with the spots information and the spots count
    """
    blobs_dog = blob_dog(image, max_sigma=max_sigma, threshold=threshold)
    return pd.DataFrame(blobs_dog, columns=["y", "x", "sigma"]), len(blobs_dog)


def spots_metrics(image: np.ndarray, spots: pd.DataFrame) -> pd.DataFrame:
    """Compute the metrics of spots in an image

    :param image: Image to quantify
    :param spots: Table of spots coordinates and radius
    :return: A dataframe with all spots metrics (one spot per row)
    """
    label_image = np.zeros(image.shape).astype(int)
    for i, row in spots.iterrows():
        rr, cc = disk((row['y'], row['x']), row['sigma'], shape=image.shape)
        label_image[rr, cc] = i+1
    props = regionprops_table(label_image, image,
                              properties=["area", "centroid", "intensity_mean",
                                          "intensity_min", "intensity_max",
                                          "intensity_std"])
    return pd.DataFrame(props)


def mean_metric(table: pd.DataFrame, metric_id="count") -> float:
    """Compute the mean of a metric

    The count metric is taken separately using len

    :param table: Table that contains instances to average
    :param metric_id: ID of the metric to average
    :return: The average value
    """
    if metric_id == "count":
        return len(table.index)
    return float(table[[metric_id]].mean().iloc[0])


def mean_t_test(cond1: list[pd.DataFrame],
                cond2: list[pd.DataFrame],
                metric_id="count") -> [float, float]:
    """Compute a Student t-test on two condition means

    :param cond1: Tables containing the individual values for each metrics
    :param cond2: Tables containing the individual values for each metrics
    :param metric_id: ID of the metric to average
    :return: the Student statistic and the p-value
    """
    cond1_values = []
    for table in cond1:
        cond1_values.append(mean_metric(table, metric_id))
    cond2_values = []
    for table in cond2:
        cond2_values.append(mean_metric(table, metric_id))

    stat_value, p_value = ttest_ind(cond1_values, cond2_values)
    return float(stat_value), float(p_value)


def pipeline_runner(dataset: sx.Dataset):
    """Main script to analyze dataset using the job runner"""

    # Deconvolution
    job_decon = sx.Job(
        func=wiener_filter,
        inputs=[{"image": "raw"}, 2, 0.1],
        outputs=[{'image': "decon"}]
    )

    # Spot Detection
    job_detection = sx.Job(
        func=spot_detection,
        inputs=[{"image": "decon"}, 3, 0.3],
        outputs=[{"table": "spots"}, {"value": "spots count"}]
    )

    # Spot Analysis
    job_analysis = sx.Job(
        func=spots_metrics,
        inputs=[{"image": "raw"}, {"table": "spots"}],
        outputs=[{"table": "metric"}],
        query_type=sx.DataQueryType.LOC_SET
    )

    # Statistical analysis
    stat1_job = sx.Job(
        func=mean_t_test,
        inputs=[{"table": "metric", "population": "population1"},
                {"table": "metric", "population": "population2"},
                "intensity_mean"],
        outputs=[{"value": "t-stat", "metric": "intensity_mean"},
                 {"value": "t-pvalue", "metric": "intensity_mean"}],
        query_type=sx.GROUP_SET
    )
    stat2_job = sx.Job(
        func=mean_t_test,
        inputs=[{"table": "metric", "population": "population1"},
                {"table": "metric", "population": "population2"},
                "count"],
        outputs=[{"value": "t-stat", "metric": "count"},
                 {"value": "t-pvalue", "metric": "count"}],
        query_type=sx.GROUP_SET
    )
    sx.run(dataset, [job_decon, job_detection, job_analysis, stat1_job,
                     stat2_job])


def pipeline_call(dataset: sx.Dataset):
    """Main script to analyse dataset"""

    job_id = "1"

    # Deconvolution
    for raw_info in sx.query_data(dataset, annotations={"image": "raw"}):
        sx.call(wiener_filter)([{'image': "decon", "job_id": job_id}], raw_info, 2, 0.1)

    # Spot Detection
    for decon_info in sx.query_data(dataset, annotations={"image": "decon"}):
        sx.call(spot_detection)([{"table": "spots", "job_id": job_id},
                                 {"value": "spots count", "job_id": job_id}],
                                decon_info, 3, 0.3)

    # Spot Analysis
    list_raw_spot = sx.query_data(
        dataset, annotations=[{"image": "raw"}, {"table": "spots"}],
        query_type=sx.LOC_SET)
    for data_info in list_raw_spot:
        sx.call(spots_metrics)([{"table": "metric", "job_id": job_id}],
                               data_info[0], data_info[1])

    # Statistical analysis
    metrics_sets = sx.query_data(dataset, annotations=[
            {"table": "metric", "population": "population1"},
            {"table": "metric", "population": "population2"},
        ], query_type=sx.GROUP_SET)
    sx.call(mean_t_test)(
        [{"value": "t-stat", "metric": "intensity_mean", "job_id": job_id},
         {"value": "t-pvalue", "metric": "intensity_mean", "job_id": job_id}],
        metrics_sets[0], metrics_sets[1], "intensity_mean")
    sx.call(mean_t_test)(
        [{"value": "t-stat", "metric": "count", "job_id": job_id},
         {"value": "t-pvalue", "metric": "count", "job_id": job_id}],
        metrics_sets[0], metrics_sets[1], "count")
