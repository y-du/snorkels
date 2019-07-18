SNORKELS
=======

SNORKELS is a lightweight in memory key-value store with on the fly compression for Python.

*(compreSsed iN memORy KEy vaLue Store)*

---

+ [Quick start](#quick-start)
+ [Requirements](#requirements)
+ [Installation](#installation)
+ [Usage](#usage)
    + [Creating a key-value store](#creating-a-key-value-store)
    + [Setting, getting and deleting values](#setting-getting-and-deleting-values)
    + [Compression levels](#compression-levels)
    + [Adding persistence](#adding-persistence)
    + [Logging](#logging)

---


Quick start
---
    import snorkels
    
    kvs = snorkels.KeyValueStore(name="test")
    
    kvs.set("key_a", "some data")
    value = kvs.get("key_a")
    kvs.delete("key_a")


Requirements
----

Python 3.5 or later.


Installation
----

Install the `snorkels` package via pip by issuing the following command with the desired release `X.X.X`: 

- `pip install git+https://github.com/y-du/snorkels.git@X.X.X` 

Upgrade to new version: 

- `pip install --upgrade git+https://github.com/y-du/snorkels.git@X.X.X`

Uninstall: 

- `pip uninstall snorkels`


Usage
----

#### Creating a key-value store

To create a key-value store simply import `snorkels` and use the provided `KeyValueStore` class:
 
    import snorkels
    
    kvs = snorkels.KeyValueStore(name, comp_lvl=CompLevel.default, ps_adapter=None)

- `name` required, name of the key-value store as `str`.

- `comp_lvl` optional, set the compression level. See [Compression levels](#compression-levels) for more.

- `ps_adapter` optional, provide your own database adapter. See [Adding persistence](#adding-persistence) for more.


#### Setting, getting and deleting values

Add / Update a value:

    kvs.set(key, value)

- `key` required, can be `str` or `bytes`.

- `value` required, can be `str` or `bytes`.

Get a value:

    kvs.get(key)

- `key` required, can be `str` or `bytes`.

- Returns `bytes`.

Delete a value:

    kvs.delete(key)

- `key` required, can be `str` or `bytes`.

Get all keys:

    kvs.keys()

- Returns a `list` of all keys as `bytes`.

Clear key-value store:

    kvs.clear()

#### Compression levels

For compression `snorkels` uses the python `zlib` module. By default the `zlib` module provides different compression levels. These levels can be accessed via `CompLevel`:

    snorkels.CompLevel.default
    snorkels.CompLevel.none
    snorkels.CompLevel.minimal
    snorkels.CompLevel.very_low
    snorkels.CompLevel.low
    snorkels.CompLevel.medium_low
    snorkels.CompLevel.medium
    snorkels.CompLevel.medium_high
    snorkels.CompLevel.high
    snorkels.CompLevel.very_high
    snorkels.CompLevel.maximum

#### Adding persistence

If data persistence is required you can implement your own database adapter or use the provided `SQLlite3Adapter`.

    db_adapter = snorkels.ps_adapter.SQLlite3Adapter(db_name, user_path=None)
    
- `db_name` required, name of the database as `str`.

- `user_path` optional, if set the database will be saved to the specified location. Default is working dictionary.

To create your own adapter please use the provided interface:

    class MyAdapter(snorkels.ps_adapter.Interface):
        def create(self, key, value):
            # your code

        def readItems(self):
            # your code
    
        def update(self, key, value):
            # your code
    
        def delete(self, key):
            # your code
    
        def clear(self):
            # your code

#### Logging

If your project uses the python `logging` facility you can combine the output produced by `snorkels` with your log output.

Retrieve the "snorkels" logger via:

    logger = logging.getLogger("snorkels")

Add your handler to the logger and Optionally set the desired level:

    logger.addHandler(your_handler)
    logger.setLevel(logging.INFO)   # optional
