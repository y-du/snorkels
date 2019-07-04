"""
   Copyright 2019 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


__all__ = (
    'KeyValueStore',
    'CompLevel',
    'Encoding',
    'KVSError',
    'SetError',
    'GetError',
    'DeleteError',
    'DumpError',
    'LoadError'
)


from .util import validateStrOrByt
from typing import Union, List
from zlib import compress, decompress, Z_DEFAULT_COMPRESSION, Z_NO_COMPRESSION, Z_BEST_COMPRESSION, Z_BEST_SPEED
from zlib import error as ZLibError
from os import path
from inspect import getfile, stack
from threading import Thread, Lock
from logging import getLogger


_root_logger = getLogger('snorkels')
_root_logger.propagate = False


class KVSError(Exception):
    pass


class SetError(KVSError):
    def __init__(self, key, ex, logger):
        logger.error("Error setting value for key '{}' - {}".format(key.decode(), ex))
        super().__init__(ex)


class GetError(KVSError):
    def __init__(self, key, ex, logger):
        logger.error("Error getting value for key '{}' - {}".format(key.decode(), ex))
        super().__init__(ex)


class DeleteError(KVSError):
    def __init__(self, key, ex, logger):
        logger.error("Error deleting key '{}' - {}".format(key.decode(), ex))
        super().__init__(ex)


class DumpError(KVSError):
    def __init__(self, ex, logger):
        logger.error("Error dumping to file - {}".format(ex))
        super().__init__(ex)


class LoadError(KVSError):
    def __init__(self, ex, logger):
        logger.error("Error loading from file - {}".format(ex))
        super().__init__(ex)


class CompLevel:
    default = Z_DEFAULT_COMPRESSION
    none = Z_NO_COMPRESSION
    minimal = Z_BEST_SPEED
    very_low = 2
    low = 3
    medium_low = 4
    medium = 5
    medium_high = 6
    high = 7
    very_high = 8
    maximum = Z_BEST_COMPRESSION


class Encoding:
    utf_8 = "UTF-8"
    ascii = "ASCII"


class KeyValueStore:
    __extension = "kvs"

    def __init__(self, db_name: str, user_path: str = None, comp_lvl: int = CompLevel.default, encoding: str = Encoding.utf_8):
        if not all((
                isinstance(db_name, str),
                isinstance(user_path, (str, type(None))),
                isinstance(comp_lvl, (int, type(None))),
                isinstance(encoding, str)
        )):
            raise TypeError
        self.__db_name = db_name
        self.__path = user_path if user_path else path.abspath(path.split(getfile(stack()[-1].frame))[0])
        self.__comp_lvl = comp_lvl
        self.__encoding = encoding
        self.__store = dict()
        self.__lock = Lock()
        self.__logger = _root_logger.getChild(self.__db_name)
        self.__load()

    def set(self, key: Union[str, bytes], value: Union[str, bytes]) -> None:
        validateStrOrByt(key, "key")
        validateStrOrByt(value, "value")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        if isinstance(value, str):
            value = bytes(value, self.__encoding)
        try:
            self.__store[key] = compress(value, self.__comp_lvl)
        except MemoryError as ex:
            raise SetError(key, ex, self.__logger)
        except ZLibError as ex:
            raise SetError(key, ex, self.__logger)

    def get(self, key: Union[str, bytes]) -> bytes:
        validateStrOrByt(key, "key")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        try:
            return decompress(self.__store[key])
        except KeyError as ex:
            raise GetError(key, ex.__class__.__name__, self.__logger)
        except ZLibError as ex:
            raise GetError(key, ex, self.__logger)

    def delete(self, key: Union[str, bytes]) -> None:
        validateStrOrByt(key, "key")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        try:
            del self.__store[key]
        except KeyError as ex:
            raise DeleteError(key, ex.__class__.__name__, self.__logger)

    def keys(self) -> List:
        return list(self.__store.keys())

    def clear(self) -> None:
        self.__store.clear()

    def dump(self):
        dump_thread = Thread(target=self.__dump)
        dump_thread.start()

    def __dump(self):
        with self.__lock:
            try:
                with open(path.join(self.__path, "{}.{}".format(self.__db_name, __class__.__extension)), "w") as file:
                    for key, value in self.__store.items():
                        file.write(key.hex() + ":" + value.hex() + "\n")
                self.__logger.info(
                    "Dumped data to file '{}'".format(
                        path.join(self.__path, "{}.{}".format(self.__db_name, __class__.__extension))
                    )
                )
            except IOError as ex:
                raise DumpError(ex, self.__logger)

    def __load(self):
        try:
            with open(path.join(self.__path, "{}.{}".format(self.__db_name, __class__.__extension)), "r") as file:
                for line in file:
                    key, value = line.split(":")
                    self.__store[bytes.fromhex(key)] = bytes.fromhex(value)
            self.__logger.info(
                "Loaded data from file '{}'".format(
                    path.join(self.__path, "{}.{}".format(self.__db_name, __class__.__extension))
                )
            )
        except FileNotFoundError:
            pass
        except IOError as ex:
            raise LoadError(ex, self.__logger)

    def __repr__(self):
        size = 0
        for value in self.__store.values():
            size += len(value)
        for key in self.__store.keys():
            size += len(key)
        size = size / 1024
        attributes = [
            ("name", self.__db_name),
            ("keys", len(self.__store.keys())),
            ("size", "{}KiB".format(round(size)))
        ]
        return "{}({})".format(
            __class__.__name__, ", ".join(["=".join([key, str(value)]) for key, value in attributes])
        )
