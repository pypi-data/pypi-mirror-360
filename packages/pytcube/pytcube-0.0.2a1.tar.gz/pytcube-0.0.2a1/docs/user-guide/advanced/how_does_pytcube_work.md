# How does PytCube work?

PytCube propose 2 modes de fonctionnement pour la colocalisation, avec l'argument `optimize=True` ou `optimize=False`. 

le terme `optimize` peux préter à confusion, c'est pour ça qu'il est necessaire de comprendre comment fonctionne PytCube pour comprendre les limitations des 2 méthodes et quand utiliser l'une ou l'autre. 

## Setup

La 1ère étape qui est commune au deux méthodes, consiste à préparer les données d'observations afin de faciliter l'étape de colocalisation. 

Pour chaque observation qui a pour coordonnée (time, lon, lat), on récupère les index du datacube (itime, ilon, ilat) qui sont les plus proche du point d'observation. 

Ensuite on convertis les buffers en minutes et kilometers en index du datacube. Comme on connait le pas de temps et le pas d'espace entre les données grillées du datacube, on peux déterminer à combien d'index du datacube correspond les buffers. On obtient alors les buffers (itime, ilon, et ilat) qui correspondent à des index du datacube. 

## Batching

PytCube utilise des batch pour paralléliser la colocalisation. Ainsi une fois les données préparé, on répartis ces données dans des batches. Pour celà les observations sont trier par ordre croissant des dates, puis on selectionne des batch de `n_obs_per_batch`. (Par exemple, si on a 1_000 observations et que l'on définis `n_obs_per_batch=100`, on obtiendra 10 batches, de chacun 100 observation.)

Une fois que l'on a répartis les observations par batch, pour chaque batch, nous allons sélectionné les données d'intérêts dans le datacube. Pour celà on récupère les index des dates minimal `t_min = itime.min()` et maximales `t_max = itime.max()` des observations dans le batch, et on selectionne une tranche du datacube correspondant allant de `t_min - buffer['itime']` à `t_max + buffer['itime']`. 

[Schema batching]

## Indexing

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

## Optimization

C'est là qu'intervient l'argument `optimize`. Jusqu'ici toutes les opérations prcédentes ont été réalisé de manière paresseuses. Ainsi Dask a créé un arbre des tâches qui sera exécuter sur le cluster lorsque l'on appellera la fonction `compute`. 

Cependant il existe 2 manière de construire cet arbre des tâches, chacune ayant ses avantages et ses inconvénients. 

### Optimize == False

La 1ère méthode qui correspond à `optimize=False` dans PytCube, revient à construire un arbre des tâches qui commence par ouvrir en mémoire l'ensemble de la tranche du datacube, puis a selectionner les MiniCube à l'intérieur, c'est une méthode `brute force` dans le sens où on lis toute la données pour ne selectionner que celle qui nous intérèsse, l'avantage est que l'arbre des tâches est très rapide à construire, et que si l'on a assez de RAM et une données en local facilement accessible, elle est dans la majorité des cas, la méthode la plus rapide. L'inconvénient est que pour des jeux de données très volumineux, elle nécéssite beaucoup de RAM, où alors de limiter la taille des tranches du Datacube en limitant la valeur de `n_obs_per_batch`. 

[Schéma Dask.visualize]

### Optimize == True

La 2ème méthode qui correspond à `optimize=True` dans PytCube, revient à construire un arbre des tâches optimisé qui ouvre uniquement les chunks d'intérets qui ne selectionne que la données d'intérêt, qui ferme le chunk avant de passer à celui d'après. Cette méthode est optimisé dans le sens où elle nécéssite peux de ressource en RAM, ce qui est de loin son grand avantage. L'inconvénient est que pour des MiniCubes avec de grande dimensions, la construction de l'arbre des tâches peux prendre beaucoup de temps (dans certain cas, vraiment beaucoup de temps.). De plus l'arbre des tâches peux lui même devenir assez volumineux, ce qui est en plus de prendre du temps à être construit, prend du temps à le transférer au scheduler et à l'initialiser. Dans le cas où l'on se trouve avec des données accessible à distance et des minicubes ayant des petites dimensions, il peux être intéressant d'utiliser cette méthode pour limiter la quantité de donnée à télécharger. 

### Synthèse

En conclusion, 2 paramètres vont principalement guider notre choix:
- La rapidité de lecture des données (par exemple: local VS S3). 
- La taille des minicubes à extraire.


