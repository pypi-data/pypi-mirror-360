# Indexing

```{note}
Work In Progress
```

L'étape de colocalisation pour un MiniCube est en elle même assez simple, elle repose sur l'indexation par `xarray`.

Pour faire simple si l'on souhaite selectionner, un MiniCube au sein d'un DataCube avec xarray, il suffit de faire:

obs = bacth.isel(obs=0)
datacube.isel(
    itime=slice(obs.itime - buffer['itime'], obs.time + buffer['itime']),
    ilon=slice(obs.lon - buffer['ilon'], obs.lon + buffer['ilon'])
    ilat=slice(obs.lat - buffer['ilat'], obs.lat + buffer['ilat'])
)

Cependant si l'on souhaite selectionner plusieurs MiniCube en même temps, il n'est pas possible de passer une liste de slice, car l'indexation de xarray repose sur l'indexation de Numpy qui ne prend pas en charge des listes de slices. Il est donc necessaire de procéder autrement. 

Pour celà nous allons utiliser l'indexation avancé de numpy qui prend en charge l'integer array indexing. Concretement pour chaque point d'observations nous allons générer les index du minicube à extraire du datacube. Par exemple:

obs.array_itime = [t-2, t-1, t, t+1, t+2]
obs.array_ilon = [x-2, x-1, x, x+1, x+2]
obs.array_ilat = [y-2, y-1, y, y+1, y+2]

Ce qui vas nous permettre d'extraire plusieurs points d'observation d'un seul coup. 