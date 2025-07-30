# Overview: Why PytCube?

## Context

In the field of Geosciences, many research works require the comparison of several datasets (analysis, calibration, qualification, etc.).

To facilitate this operation, a preliminary step involves performing a co-location between the datasets to select only the data of interest useful for subsequent comparisons.

Depending on the input data, there are different methods to achieve this co-location. PytCube aims to provide an efficient solution for co-locating a `DataCube` with a `Dataset` of observation points to obtain co-located data, referred to as `MiniCubes`.

![](/_static/pytcube_schema.png)

## Issues

The co-location between an observation point and a datacube is not complicated to perform in itself. Indeed, `Xarray` provides simple and effective solutions for this operation. The complexity arises when one wishes to scale up and perform co-locations on 1,000, 10,000, or even 100,000 points. At this stage, performing the operations sequentially is no longer feasible. It becomes necessary to parallelize the operation using `Dask`.

This is where `PytCube` comes into play. Based on `Xarray` and `Dask`, PytCube aims to facilitate and optimize the co-location step by parallelizing the extraction of data from the datacube.

To perform these operations, PytCube provides two main functions:

* **`pytcube.prepare_for_colocate`**:
  Prepares point-based indexing by computing the nearest grid cell indices for each observation point within a specified search window. This function performs coordinate alignment, validity checks, domain filtering, and builds the indexing arrays needed for fast subsetting. It returns formatted versions of the input grid and point datasets, ready for colocation.

* **`pytcube.colocate`**:
  Performs the actual extraction of spatio-temporal sub-cubes around each observation point using advanced indexing. This function leverages `fast-vindex` for efficient and parallel-compatible selection, and is suitable for use in larger workflows involving distributed computing or writing to formats like Zarr.
