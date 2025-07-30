# Batching

```{note}
Work In Progress
```

Une fois les données préparées, nous allons pouvoir préparer la colocalisation. Pour paralléliser efficacement les calculs, PytCube répartis les données préparée dans des batchs. Pour celà les observations sont trier par ordre croissant des dates, puis on selectionne des batch de `n_obs_per_batch`. (Par exemple, si on a 1_000 observations et que l'on définis `n_obs_per_batch=100`, on obtiendra 10 batches, de chacun 100 observation.)

Une fois que l'on a répartis les observations par batch, pour chaque batch, nous allons sélectionné les données d'intérêts dans le datacube. Pour celà on récupère les index des dates minimal `t_min = itime.min()` et maximales `t_max = itime.max()` des observations dans le batch, et on selectionne une tranche du datacube correspondant allant de `t_min - buffer['itime']` à `t_max + buffer['itime']`. 

[Schema batching]