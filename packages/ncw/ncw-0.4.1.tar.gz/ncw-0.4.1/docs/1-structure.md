# Structure class

> A wrapper around a [Nested Collection] providing **readonly access**.
>
> Class defined in the **wrappers** module and additionally exposed at package level

``` python
from ncw import Structure
```


## Initialization arguments

> Either a [Nested Collection]
> or another Structure (or subclass thereof) instance,
> and an optional **separator** argument
> which must be a single unicode character (default: ASCII dot `.`).

Initializing from another Structure instance is a simple way
to clone that instance:

``` python
new_instance = Structure(existing_instance)
```

However, the same could also be achieved using

``` pythom
new_instance = Structure(existing_instance.data)
```

> _added in version 0.4.0:_ Allow initialization from another instance

!!! example

``` pycon
>>> structure_instance = Structure({"a":{"b": {"cde": 123}}})
```


## Interface

### Readonly properties

#### .data

> a [deep copy] of the [Nested Collection] the instance was initialized with.

!!! note "more precisely: deep copy of a deep copy"

    In fact, a deep copy of the original data structure is stored internally
    at initialization time, and this attribute is a readonly property
    returning a deep copy of the internally stored data structure,
    so in technically correct terms, this is a _deep copy of a deep copy_
    of the intialization argument.


#### .is_mutable

> a boolean value, always `False`.


#### .parsing_cache

> a [cache.ParsingCache] instance initialized with the **separator** argument.

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
>     value = structure_instance[pathspec]
>
> returns a [deep copy] of the value located at **pathspec** in the structure.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> structure_instance["a.b.cde"] == structure_instance["a", "b", "cde"] == 123
True
```


#### instance1 == instance2, instance1 != instance2

> **Comparison for (in)equality (via \_\_eq\_\_)**
>
> _added in version 0.4.0_
>
>     structure_instance_1 == structure_instance_2
>     structure_instance_1 != structure_instance_2
>
> returns `True` or `False` according to equality or inequality
> of all of both instances’ [.data], [.is_mutable], and [.parsing_cache].separator
> properties.

!!! example

``` pycon
>>> structure_instance == Structure({'a': {'b': {'cde': 123}}}, separator='.')
True
>>> structure_instance == Structure({'a': {'XYZ': {'cde': 123}}}, separator='.')
False
>>> structure_instance == Structure({'a': {'b': {'cde': 123}}}, separator='/')
False
>>> structure_instance != Structure({'a': {'b': {'cde': 123}}}, separator='/')
True
```


#### repr(instance)

> **String representation (via \_\_repr\_\_)**
>
> _added in version 0.3.1_
>
>     repr(structure_instance)

!!! example

    The statement printed here could be used to create a new Structure instance
    that compares equal

``` pycon
>>> print(repr(structure_instance))
Structure({'a': {'b': {'cde': 123}}}, separator='.')
```


### Methods

#### .get()

!!! failure inline end "No traversal through leaves"

    Raises a **TypeError** if _pathspec_ would require walking
    through a leaf (ie. a [scalar value] somewhere in the data structure).

>     value = structure_instance.get(pathspec)
>
> returns a [deep copy] of the value located at **pathspec** in the structure.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].

!!! example

``` pycon
>>> structure_instance.get("a.b.cde") == structure_instance.get(("a", "b", "cde")) == 123
True
```


#### .get_with_default()

> _added in version 0.4.1_
>
>     value = structure_instance.get_with_default(pathspec, default)
>
> returns a [deep copy] of the value located at **pathspec** in the structure,
> or **default** if `structure_instance.get(pathspec)` would raise a
> **KeyError** or **IndexError**.

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].
**default** must be suitable as a return value (ie. [ValueType]).

!!! example

``` pycon
>>> structure_instance.get("a.x.y")
(…)
KeyError: 'x'
>>> structure_instance.get_with_default("a.x.y", "fallback value")
'fallback value'
```


#### .iter_canonical_endpoints()

> _added in version 0.4.0_
>
>     for path in structure_instance.iter_canonical_endpoints():
>         print(path)
>
> returns an Iterator over canonical path representations for all endpoints
> (ie. items in the datastructure that are either a [scalar value]
> or an empty [collection].

!!! example

``` pycon
>>> for path in structure_instance.iter_canonical_endpoints():
...     print(path)
...
a.b.cde
```


* * *
[Nested Collection]: 5-glossary.md#nested-collection
[deep copy]: https://docs.python.org/3/library/copy.html#copy.deepcopy
[cache.ParsingCache]: 3-cache.md#parsingcache
[IndexType]: 5-glossary.md#indextype
[SegmentsTuple]: 5-glossary.md#segmentstuple
[ValueType]: 5-glossary.md#valuetype
[.data]: #data
[.is_mutable]: #is_mutable
[.parsing_cache]: #parsing_cache
[.get()]: #get
[scalar value]: 5-glossary.md#scalartype
[collection]: 5-glossary.md#collectiontype
