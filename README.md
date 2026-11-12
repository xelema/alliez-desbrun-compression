# Compression progressive de maillages

Implémentation de l'algorithme d'Alliez et Desbrun (2001), avec une sortie au format OBJA.

## Installation

Il faut Python 3 et numpy.

```
pip install numpy
```

## Compresser un modèle

Depuis la racine du dépôt :

```
python compress.py demo/example/suzanne.obj
```

Le fichier `demo/example/suzanne.obja` est créé à côté du fichier d'entrée.
Les options sont listées avec `python compress.py -h`.

## Visualiser le résultat

```
cd demo
python server.py
```

Puis ouvrir http://localhost:8000/?example/suzanne.obja dans un navigateur.

## Tests

Un script par pôle, à lancer depuis la racine :

```
python tests/test_pole1.py
python tests/test_pole2.py
python tests/test_pole3.py
python tests/test_pole4.py
```
