---
file_format: mystnb
kernelspec:
  name: python3
---

# Configuration

The `DataCube` and `Dataset` must be created as instances of `xarray.Dataset`, ensuring compatibility with the functions and methods in this library. This format allows for efficient indexing, data alignment, and computation across spatio-temporal coordinates.

(configuration_datacube)=
## DataCube

The `DataCube` should be a 3D `xarray.Dataset` object containing spatial and temporal dimensions. Each data variable is indexed along `(time, lon, lat)` to represent a continuous geospatial data structure.

### Dimensions

- `time`: The temporal dimension, typically in a chronological order. This dimension represents time intervals or timestamps for the dataset.
- `lon`: The longitudinal spatial dimension, representing east-west geographic positions.
- `lat`: The latitudinal spatial dimension, representing north-south geographic positions.

### Coordinates

- `time` `(time)`: Defines time coordinates, typically as datetime values in a consistent time zone.
- `lon` `(lon)`: Longitude coordinates in degrees, often spanning from -180 to 180.
- `lat` `(lat)`: Latitude coordinates in degrees, typically ranging from -90 to 90.

### Data Variables

- `<var_name>` `(time, lon, lat)`: Variables stored in the DataCube, with values indexed by time, lon, and lat. Each variable should represent a specific measurement, such as temperature, humidity, or wind speed.

```{code-cell}
:tags: [remove-input]
from pytcube.utils import datacube
datacube
```

(configuration_dataset)=
## Dataset

The `Dataset` should be a 1D `xarray.Dataset` object structured as an array of individual observations, with each entry providing specific spatio-temporal coordinates. This format allows for analyzing discrete points in time and space relative to the broader DataCube context.

### Dimensions

- `obs`: The observation dimension, representing each individual observation or data point with its unique set of coordinates.

### Coordinates

- `obs` `(obs)`: Indexes each observation entry in the dataset.

### Data Variables

- `time` `(obs)`: A 1D array of timestamps for each observation, matching a particular point in time.
- `lon` `(obs)`: The longitudinal position for each observation in degrees.
- `lat` `(obs)`: The latitudinal position for each observation in degrees.

```{code-cell}
:tags: [remove-input]
from pytcube.utils import dataset
dataset
```

(configuration_cluster)=
## Cluster

The strength of PytCube lies in its ability to parallelize the colocalization step. To achieve this, PytCube uses the `Dask` library, which enables the definition of a cluster on which operations will run. There are several ways to define a cluster, but we will present two here: a local cluster, called `LocalCluster`, which uses local resources, and a PBS cluster, called `PBSCluster`, which submits jobs requesting resources on an HPC.

### LocalCluster

A `LocalCluster` allows for using local resources to parallelize colocalization operations. Defining a local cluster is very straightforward; simply define it as follows:

```python
from dask.distributed import LocalCluster, Client

cluster = LocalCluster()
client = Client(cluster)
```

For more information on `LocalCluster`, you can refer to the [official documentation](https://distributed.dask.org/en/stable/api.html#distributed.LocalCluster).

### PBSCluster

A `PBSCluster` allows you to request resources on an HPC that uses the scheduler `(Portable Batch System)` (similar solutions exist for other schedulers, such as Slurm, LSF, etc.; see https://jobqueue.dask.org/en/latest/clusters-api.html). To define a PBS cluster, it is necessary to specify the resources you wish to use.

```python
from dask.distributed import Client
import dask_jobqueue

cluster = dask_jobqueue.PBSCluster(queue='mpi', 
                                   cores=28,
                                   memory="115g",
                                   walltime="01:00:00",
                                   interface='ib0',
                                   processes=4
                                  )
cluster.scale(jobs=1)
client = Client(cluster)
```

For more information on `PBSCluster`, you can refer to the [official documentation](https://jobqueue.dask.org/en/latest/generated/dask_jobqueue.PBSCluster.html#dask_jobqueue.PBSCluster).

### Dashboard

To monitor task progress, there are several options, but the best approach is to access the dashboard provided by the Dask client. If the cluster is local, you can directly access the URL `http://localhost:8787` provided by the command: ```client.dashboard_link```

![](../_static/dashboard_dask.png)

If the cluster is remote, you will need to set up an SSH port forwarding. To do this, simply open a terminal on your local machine and enter the following SSH command: `ssh -L 8787:localhost:8787 user@remote_hpc_address`, see https://docs.dask.org/en/stable/diagnostics-distributed.html#connecting-to-the-dashboard.

Here is a snippet of code that allows you to directly obtain the correct SSH command:

```python
import os

remote_hpc_address = 'datarmor.ifremer.fr'
user = os.environ["USER"]
hostname = os.environ["HOSTNAME"]
port = client.scheduler_info()["services"]["dashboard"]

ssh_command = f'ssh -N -L {port}:{hostname}:{port} {user}@{remote_hpc_address}'
url = f"http://localhost:{port}"
print(ssh_command, url)
```