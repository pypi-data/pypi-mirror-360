# Terminology

## DataCube

The `DataCube` is a 3-dimensional array with axes defined by `time`, `lon`, and `lat`. It contains spatio-temporal data, where each element represents a specific measurement or value at a given time and spatial location (latitude and longitude). This cube-like structure is essential for efficiently accessing and analyzing data across multiple dimensions. 

See the [](configuration_datacube) section for configuration.

## Dataset

The `Dataset` is a 1-dimensional array with an `obs` axis, which holds a set of observations. Each observation is associated with a specific spatio-temporal coordinate `time`, `lon`, and `lat`. Unlike the continuous grid of the datacube, the dataset is a collection of discrete data points that link to particular times and locations. 

See the [](configuration_dataset) section for configuration.

## MiniCube

The `MiniCube` is a localized extraction from the datacube that surrounds each observation within the dataset. Defined by a configurable buffer size, a minicube captures a 3D window centered on an observation, extending spatially in both latitude and longitude and temporally in time. This enables analyses of local conditions and patterns around individual observations.

## Cluster

Le `Cluster` permet de distribuer les opérations sur les différentes ressources de calcules qui le compose. Il est défnis à partir de la librairie `Dask`. 

See the [](configuration_cluster) section for configuration.