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

    def set(self, key: Union[str, bytes], value: Union[str, bytes]) -> None:
        validateStrOrByt(key, "key")
        validateStrOrByt(value, "value")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        if isinstance(value, str):
            value = bytes(value, self.__encoding)
        self.__store[key] = self.__compress(value)

    def get(self, key: Union[str, bytes]) -> bytes:
        validateStrOrByt(key, "key")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        return self.__decompress(self.__store[key])

    def delete(self, key: Union[str, bytes]) -> None:
        validateStrOrByt(key, "key")
        if isinstance(key, str):
            key = bytes(key, self.__encoding)
        del self.__store[key]

    def keys(self) -> List:
        return list(self.__store.keys())

    def clear(self) -> None:
        self.__store.clear()

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
        return "{}({})".format(__class__.__name__, ", ".join(["=".join([key, str(value)]) for key, value in attributes]))

    def __dump(self):
        with self.__lock:
            with open(path.join(self.__path, "{}.kvs".format(self.__db_name)), "bw") as file:
                for key, value in self.__store.items():
                    file.write(compress(bytes("{}:{}".format(key.hex(), value.hex()), self.__encoding), Z_BEST_COMPRESSION).replace(bytes("\n", self.__encoding), bytes("\\n", self.__encoding)))
                    file.write(bytes("\n", self.__encoding))

    def dump(self):
        dump_thread = Thread(target=self.__dump)
        dump_thread.start()

    def load(self):
        with self.__lock:
            with open(path.join(self.__path, "{}.kvs".format(self.__db_name)), "br") as file:
                for line in file:
                    key, value = self.__decompress(line.replace(bytes("\\n", self.__encoding), bytes("\n", self.__encoding))).split(bytes(":", self.__encoding))
                    self.__store[bytes.fromhex(str(key, self.__encoding))] = bytes.fromhex(str(value, self.__encoding))