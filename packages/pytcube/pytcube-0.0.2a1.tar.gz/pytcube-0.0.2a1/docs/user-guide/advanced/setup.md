# Setup

```{note}
Work In Progress
```

La 1ère étape réalisé par PytCube, consiste à préparer les données d'observations afin de faciliter l'étape de colocalisation. 

Pour chaque observation qui a pour coordonnée `obs(time, lon, lat)`, on récupère les index du datacube `obs(itime, ilon, ilat)` qui sont les plus proche du point d'observation. Ainsi on associe à chaque coordonnées son index correspondant dans le datacube. 

obs[['time', 'lon', 'lat']]

![](/_static/index_coordinates.png)

L'étape suivante consiste à convertir en index les buffers qui ont été renseigné par l'utilisateur en minutes et kilometres noté `buffer(time, lon, lat)`. Comme on connait le pas de temps et le pas d'espace entre les données grillées du datacube, on peux déterminer à combien d'index du datacube correspond les buffers. On obtient alors les buffers `buffer(itime, ilon, et ilat)` qui correspondent à des index du datacube. 