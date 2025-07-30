# The cache module

> This module provides the SegmentsParser ans ParsingCache classes
> that are normally only used internally by the [Structure class]
> and its subclasses.

``` python
from ncw import cache
```


## ParsingCache

> **A threadsafe cache mapping [SegmentsTuple] instances to strings,**
> **invoking and using new [SegmentsParser] instances on demand.**
>
>     parsing_cache_instance = cache.ParsingCache(separator=separator_char)
>
> initializes an instance with **separator_char** as the separator
> (default: ASCII dot `.`).
> Only single unicode characters are allowed here – if you try
> to initialize an instance with a longer string, a TypeError will be raised.


### Readonly property

#### .separator

> the separator character (**str** of length 1)


### Instance attribute

#### .stats

> a [collections.Counter] instance counting cache hits, misses and bypasses.


### Capabilities through special methods

#### instance\[pathspec\]

!!! abstract inline end "Implementation detail"

    Item read access with the is implemented by calling the [.get_cached()] method internally.

> **Item read access (via \_\_getitem\_\_)**
>
>     segments = parsing_cache_instance[pathspec]
>
> returns a (maybe newly parsed, maybe also cached) [SegmentsTuple] for **pathspec**

**pathspec** may be a string containing the path segments joined by
the separator character, or a [SegmentsTuple].
If a [SegmentsTuple] is provided, ist is just returned as-si, bypassing the cache.

!!! example

``` pycon
>>> parsing_cache_instance.stats
Counter()
>>> parsing_cache_instance["x.yy.zzzz"]
('x', 'yy', 'zzzz')
>>> parsing_cache_instance.stats
Counter({'miss': 1})
>>> parsing_cache_instance["x.yy.zzzz"]
('x', 'yy', 'zzzz')
>>> parsing_cache_instance.stats
Counter({'miss': 1, 'hit': 1})
>>> parsing_cache_instance["x", "yy", "zzzz"]
('x', 'yy', 'zzzz')
>>> parsing_cache_instance.stats
Counter({'miss': 1, 'hit': 1, 'bypass': 1})
```


#### repr(instance)

> **String representation (via \_\_repr\_\_)**
>
>     repr(parsing_cache_instance)

!!! example

``` pycon
>>> pc_instance = cache.ParsingCache(separator="/")
>>> print(repr(pc_instance))
ParsingCache(separator='/')
```


### Methods

#### .get_cached()

>     segments = parsing_cache_instance.get_cached(path_source)
>
> Returns a [SegmentsTuple] for **path_source**, preferably from the internal cache.
>
> If nothing was found in the internal cache, a new [SegmentsParser] is used
> to parse a [SegmentsTuple] out of **path_source**, and the result is cached and returned.

**path_source** is a string containing the path segments joined by
the separator character.

This method uses a lock mechanism to read from and write to the internal cache
in a thread safe manner.

!!! example

``` pycon
>>> parsing_cache_instance.stats.clear()
>>> parsing_cache_instance.get_cached("aaa.bbb.ccc")
('aaa', 'bbb', 'ccc')
>>> parsing_cache_instance.stats
Counter({'miss': 1})
>>> parsing_cache_instance.get_cached("aaa.bbb.ccc")
('aaa', 'bbb', 'ccc')
>>> parsing_cache_instance.stats
Counter({'miss': 1, 'hit': 1})
```


#### .canonical()

>     path_source = parsing_cache_instance.canonical(segments)
>
> Returns a path source string (ie. segments joined togehter by the separator character)
> from a [SegmentsTuple] and adds that relation to the internal cache
> if not present yet.


## SegmentsParser

> **Non-threadsafe parser generating a [SegmentsTuple] from a string**
>
>     parser = cache.SegmentsParser(separator=separator_char)
>
> initializes an instance with **separator_char** as the separator
> (default: ASCII dot `.`).
> Only single unicode characters are allowed here – if you try
> to initialize an instance with a longer string, a TypeError will be raised.


### Readonly property

#### .separator

> the separator character (**str** of length 1)


### Methods

#### .split_into_segments()

>     segments = parsing_cache_instance.split_into_segments(path_source)
>
> Parses **path_source** into a [SegmentsTuple].


* * *
[Structure class]: 1-structure.md
[Nested Collection]: 5-glossary.md#nested-collection
[IndexType]: 5-glossary.md#indextype
[ScalarType]: 5-glossary.md#scalartype
[SegmentsTuple]: 5-glossary.md#segmentstuple
[SegmentsParser]: #segmentsparser
[.get_cached()]: #get_cached
[collections.Counter]: https://docs.python.org/3/library/collections.html#collections.Counter
