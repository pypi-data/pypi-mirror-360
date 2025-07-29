
import pytest
import os
import zpp_store

class MyObject:
    def __init__(self, x):
        self.x = x

# Test de la création d'un Store en mémoire
def test_in_memory_store():
    with zpp_store.Store() as store:
        store.push("key", "value")
        assert store.pull("key") == "value"

# Test de la création d'un Store avec un fichier
def test_file_based_store():
    filename = "test.dat"
    with zpp_store.Store(filename) as store:
        store.push("data.point", {"a": 1})
        assert store.pull("data.point") == {"a": 1}
    os.remove(filename)

# Test du chiffrement et du déchiffrement
def test_encryption():
    filename = "encrypted.dat"
    password = "my-secret-password"
    with zpp_store.Store(filename, password=password, protected=True) as store:
        store.push("secret", "my-secret-data")
        assert store.pull("secret") == "my-secret-data"
    os.remove(filename)

# Test de la suppression de données
def test_erase():
    with zpp_store.Store() as store:
        store.push("to_delete", "some_value")
        assert store.pull("to_delete") is not None
        store.erase("to_delete")
        assert store.pull("to_delete") is None

# Test de la liste des clés
def test_list_keys():
    with zpp_store.Store() as store:
        store.push("a.b.c", 1)
        store.push("a.d", 2)
        keys = store.list()
        assert "a.b.c" in keys
        assert "a.d" in keys

# Test de la sérialisation/désérialisation d'objets complexes
def test_complex_serialization():
    obj = MyObject(10)
    
    with zpp_store.Store() as store:
        store.push("my.class", obj)
        retrieved_obj = store.pull("my.class")
        assert isinstance(retrieved_obj, MyObject)
        assert retrieved_obj.x == 10
