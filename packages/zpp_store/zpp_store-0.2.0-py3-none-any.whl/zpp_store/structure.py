from hashlib import sha256
import json
from .store import Formatstore, Store
import msgpack

class DataStore:
    def __repr__(self):
        return f"{feed_dict({}, self)}"

    def __str__(self):
        return self.__repr__()

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = feed_class(DataStore(), value)

        if " " in name:
            name = name.replace(" ", "_")

        super().__setattr__(name, value)

    def __getattribute__(self, name):
        if " " in name:
            name = name.replace(" ", "_")
        return super().__getattribute__(name)


    def __delattr__(self, name):
        if " " in name:
            name = name.replace(" ", "_")

        super().__delattr__(name)


    #Construit un hash de la class sérialisée
    def get_hash(self):
        with Store(format=Formatstore.to_dict) as vault:
            #Sérialisation de la class
            vault.push("DA", feed_dict({}, self))

            #Création du hash à partir du dictionnaire de résultat
            return sha256(msgpack.packb(vault.get_content())).hexdigest()


#Ajouter les données d'un dictionnaire dans une Class
def feed_class(data_class, data):
    for key, value in data.items():
        if isinstance(value, dict):
            setattr(data_class, key, feed_class(DataStore(), value))
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(feed_class(DataStore(), item))
                else:
                    new_list.append(item)
            setattr(data_class, key, new_list)
        else:
            setattr(data_class, key, value)
    return data_class


#Ajouter les données d'une Class dans un dictionnaire
def feed_dict(data_dict, data):
    for key, value in data.__dict__.items():
        if isinstance(value, DataStore):
            data_dict[key] = feed_dict({}, value)
        elif isinstance(value, list):
            data_dict[key] = [
                feed_dict({}, item) if isinstance(item, DataStore) else item
                for item in value
            ]
        else:
            data_dict[key] = value
    return data_dict


#Dict to Class
def structure(data):
    new_class = DataStore()
    return feed_class(new_class, data)


#Class to Dict
def destructure(data):
    if isinstance(data, DataStore):
        return feed_dict({}, data)
    else:
        raise TypeError(f"Type {type(data)} not supported")