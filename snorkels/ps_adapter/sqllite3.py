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


__all__ = ('SQLlite3Adapter', 'SQLlite3ThreadAdapter')


from .interface import Interface
from os import path
from inspect import getfile, stack
from typing import Optional
from sqlite3 import connect as sqlliteConnect
from threading import Thread
from queue import Queue, Empty


class SQLlite3Adapter(Interface):
    def __init__(self, db_name: str, user_path: Optional[str] = None):
        self.__db_name = db_name
        self.__db_path = path.join(
            user_path if user_path else path.abspath(path.split(getfile(stack()[-1].frame))[0]),
            "{}.sqllite3".format(self.__db_name)
        )
        with sqlliteConnect(self.__db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS {}_kvs (key TEXT PRIMARY KEY UNIQUE, value BLOB)".format(self.__db_name)
            )
        conn.close()

    def create(self, key, value):
        with sqlliteConnect(self.__db_path) as conn:
            conn.execute(
                "INSERT INTO {}_kvs (key, value) VALUES (?, ?)".format(self.__db_name), (str(key, "UTF-8"), value)
            )
        conn.close()

    def readItems(self):
        with sqlliteConnect(self.__db_path) as conn:
            for row in conn.execute("SELECT * FROM {}_kvs".format(self.__db_name)):
                yield row
        conn.close()

    def update(self, key, value):
        with sqlliteConnect(self.__db_path) as conn:
            conn.execute("UPDATE {}_kvs SET value=(?) WHERE key=(?)".format(self.__db_name), (value, str(key, "UTF-8")))
        conn.close()

    def delete(self, key):
        with sqlliteConnect(self.__db_path) as conn:
            conn.execute("DELETE FROM {}_kvs WHERE key=(?)".format(self.__db_name), (str(key, "UTF-8"), ))
        conn.close()

    def clear(self):
        with sqlliteConnect(self.__db_path) as conn:
            conn.execute("DROP TABLE IF EXISTS {}_kvs".format(self.__db_name))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS {}_kvs (key TEXT PRIMARY KEY UNIQUE, value BLOB)".format(self.__db_name)
            )
        conn.close()
