
import pytest
from zpp_store.structure import DataStore, structure, destructure

# Test de la création d'une instance DataStore
def test_datastore_creation():
    ds = DataStore()
    assert isinstance(ds, DataStore)

# Test de la conversion d'un dictionnaire en DataStore
def test_structure_conversion():
    data = {"key1": "value1", "nested": {"key2": 123}}
    ds = structure(data)
    assert ds.key1 == "value1"
    assert ds.nested.key2 == 123

# Test de la conversion d'une DataStore en dictionnaire
def test_destructure_conversion():
    ds = DataStore()
    ds.name = "Test"
    ds.config = DataStore()
    ds.config.version = 1.0
    
    data = destructure(ds)
    
    expected_data = {"name": "Test", "config": {"version": 1.0}}
    assert data == expected_data

# Test de la gestion des espaces dans les noms d'attributs
def test_attribute_with_spaces():
    ds = DataStore()
    setattr(ds, "attribute with space", "value")
    assert getattr(ds, "attribute_with_space") == "value"

# Test du calcul de hash
def test_get_hash():
    data = {"a": 1, "b": [2, 3]}
    ds = structure(data)
    
    # Le hash doit être cohérent
    hash1 = ds.get_hash()
    hash2 = ds.get_hash()
    assert hash1 == hash2
    
    # Un changement dans les données doit produire un hash différent
    ds.a = 5
    hash3 = ds.get_hash()
    assert hash1 != hash3

# Test de la représentation de la classe
def test_repr():
    data = {"a": 1}
    ds = structure(data)
    assert repr(ds) == "{'a': 1}"
