from typing import Optional

import xarray as xr

from fast_vindex import patched_vindex

def prepare_for_colocate(
    grid_data: xr.Dataset,
    point_data: xr.Dataset,
    search_window: Optional[dict] = None,
    cyclic_dims: list = [],
    grid_prefix: str = 'grid_',
    point_prefix: str = 'point_',
) -> xr.Dataset:

    """
    TO DO:
    * [x] ajouter la partie modulo
    """
    grid, point = grid_data, point_data

    grid_dims = grid.dims
    point_dims = point.dims

    if search_window is None:
        search_window = {dim: 0 for dim in grid_dims}
            
    # Formatage
    # Vérifie que toutes les dimensions du grid sont présentes dans les variables ou coordonnées de point_data
    missing_keys = [k for k in grid.sizes if k not in point.data_vars and k not in point.coords]
    
    if missing_keys:
        raise ValueError(f"Missing keys in point_data: {missing_keys}")

    point = point.point._format(grid_dims, prefix=point_prefix)
    grid = grid.grid._format(prefix=grid_prefix)

    # Création des index des coordonnées du dataset dans le datacube
    for dim in grid_dims:
        point[f"{point_prefix}i{dim}"] = point.point._find_nearest_indices(grid, dim, grid_prefix, point_prefix)

    # Vérifie si le minicube est dans le domaine
    for dim in grid_dims:
        _min = search_window[dim]
        _max = grid.sizes[f"{grid_prefix}{dim}"] - search_window[dim]

        point[f"{point_prefix}i{dim}_in_domain"] = point.point._in_domain(
            point[f"{point_prefix}i{dim}"],
            _min,
            _max
        )

    # Filtre les minicube qui sont en dehors du domain
    non_cyclic_dims = [dim for dim in grid_dims if dim not in cyclic_dims]
    condition = (point[f"{point_prefix}i{non_cyclic_dims[0]}_in_domain"] == True)
    for dim in non_cyclic_dims[1:]:
        condition &= (point[f"{point_prefix}i{dim}_in_domain"]== True)

    point = point.where(condition, drop=True)

    # Create the i_arrays
    for dim in grid_dims:
        point[f"{point_prefix}i{dim}_array"] = point.point._array(
            point[f"{point_prefix}i{dim}"], 
            f"{dim}_step", 
            search_window[dim]
        )

    for dim in cyclic_dims:
        modulo = lambda x: x % grid.sizes[f"{grid_prefix}{dim}"]
        point[f"{point_prefix}i{dim}_array"] = modulo(point[f"{point_prefix}i{dim}_array"].astype('int32'))
    
    #modulo = lambda lon: lon % datacube.sizes['dc_lon']
    #dataset['ds_ilon_array'] = modulo(dataset.ds_ilon_array).astype('int32')
    
    return grid, point

def colocate(
    grid_data: xr.Dataset,
    point_data: xr.Dataset,
    grid_prefix: str = 'grid_',
    point_prefix: str = 'point_',
) -> xr.Dataset:

    grid, point = grid_data, point_data

    indexers = {}
    for dim in grid.sizes:
        dim = dim.split('_')[-1]
        indexers[f"{grid_prefix}{dim}"] = point[f"{point_prefix}i{dim}_array"].astype('int32')

    with patched_vindex():
        result = grid.isel(**indexers)

    return result