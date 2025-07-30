import xarray as xr

@xr.register_dataset_accessor("grid")
class GridAccessor:

    def __init__(self, xarray_obj: xr.Dataset):
        self._obj = xarray_obj
        
    def _format(self, prefix):
        dims_renamed = {dim: f"{prefix}{dim}" for dim in self._obj.dims} 
        return self._obj.rename(dims_renamed) # rename dims and coords
