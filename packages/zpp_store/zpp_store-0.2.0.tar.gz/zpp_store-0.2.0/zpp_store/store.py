import yaml
import os
import itertools
import datetime
import decimal
import importlib
import types
import array
import inspect
import io
import msgpack
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from .input import secure_input


class Formatstore():
    to_yaml = 1
    to_binary = 2
    to_dict = 3


class Store:
    def __init__(self, filename=None, password=None, protected=False, format=Formatstore.to_binary):
        self.filename = filename
        self.id_counter = itertools.count(1)  # Générateur d'identifiants uniques
        self.format = format

        if protected and not password:
            password = secure_input("Password store: ")
        self.password = password.encode() if password else None

        # Si le fichier n'existe pas, créez-le avec une liste vide
        if self.filename:
            if os.path.dirname(self.filename) and not os.path.exists(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            #Impossible d'écrire directement un dictionnaire dans un fichier
            if self.format is Formatstore.to_dict:
                raise ValueError(f"Format {self.format} unsupported with output file")

            if not os.path.exists(filename):
                self._write_file({})
        else:
            self._data = {}
            self._write_file({})


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


    def get_content(self):
        return self._data


    def encrypt(self, data):
        salt = os.urandom(16)  # Salt pour le KDF

        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        key = kdf.derive(self.password)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return salt + iv + encrypted_data


    def decrypt(self, data):
        salt = data[:16]
        iv = data[16:32]
        encrypted_data = data[32:]
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        key = kdf.derive(self.password)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()


    def push(self, data_name, data, overwrite=True):
        existing_data = self._read_file()

        keys = data_name.split('.')  # Exemple: ["config", "app"]
        d = existing_data

        # Naviguer dans le dictionnaire en créant les sous-dicts si besoin
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]

        last_key = keys[-1]

        if last_key not in d or overwrite:
            # Si data est un dict, fusionner dans la hiérarchie existante
            if isinstance(data, dict):
                if last_key not in d or not isinstance(d[last_key], dict):
                    d[last_key] = {}
                # Intégrer chaque clé/valeur dans la hiérarchie
                for k, v in data.items():
                    d[last_key][k] = v
            else:
                d[last_key] = self._serialize(data)
        else:
            raise NameError(f"data_name '{data_name}' already exists")

        self._write_file(existing_data)


    def pull(self, data_name):
        existing_data = self._read_file()
        keys = data_name.split('.')
        d = existing_data
        for key in keys:
            if not isinstance(d, dict) or key not in d:
                return None
            d = d[key]
        return self._deserialize(d)


    def erase(self, data_name):
        existing_data = self._read_file()
        
        keys = data_name.split('.')
        d = existing_data

        # Naviguer dans le dict pour atteindre la clé à supprimer
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                return False  # chemin inexistant
            d = d[key]

        last_key = keys[-1]
        if last_key in d:
            del d[last_key]
            self._write_file(existing_data)
            return True

        return False


    def list(self):
        existing_data = self._read_file()
        
        def collect_keys(d, prefix=''):
            keys = []
            for k, v in d.items():
                path = f"{prefix}.{k}" if prefix else k
                keys.append(path)
                if isinstance(v, dict):
                    keys.extend(collect_keys(v, path))
            return keys

        return collect_keys(existing_data)


    def _read_file(self):
        # Lire les données existantes depuis un fichier ou self._data
        if self.filename:
            file_content = open(self.filename, 'rb').read()
        else:
            file_content = self._data

        #Déchiffrer le fichier si besoin
        if self.password:
            file_content = self.decrypt(file_content)

        try:
            if self.format is Formatstore.to_yaml:
                existing_data = yaml.load(file_content, Loader=yaml.SafeLoader)
            elif self.format is Formatstore.to_binary:
                existing_data = msgpack.unpackb(file_content, raw=False, strict_map_key=False)
            elif self.format is Formatstore.to_dict:
                existing_data = self._data
        except Exception as e:
            raise ValueError("Data unpacking failed. Possibly wrong password or corrupted data.") from e

        return existing_data


    def _write_file(self, data):
        # Écrire les données mises à jour
        if self.format is Formatstore.to_yaml:
            data_pack = yaml.dump(data)
            data_pack = data_pack.encode()
        elif self.format is Formatstore.to_binary:
            data_pack = msgpack.packb(data)
        else:
            data_pack = data

        if self.password:
            data_pack = self.encrypt(data_pack)

        if self.format is Formatstore.to_yaml or self.format is Formatstore.to_binary:
            if self.filename:
                file = open(self.filename, 'wb')
                file.write(data_pack)
            else:
                self._data = data_pack
        else:
            self._data = data_pack


    def _serialize(self, data, obj_cache=None):
        if obj_cache is None:
            obj_cache = {}
        
        # Gérer les références circulaires
        obj_id = id(data)
        if obj_id in obj_cache:
            return {'_type': 'ref', '_id': obj_cache[obj_id]}

        # Attribuer un identifiant unique pour chaque nouvel objet
        unique_id = next(self.id_counter)
        obj_cache[obj_id] = unique_id
        
        if isinstance(data, io.BytesIO):
            return {
                '_type': 'BytesIO',
                '_id': unique_id,
                'data': data.getvalue().hex(),
                'position': data.tell(),
                'mode': 'rb'
            }
        elif isinstance(data, io.StringIO):
            return {
                '_type': 'StringIO',
                '_id': unique_id,
                'data': data.getvalue(),
                'position': data.tell(),
                'mode': 'r'
            }
        elif isinstance(data, io.TextIOWrapper):
            original_position = data.tell()
            data.seek(0)
            content = data.read()
            data.seek(original_position)
            return {
                '_type': 'TextIOWrapper',
                '_id': unique_id,
                'data': content,
                'position': original_position,
                'encoding': data.encoding,
                'newline': data.newlines
            }
        elif isinstance(data, io.BufferedReader):
            original_position = data.tell()
            data.seek(0)
            content = data.read()
            data.seek(original_position)
            return {
                '_type': 'BufferedReader',
                '_id': unique_id,
                'data': content.hex(),
                'position': original_position,
                'mode': 'rb'
            }
        elif hasattr(data, '__dict__') and not isinstance(data, types.FunctionType):
            serialized_data = {
                '_type': 'object',
                '_class': data.__class__.__name__,
                '_module': data.__class__.__module__,
                '_id': unique_id,
                'data': {key: self._serialize(value, obj_cache) for key, value in data.__dict__.items()},
                'methods': {name: method.__code__.co_code.hex() for name, method in data.__class__.__dict__.items() if callable(method)},
            }
            return serialized_data
        elif isinstance(data, list):
            return {'_type': 'list', '_id': unique_id, 'data': [self._serialize(item, obj_cache) for item in data]}
        elif isinstance(data, dict):
            return {'_type': 'dict', '_id': unique_id, 'data': {key: self._serialize(value, obj_cache) for key, value in data.items()}}
        elif isinstance(data, (set, frozenset)):
            return {'_type': type(data).__name__, '_id': unique_id, 'data': [self._serialize(item, obj_cache) for item in data]}
        elif isinstance(data, tuple):
            return {'_type': 'tuple', '_id': unique_id, 'data': [self._serialize(item, obj_cache) for item in data]}
        elif isinstance(data, complex):
            return {'_type': 'complex', '_id': unique_id, 'real': data.real, 'imag': data.imag}
        elif isinstance(data, bytes):
            return {'_type': 'bytes', '_id': unique_id, 'data': data.hex()}
        elif isinstance(data, bytearray):
            return {'_type': 'bytearray', '_id': unique_id, 'data': data.hex()}
        elif isinstance(data, array.array):
            return {'_type': 'array', '_id': unique_id, 'typecode': data.typecode, 'data': data.tolist()}
        elif isinstance(data, datetime.datetime):
            return {'_type': 'datetime', '_id': unique_id, 'data': data.timestamp()}
        elif isinstance(data, decimal.Decimal):
            return {'_type': 'decimal', '_id': unique_id, 'value': str(data)}
        elif isinstance(data, types.FunctionType):
            return {
                '_type': 'function',
                '_id': unique_id,
                'name': data.__name__,
                'code': inspect.getsource(data),
                'globals': {k: self._serialize(v, obj_cache) for k, v in data.__globals__.items() if k in data.__code__.co_names},
                'defaults': self._serialize(data.__defaults__, obj_cache),
                'closure': self._serialize([c.cell_contents for c in (data.__closure__ or [])], obj_cache)
            }
        elif isinstance(data, (types.BuiltinFunctionType, types.BuiltinMethodType)):
            return {'_type': 'builtin', '_id': unique_id, 'name': data.__name__}
        elif isinstance(data, str):
            return {'_type': 'str', '_id': unique_id, 'value': data}
        elif isinstance(data, bool):
            return {'_type': 'bool', '_id': unique_id, 'value': data}
        elif isinstance(data, int):
            return {'_type': 'int', '_id': unique_id, 'value': data}
        elif isinstance(data, float):
            return {'_type': 'float', '_id': unique_id, 'value': data}
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")


    def _deserialize(self, data, obj_cache=None):
        if obj_cache is None:
            obj_cache = {}

        # Gérer les références circulaires
        if isinstance(data, dict) and '_type' in data:
            if data['_type'] == 'ref':
                if data['_id'] in obj_cache:
                    return obj_cache[data['_id']]
                else:
                    raise KeyError(f"Reference with id {data['_id']} not found")
            elif data['_type'] == 'BytesIO':
                buf = io.BytesIO(bytes.fromhex(data['data']))
                buf.seek(data['position'])
                obj_cache[data['_id']] = buf
                return buf
            elif data['_type'] == 'StringIO':
                buf = io.StringIO(data['data'])
                buf.seek(data['position'])
                obj_cache[data['_id']] = buf
                return buf
            elif data['_type'] == 'TextIOWrapper':
                buf = io.StringIO(data['data'])
                buf.seek(data['position'])
                wrapped = io.TextIOWrapper(buf, encoding=data['encoding'], newline=data['newline'])
                obj_cache[data['_id']] = wrapped
                return wrapped
            elif data['_type'] == 'BufferedReader':
                buf = io.BytesIO(bytes.fromhex(data['data']))
                buf.seek(data['position'])
                wrapped = io.BufferedReader(buf)
                obj_cache[data['_id']] = wrapped
                return wrapped
            elif data['_type'] == 'object':
                class_name = data['_class']
                module_name = data['_module']
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                obj = cls.__new__(cls)
                obj.__dict__.update({key: self._deserialize(value, obj_cache) for key, value in data['data'].items()})
                obj_cache[data['_id']] = obj
                return obj
            elif data['_type'] == 'datetime':
                return datetime.datetime.fromtimestamp(data['data'])
            elif data['_type'] == 'decimal':
                return decimal.Decimal(data['value'])
            elif data['_type'] == 'complex':
                return complex(data['real'], data['imag'])
            elif data['_type'] == 'bytes':
                return bytes.fromhex(data['data'])
            elif data['_type'] == 'bytearray':
                return bytearray.fromhex(data['data'])
            elif data['_type'] == 'array':
                return array.array(data['typecode'], data['data'])
            elif data['_type'] in ('set', 'frozenset'):
                collection = {self._deserialize(item, obj_cache) for item in data['data']} if data['_type'] == 'set' else frozenset(self._deserialize(item, obj_cache) for item in data['data'])
                obj_cache[data['_id']] = collection
                return collection
            elif data['_type'] == 'list':
                collection = [self._deserialize(item, obj_cache) for item in data['data']]
                obj_cache[data['_id']] = collection
                return collection
            elif data['_type'] == 'dict':
                collection = {key: self._deserialize(value, obj_cache) for key, value in data['data'].items()}
                obj_cache[data['_id']] = collection
                return collection
            elif data['_type'] == 'tuple':
                collection = tuple(self._deserialize(item, obj_cache) for item in data['data'])
                obj_cache[data['_id']] = collection
                return collection
            elif data['_type'] == 'function':
                globals_dict = {}
                for name, value in data['globals'].items():
                    try:
                        globals_dict[name] = eval(value)
                    except:
                        globals_dict[name] = value
                
                exec(data['code'], globals_dict)
                func_name = data['name']
                func = globals_dict[func_name]
                obj_cache[data['_id']] = func
                return func
            elif data['_type'] == 'builtin':
                collection = getattr(__builtins__, data['name'])
                obj_cache[data['_id']] = collection
                return collection
            elif data['_type'] == 'str':
                obj_cache[data['_id']] = data['value']
                return data['value']
            elif data['_type'] == 'int':
                obj_cache[data['_id']] = int(data['value'])
                return int(data['value'])
            elif data['_type'] == 'float':
                obj_cache[data['_id']] = float(data['value'])
                return float(data['value'])
            elif data['_type'] == 'bool':
                obj_cache[data['_id']] = bool(data['value'])
                return bool(data['value'])
        elif isinstance(data, list):
            return [self._deserialize(item, obj_cache) for item in data]
        elif isinstance(data, dict):
            return {key: self._deserialize(value, obj_cache) for key, value in data.items()}
        else:
            return data

    def _sanitize_data(self, data):
        # Vérifiez les types de données avant la sérialisation
        if data is None:
            return data
        elif isinstance(data, (str, int, float, bool, dict, list, tuple, set, frozenset)):
            return data
        elif isinstance(data, (datetime.datetime, decimal.Decimal, complex, bytes, bytearray, array.array)):
            return data
        elif isinstance(data, types.FunctionType):
            return data
        elif isinstance(data, (types.BuiltinFunctionType, types.BuiltinMethodType)):
            return data
        elif hasattr(data, '__dict__'):
            return data
        raise TypeError(f"Unsupported data type: {type(data)}")


