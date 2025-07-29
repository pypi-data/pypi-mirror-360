# zpp_store

## Informations

Outil de sérialisation d'objet Python.
Il peut prendre en charge:
- les formats classiques: str, int, float, bool, type, none, complex, bytes, decimal
- les formats structurés: list, dict, tuple, array, bytearray, frozenset
- les formats io: BytesIO, StringIO, TextIOWrapper, BufferedReader
- les objets: Class, datetime, function, builtin function

Le fichier de sortie peut-être soit un yaml, soit un fichier binaire; et celui-ci peut être chiffré avec un mot de passe.
Le système fonctionne comme un coffre dans lequel on peut stocker plusieurs données et utilise le système clé/valeur pour identifier les données.

Il intègre également un outil pour stocker des données sous forme de Class pour les structurer et faciliter leurs manipulations.

### Prérequis
- Python 3

## Installation


```shell
pip install zpp_store
```

## Utilisation
### Initialisation du connecteur

Le store est accessible de deux façons:
- En initialisant le store dans une variable
```python
import zpp_store

vault = zpp_store.Store()
```
- Ou avec la méthode **with**
```python
import zpp_store

with zpp_store.Store() as vault:
	'''Traitement'''
```

La Classe Store peut prendre plusieurs arguments:
- ***filename***: pour spécifier le fichier de sortie
	Si le fichier de sortie n'est pas précisé, le résultat restera dans le stockage de la classe. Il sera alors possible de récupérer le résultat avec la méthode **get_content()**
- ***protected***: pour spécifier si le fichier doit être chiffré (si le mot de passe n'est pas spécifié. Un prompt demandera le mot de passe)
- ***password***: pour spécifier le mot de passe pour le chiffrement (active protected)
- ***format***: pour spécifier le format de sortie. **zpp_store.Formatstore.to_yaml**, **zpp_store.Formatstore.to_binary** ou **zpp_store.Formatstore.to_dict**. 
	Attention, le format to_dict n'accepte pas la sortie dans un fichier.
<br>

###  Sérialisation de données

Pour sérialiser des données, il suffit d'appeler la classe **Store** et d'utiliser la méthode **push** avec comme paramètre le nom de la clé à utiliser et la donnée à sérialiser.

```python
import zpp_store

class Person:
	def __init__(self, name, age, city):
		self.name = name
		self.age = age
		self.city = city

new_person = Person("Bob", 35, "Paris")

with zpp_store.Store() as vault:
	vault.push("utilisateur_bob", new_person)
```

Possibilité de travailler avec des données hiérarchiques en séparant les clés par un point.
```python
vault.push("config.app.data", "data_line")  #Ce qui donnera {"config": {"app": {"data": "data_line"}}}
```

<br>

###  Désérialisation de données

Pour désérialiser des données, il suffit d'appeler la classe **Store** et d'utiliser la méthode **pull** avec comme paramètre le nom de la clé à récupérer.

```python
import zpp_store

class Person:
	def __init__(self, name, age, city):
		self.name = name
		self.age = age
		self.city = city

with zpp_store.Store() as vault:
	new_person = vault.pull("utilisateur_bob")
```
<br>

### Suppression de données

Il est possible de supprimer des données avec la méthode **erase()** en précisant en paramètre la clé.

```python
import zpp_store

with zpp_store.Store() as vault:
	vault.erase("utilisateur_bob")
```

La méthode retournera alors **True** si une donnée a été supprimée, sinon **False**.
<br>

### Liste des clés

Il est possible de lister l'ensemble des clés disponibles dans un store.

```python
import zpp_store

with zpp_store.Store() as vault:
	print(vault.list()) # Affiche: ['app', 'app.config', 'app.users']
```

### Structuration de données

Il est possible de structurer un dictionnaire pour le transformer en **DataStore** et pour nous permettre de manipuler ces données comme une Class avec a.b.c
Pour cela, il nous suffit d'appeler la méthode **structure()** avec comme argument le dictionnaire

```python
import zpp_store

dict_data = {"Bonjour": "Hello world", "Data": {"insert": True, "false": True}}

data = zpp_store.structure(dict_data)
```

Le dictionnaire devient alors un **zpp_store.structure.DataStore**

Pour permettre de contrôler la modification, le DataStore permet de récupérer un hash du contenu avec la méthode **get_hash()**

```python
import zpp_store

dict_data = {"Bonjour": "Hello world", "Data": {"insert": True, "false": True}}

data = zpp_store.structure(dict_data)
hash_dict = data.get_hash()
```
<br>

### Déstructuration de données

Pour récupérer un dictionnaire à partir d'un **DataStore**, il suffit d'appeler la méthode **destructure()**.

```python
import zpp_store

data = zpp_store.destructure(datastore)
```