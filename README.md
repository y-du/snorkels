SNORKELS
=======

SNORKELS is a lightweight in memory key-value store with on the fly compression for Python.

*(compreSsed iN memORy KEy vaLue Store)*

---

+ [Description](#description)
+ [Quick start](#quick-start)
+ [Requirements](#requirements)
+ [Installation](#installation)
+ [Usage](#usage)
    + [Logging](#logging)

---

Description
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


#### Logging


