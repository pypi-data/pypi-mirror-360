# MutableStructure class

> Subclass of the [Structure class]:
> a wrapper around a [Nested Collection] providing **read and write access**.
>
> Class defined in the **wrappers** module and additionally exposed at package level

``` python
from ncw import MutableStructure
```

## Initialization arguments

> Either a [Nested Collection]
> or another [Structure class] (or subclass thereof) instance,
> and an optional **separator** argument
> which must be a single unicode character (default: ASCII dot `.`).
> Same as in the [parent class][Structure class].

Initializing from another MutableStructure or [Structure class] instance
is a simple way to clone that instance:

``` python
new_instance = MutableStructure(existing_instance)
```

However, the same could also be achieved using

``` python
new_instance = MutableStructure(existing_instance.data)
```

> _added in version 0.4.0:_ Allow initialization from another instance

!!! example

``` pycon
>>> mutable_structure_instance = MutableStructure({"a":{"b": {"cde": 123}}})
```


## Interface

### Readonly properties

#### .data

> a [deep copy] of the [Nested Collection] the instance was initialized with.

!!! note

    In MutableStructure instances, the internally stored data structure
    is returned directly.


#### .is_mutable

> a boolean value, initially `True`.
> Can be irreversibly changed to `False` by calling the [.freeze()] method.


#### .parsing_cache

> a [cache.ParsingCache] instance initialized with the **separator** argument
> same as in the [Structure class]


[cache.ParsingCache] instances per separator character are shared
across all **Structure** (and subclasses) instances
(that mechanism currently uses an internal **dict** instance,
but that will be changed to a more foolproof implementation in a future release).


### Capabilities through special methods

#### instance\[pathspec\]

!!! abstract inline end "Implementation detail"

    Item read access is implemented by calling the [.get()] method internally.

> **Item read access (via \_\_getitem\_\_)**
>
>     value = mutable_structure_instance[pathspec]
>
> returns the value located at **pathspec** in the structure,
> in contrast to the parent class where only a [deep copy] is returned.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> mutable_structure_instance["a.b.cde"] == mutable_structure_instance["a", "b", "cde"] == 123
True
```


#### del instance\[pathspec\]

!!! abstract inline end "Implementation detail"

    Item deletion is implemented by calling the [.delete()] method internally.

> **Item deletion (via \_\_delitem\_\_)**
>
>     del mutable_structure_instance[pathspec]
>
> deletes the value located at **pathspec** in the structure.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> del mutable_structure_instance["a.b"]
```


#### instance\[pathspec\] = new\_value

!!! abstract inline end "Implementation detail"

    Item write access is implemented by calling the [.update()] method internally.

>  **Item write access (via \_\_setitem\_\_)**
>
>     mutable_structure_instance[pathspec] = new_value
>
> sets the value located at **pathspec** in the structure
> to the new value.
> If the path does not exist yet in the data structure, intermediate parts
> are created automatically (as dicts only) if possible.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> mutable_structure_instance["a.b.ghi"] = 1023
>>> mutable_structure_instance["a", "b", "ghi"] == 1023
True
>>> mutable_structure_instance["ff.fe"] = 65534
>>> mutable_structure_instance["x", "y"] = "ZZZ-new"
```


#### instance1 == instance2, instance1 != instance2

> **Comparison for (in)equality (via \_\_eq\_\_)**
>
> _added in version 0.4.0_
>
>     mutable_structure_instance_1 == mutable_structure_instance_2
>     mutable_structure_instance_1 != mutable_structure_instance_2
>
> returns `True` or `False` according to equality or inequality
> of all of both instances’ [.data], [.is_mutable], and [.parsing_cache].separator
> properties,same as in the parent class.

!!! example

``` pycon
>>> mutable_structure_instance == MutableStructure({'a': {}, 'ff': {'fe': 65534}, 'x': {'y': 'ZZZ-new'}\
}, separator='.')
True
>>> mutable_structure_instance == MutableStructure({"a":{"b": {"cde": 123}}})
False
>>> mutable_structure_instance == MutableStructure({'a': {}, 'ff': {'fe': 65534}, 'x': {'y': 'ZZZ-new'}\
}, separator='/')
False
>>> mutable_structure_instance != MutableStructure({'a': {}, 'ff': {'fe': 65534}, 'x': {'y': 'ZZZ-new'}\
}, separator='/')
True
```


#### repr(instance)

> **String representation (via \_\_repr\_\_)**
>
> _added in version 0.3.1_
>
>     repr(mutable_structure_instance)
>
> Same as in the parent class.

!!! example

    The statement printed here could be used to create a new Structure instance
    that compares equal:

``` pycon
>>> print(repr(mutable_structure_instance))
MutableStructure({'a': {}, 'ff': {'fe': 65534}, 'x': {'y': 'ZZZ-new'}}, separator='.')
```


### Methods


#### .delete()

>     mutable_structure_instance.delete(pathspec)
>
> deletes the value located at **pathspec**.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> mutable_structure_instance
MutableStructure({'a': {}, 'ff': {'fe': 65534}, 'x': {'y': 'ZZZ-new'}}, separator='.')
>>> mutable_structure_instance.delete("ff")
>>> mutable_structure_instance
MutableStructure({'a': {}, 'x': {'y': 'ZZZ-new'}}, separator='.')
```


#### .freeze()

>     mutable_structure_instance.freeze()
>
> Irreversibly makes the instance immutable,
> changing the behavior of the [.data] property and the [.get()]
> method to return {deep copies}[deep copy] instead of the
> internally stored data itself.
>
> Returns a list of diagnostic strings.

!!! example

    Working on a copy here to ensure the following examples still work

``` pycon
>>> msi_clone = MutableStructure(mutable_structure_instance)
>>> msi_clone.is_mutable
True
>>> msi_clone.freeze()
['MutableStructure instance changed to immutable', 'the .get() method will from now on return a deep copy of the found substructure']
>>> msi_clone.is_mutable
False
>>> msi_clone.freeze()
['No change, MutableStructure instance had already been immutable']
```


#### .get()

!!! failure inline end "No traversal through leaves"

    Raises a **TypeError** if _pathspec_ would require walking
    through a leaf (ie. a [scalar value] somewhere in the data structure).

>     value = mutable_structure_instance.get(pathspec)
>
> returns the value located at **pathspec** in the structure,
> in contrast to the parent class where only a [deep copy] is returned.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> mutable_structure_instance.get("x.y") == mutable_structure_instance.get(("x", "y")) == "ZZZ-new"
True
```


#### .get_with_default()

> _added in version 0.4.1_
>
>     value = mutable_structure_instance.get_with_default(pathspec, default)
>
> returns the value located at **pathspec** in the structure,
> or **default** if `mutable_structure_instance.get(pathspec)` would raise a
> **KeyError** or **IndexError**.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].
**default** must be suitable as a return value (ie. [ValueType]).

!!! example

``` pycon
>>> mutable_structure_instance.get("a.b.cde")
(…)
KeyError: 'b'
>>> mutable_structure_instance.get_with_default("a.b.cde", "fallback value")
'fallback value'
```


#### .iter_canonical_endpoints()

> _added in version 0.4.0_
>
>     for path in mutable_structure_instance.iter_canonical_endpoints():
>         print(path)
>
> returns an Iterator over canonical path representations for all endpoints
> (ie. items in the datastructure that are either a [scalar value]
> or an empty [collection].
> Same as in the parent class.

!!! example

``` pycon
>>> for path in mutable_structure_instance.iter_canonical_endpoints():
...     print(path)
...
a
x.y
```

#### .update()

>     mutable_structure_instance.update(pathspec, new_value)
>
> sets the value located at **pathspec** to **new_value**,
> creating intermediate data structure parts if necessary and possible.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> mutable_structure_instance
MutableStructure({'a': {}, 'x': {'y': 'ZZZ-new'}}, separator='.')
>>> mutable_structure_instance.update(("math", "pi"), 3.14159)
>>> mutable_structure_instance
MutableStructure({'a': {}, 'x': {'y': 'ZZZ-new'}, 'math': {'pi': 3.14159}}, separator='.')
```


* * *
[Structure class]: 1-structure.md
[Nested Collection]: 5-glossary.md#nested-collection
[deep copy]: https://docs.python.org/3/library/copy.html#copy.deepcopy
[cache.ParsingCache]: 3-cache.md#parsingcache
[IndexType]: 5-glossary.md#indextype
[ValueType]: 5-glossary.md#valuetype
[SegmentsTuple]: 5-glossary.md#segmentstuple
[.data]: #data
[.is_mutable]: #is_mutable
[.parsing_cache]: #parsing_cache
[.freeze()]: #freeze
[.get()]: #get
[.update()]: #update
[.delete()]: #delete
[scalar value]: 5-glossary.md#scalartype
[collection]: 5-glossary.md#collectiontype
