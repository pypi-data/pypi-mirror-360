---
file_format: mystnb
kernelspec:
  name: python3
---

# Quick overview

Here are some quick examples of what you can do with PytCube. Everything is explained in much more detail in the rest of the documentation.

```{code-cell}
import numpy as np
import pandas as pd
import pytcube
import xarray as xr
```

```{code-cell}
DIMS = {'time':30, 'lon':360, 'lat':180}
START_DATE = '2020-01-01'
OBS = 100
```

```{code-cell}
:tags: [remove-cell]
rs = np.random.RandomState(123)
```


## DataCube

Generation of a random `DataCube`

```{code-cell}
def arange_center(start, stop, size):
    step = (stop - start) / size
    return np.arange(start + step/2, stop + step/2, step)
```

```{code-cell}
datacube = xr.Dataset()
datacube['time'] = ('time', pd.date_range(START_DATE, periods=DIMS['time'], freq='d'))
datacube['lon'] = ('lon', arange_center(-180, 180, DIMS['lon']))
datacube['lat'] = ('lat', arange_center(-90, 90, DIMS['lat']))
datacube['data'] = (['time', 'lon', 'lat'], rs.rand(DIMS['time'], DIMS['lon'], DIMS['lat']))
datacube
```

## Dataset

Generation of a `Dataset` of random observations

```{code-cell}
dataset = xr.Dataset()
dataset['obs'] = ('obs', np.arange(OBS))
dataset['time'] = ('obs', pd.to_datetime(rs.choice(pd.date_range(START_DATE, periods=DIMS['time'], freq='d'), size=OBS, replace=True)))
dataset['lon'] = ('obs', rs.uniform(-180, 180, size=OBS))
dataset['lat'] = ('obs', rs.uniform(-90, 90, size=OBS))
dataset
```

## Extraction

`pytcube.extraction` enables lazy extraction of minicubes. 

- `BUFFER` is used to define the size of the minicubes to be extracted around the observation points:
    - *time*: +/- X minutes around observation's `time` values.
    - *lon*: +/- X kilometers around observation's `longitude` values.
    - *lat*: +/- X kilometers around observation's `latitude` values.
- `N_OBS_PER_BATCH` is used to define the number of observations per batch, each batch being processed in parallel. 
- `PATH` is used to define the path to the zarr file where the minicubes will be written. 

```{code-cell}
BUFFER = {'time': 1440, 'lon': 200, 'lat': 200} # minutes & kilometers
N_OBS_PER_BATCH = 10
PATH = '/home1/scratch/gcaer/data/pytcube/overview.zarr'
```

```{code-cell}
---
mystnb:
  merge_streams: true
---
batches = pytcube.extraction(datacube, dataset, BUFFER, N_OBS_PER_BATCH, path=PATH)
```

## Compute

`pytcube.compute` calculates parallel extraction and writing in Zarr format.

```{code-cell}
---
mystnb:
  merge_streams: true
---
results = pytcube.compute(batches)
results
```

## Results

Opening the results and displaying a slice of a minicube

```{code-cell}
result = xr.open_zarr(PATH)
```

```{code-cell}
result.isel(id=0, t=0).datacube_data.plot()
```
