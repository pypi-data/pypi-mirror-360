# Optimization

```{note}
Work In Progress
```

C'est là qu'intervient l'argument `optimize`. Jusqu'ici toutes les opérations prcédentes ont été réalisé de manière paresseuses. Ainsi Dask a créé un arbre des tâches qui sera exécuter sur le cluster lorsque l'on appellera la fonction `compute`. 

Cependant il existe 2 manière de construire cet arbre des tâches, chacune ayant ses avantages et ses inconvénients. 

## Optimize == False

La 1ère méthode qui correspond à `optimize=False` dans PytCube, revient à construire un arbre des tâches qui commence par ouvrir en mémoire l'ensemble de la tranche du datacube, puis a selectionner les MiniCube à l'intérieur, c'est une méthode `brute force` dans le sens où on lis toute la données pour ne selectionner que celle qui nous intérèsse, l'avantage est que l'arbre des tâches est très rapide à construire, et que si l'on a assez de RAM et une données en local facilement accessible, elle est dans la majorité des cas, la méthode la plus rapide. L'inconvénient est que pour des jeux de données très volumineux, elle nécéssite beaucoup de RAM, où alors de limiter la taille des tranches du Datacube en limitant la valeur de `n_obs_per_batch`. 

[Schéma Dask.visualize]

## Optimize == True

La 2ème méthode qui correspond à `optimize=True` dans PytCube, revient à construire un arbre des tâches optimisé qui ouvre uniquement les chunks d'intérets qui ne selectionne que la données d'intérêt, qui ferme le chunk avant de passer à celui d'après. Cette méthode est optimisé dans le sens où elle nécéssite peux de ressource en RAM, ce qui est de loin son grand avantage. L'inconvénient est que pour des MiniCubes avec de grande dimensions, la construction de l'arbre des tâches peux prendre beaucoup de temps (dans certain cas, vraiment beaucoup de temps.). De plus l'arbre des tâches peux lui même devenir assez volumineux, ce qui est en plus de prendre du temps à être construit, prend du temps à le transférer au scheduler et à l'initialiser. Dans le cas où l'on se trouve avec des données accessible à distance et des minicubes ayant des petites dimensions, il peux être intéressant d'utiliser cette méthode pour limiter la quantité de donnée à télécharger. 

## Synthèse

En conclusion, 2 paramètres vont principalement guider notre choix:
- La rapidité de lecture des données (par exemple: local VS S3). 
- La taille des minicubes à extraire.
