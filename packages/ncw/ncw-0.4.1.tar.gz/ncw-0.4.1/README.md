# ncw

_Nested collections wrapper_

Classes to access and/or modify data in nested collections (**dict** or **list** instances)
of **str**, **int**, **float**, **bool**, or `None`.


## Usage

Use the **Structure** class to access (deep) copies of substructures by either
a string comprised of the segments of the keys or indexes in the "path" addressing the
substructure or value in the nested collection, joined together by a separator character
(usually an ASCII dot: `.`), or a tuple of these path segments.

``` pycon
>>> serialized = '{"herbs": {"common": ["basil", "oregano", "parsley", "thyme"], "disputed": ["anise", "coriander"]}}'
>>>
>>> import json
>>> original_data = json.loads(serialized)
>>>
>>> from ncw import Structure
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
```

The **MutableStructure** class allows changes to the underlying data structure,
see the [documentation] for more details.

* * *
[documentation]: https://blackstream-x.gitlab.io/ncw
