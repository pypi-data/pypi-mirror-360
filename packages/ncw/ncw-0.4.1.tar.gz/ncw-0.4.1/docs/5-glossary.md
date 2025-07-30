# Glossary of terms

## Nested Collection

> A data structure as returned e.g. from the standard library’s
> [json.load()] or [json.loads()] functions.

Usually a [CollectionType] (ie. **dict** or **list**) instance containing other
[CollectionType] and/or [ScalarType] instances.

In the context of this package, nested collections are used as data sources for
a [Structure] or [MutableStructure] instance.

Theoretically, also a [ScalarType] instance could be used as a nested collection
and wrapped in a [Structure] or [MutableStructure] instance,
but that does not make much sense.


## Structure

> A wrapper around a [Nested Collection] providing **readonly access**.
>
> Class defined in the **wrappers** module and additionally exposed at package level

At initialization time, a [deep copy] of the provided data structure
is stored in a [private attribute],
thus guaranteeing that the original data structure is never modified
by the Structure instance or its subclasses.

The **.data** property always returns a [deep copy] of
the data structure stored in this private attribute.

The **.get()** method or item access (through `structure_instance[index]`)
always return [deep copies][deep copy] of the substructures determined by the provided index
(of type [IndexType]).


## MutableStructure

> Subclass of [Structure]:
> a wrapper around a [Nested Collection] providing **read and write access**.
>
> Class defined in the **wrappers** module and additionally exposed at package level

In contrast to the parent class:

*   the **.data** property always returns the internally stored data structure itself.
*   the **.get()** method and item access
    (`mutable_structure_instance[index]`) return the addressed substructure itself.

Additionally, **.delete()** and **.update()** methods are provided as well as

    del mutable_structure_instance[index]

and

    mutable_structure_instance[index] = …

capabilities, all of them changing the internally stored data structure _in place_.


## Type Aliases

> All of these Type Aliases are defined in the **commons** module.


### CollectionType

> A **dict** or **list** instance.


### ScalarType

> An immutable value, either `None` or a **str**, **float**, **int**, or **bool**
> instance. Sutable as keys for **dict** instances in [nested collections][Nested Collection].


### ValueType

> A [CollectionType] or [ScalarType] instance, suitable as a value for **dict**
> or **list** instances in [nested collections][Nested Collection].


### SegmentsTuple

> A **tuple** of [ScalarType] instances
> (used by the **commons.partial_traverse()** and **commons.full_traverse()** functions)


### IndexType

> A [SegmentsTuple] or a **str** instance.

May be used as a traversal path in [Structure] or [MutableStructure] instances,
ie. for adressing any [ValueType] contained in the underlying [nested collection][Nested Collection].


* * *
[Nested Collection]: #nested-collection
[private attribute]: https://docs.python.org/3/tutorial/classes.html#tut-private
[deep copy]: https://docs.python.org/3/library/copy.html#copy.deepcopy
[json.load()]: https://docs.python.org/3/library/json.html#json.load
[json.loads()]: https://docs.python.org/3/library/json.html#json.loads
[Structure]: #structure
[MutableStructure]: #mutablestructure
[CollectionType]: #collectiontype
[ScalarType]: #scalartype
[ValueType]: #valuetype
[SegmentsTuple]: #segmentstuple
[IndexType]: #indextype
