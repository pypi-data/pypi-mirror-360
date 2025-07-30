# Overview

_Nested collections wrapper_


## Purpose

> Prevent square brackets overkill

Read and/or modify data in nested collections with simplified addressing,
e.g. to replace

``` python
value = nested_collection["data"]["attributes"]["parent"]["id"]
```

by

``` python
value = structure["data.attributes.parent.id"]
```

or

``` python
value = structure["data", "attributes", "parent", "id"]
```


!!! tip "not a replacement for jq or yq"

    **ncw** is _not_ intended as a replacement for **[jq]** or **[yq]**.
    For example, it does not even offer a commandline tool for data access.

    **Please also note:** while path address syntax might look similar
    at a superficial first glance, it is completely distinct from the
    **[jq language][jq]**.


## Installation

``` bash
pip install ncw
```


## Basic usage

!!! abstract inline end "separated from original data"

    Both classes do not store the data structure itself provided at initialization
    but a [deep copy] of it – in order to prevent accidental changes to the original data.

The **[Structure class]** prevents accidental changes to the underlying data structure
by preventing direct access.
All returned substructures are deep copies of the internally stored substructures.

The **[MutableStructure class]** allows changes (ie. deletions and updates)
to the underlying data structure, and returns the internally stored substructures themselves.



``` pycon
>>> serialized = '{"herbs": {"common": ["basil", "oregano", "parsley", "thyme"], "disputed": ["anise", "coriander"]}}'
>>>
>>> import json
>>> original_data = json.loads(serialized)
>>>
>>> from ncw import Structure, MutableStructure
>>>
>>> readonly = Structure(original_data)
>>> readonly["herbs"]
{'common': ['basil', 'oregano', 'parsley', 'thyme'], 'disputed': ['anise', 'coriander']}
>>> readonly["herbs.common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common"]
['basil', 'oregano', 'parsley', 'thyme']
>>> readonly["herbs", "common", 1]
'oregano'
>>> readonly["herbs.common.1"]
'oregano'
>>> readonly["herbs.common.1"] = "marjoram"
Traceback (most recent call last):
  File "<python-input-9>", line 1, in <module>
    readonly["herbs.common.1"] = "marjoram"
    ~~~~~~~~^^^^^^^^^^^^^^^^^^
TypeError: 'Structure' object does not support item assignment
>>>
>>> writable = MutableStructure(original_data)
>>> writable.data == original_data
True
>>> writable.data is original_data
False
>>> writable["herbs.common.1"]
'oregano'
>>> writable["herbs.common.1"] = "marjoram"
>>> del writable["herbs", "common", 2]
>>> writable["herbs.common"]
['basil', 'marjoram', 'thyme']
>>>
```

* * *
[jq]: https://jqlang.org/
[yq]: https://github.com/kislyuk/yq
[deep copy]: https://docs.python.org/3/library/copy.html#copy.deepcopy
[Structure class]: 1-structure.md
[MutableStructure class]: 2-mutable-structure.md
