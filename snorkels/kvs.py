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


__all__ = ('KeyValueStore', 'KVSError', 'CompressionError', 'DecompressionError')


from .util import validateStrOrByt
from typing import Union, Optional, List
from zlib import compress, decompress, Z_DEFAULT_COMPRESSION, Z_BEST_COMPRESSION
from zlib import error as ZLibError
from os import path
from inspect import getfile, stack
from threading import Thread, Lock


class KVSError(Exception):
    pass


class CompressionError(KVSError):
    pass


class DecompressionError(KVSError):
    pass


class KeyValueStore:
    def __init__(self, db_name: str, user_path: str = None, compression_lvl: Optional[int] = None, encoding: str = "UTF-8"):
        if not all((isinstance(db_name, str), isinstance(user_path, (str, type(None))), isinstance(compression_lvl, (int, type(None))), isinstance(encoding, str))):
            raise TypeError
        self.__db_name = db_name
        self.__path = user_path if user_path else path.abspath(path.split(getfile(stack()[-1].frame))[0])
        self.__compr_lvl = compression_lvl or Z_DEFAULT_COMPRESSION
        self.__encoding = encoding
        self.__store = dict()
        self.__lock = Lock()

    def __setitem__(self, key: Union[str, bytes], value: Union[str, bytes]) -> None:
        self.set(key, value)

    def __getitem__(self, item: Union[str, bytes]) -> bytes:
        return self.get(item)

    def __delitem__(self, key: Union[str, bytes]) -> None:
        self.delete(key)

    def __compress(self, value: bytes) -> bytes:
        try:
            return compress(value, self.__compr_lvl)
        except ZLibError as ex:
            raise CompressionError(ex)

    def __decompress(self, value: bytes) -> bytes:
        try:
            return decompress(value)
        except ZLibError as ex:
            raise DecompressionError(ex)

    def set(self, key: Union[str, int, float, bytes], value: Union[str, bytes]) -> None:
        validateType(key, "key", (str, int, float, bytes))
        validateType(value, "value", (str, bytes))
        if isinstance(value, str):
            value = bytes(value, self.__encoding)
        self.__store[key] = self.__compress(value)

    def get(self, key: Union[str, int, float, bytes]) -> str:
        validateType(key, "key", (str, int, float, bytes))
        return str(self.__decompress(self.__store[key]), encoding=self.__encoding)

    def delete(self, key: Union[str, int, float, bytes]) -> None:
        validateType(key, "key", (str, int, float, bytes))
        del self.__store[key]

    def keys(self) -> List:
        return list(self.__store.keys())

    def values(self) -> List:
        return [str(self.__decompress(value), encoding=self.__encoding) for value in self.__store.values()]

    def clear(self) -> None:
        self.__store.clear()

    def __repr__(self):
        size = 0
        for value in self.__store.values():
            size += len(value)
        size = size / 1024
        attributes = [
            ('keys', len(self.__store.keys())),
            ('size', "{}KiB".format(round(size)))
        ]
        return "{}({})".format(__class__.__name__, ", ".join(["=".join([key, str(value)]) for key, value in attributes]))

    def dump(self, n, c=True):
        with open(n, "ba") as file:
            for key, value in self.__store.items():
                file.write(pickleDumps((key, value)))
        del file


    def load(self):
        with open("test.kvs", "br") as file:
            return pickleLoads(decompress(file.read()))