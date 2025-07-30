# Output Format

The output of the `pytcube.compute()` function is a generalized `xarray.Dataset`.

## Dimensions

- `id`: Unique identifier for each observation.
- `t`: Time dimension within each minicube.
- `x`: Longitude grid points within each minicube.
- `y`: Latitude grid points within each minicube.

## Coordinates

- Main coordinates:
    - `id` `(id)`: Unique identifier for each observation.
    - `obs` `(id)`: Original identifier of each observation.
- Coordinates with `datacube_` prefix: 
    - `datacube_time` `(id, t)`: Time values for each `id` across the `t` dimension.
    - `datacube_lon` `(id, x)`: Longitude values for each `id` across the `x` dimension.
    - `datacube_lat` `(id, y)`: Latitude values for each `id` across the `y` dimension.
- Coordinates with `dataset_` prefix: 
    - `dataset_time` `(id)`: Time values associated with each `id`.
    - `dataset_lon` `(id)`: Longitude values associated with each `id`.
    - `dataset_lat` `(id)`: Latitude values associated with each `id`.

## Data Variables

- `datacube_<var_name>` `(id, t, x , y)`: Variable value of the minicube `(t, x, y)` for each `id`.
    