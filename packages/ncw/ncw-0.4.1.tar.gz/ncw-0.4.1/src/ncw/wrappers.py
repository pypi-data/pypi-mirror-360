# -*- coding: utf-8 -*-
# mypy: disable-error-code="index"

"""
Datastructure wrappers
"""

import copy

from typing import Iterator, TypeAlias, Union

from . import commons
from . import cache


_SINGLETON_CACHES: dict[str, cache.ParsingCache] = {
    commons.DOT: cache.ParsingCache(separator=commons.DOT),
}

StructureDataType: TypeAlias = Union[commons.ValueType, "Structure"]


def enforce_dict_or_list(
    candidate: commons.ValueType,
    error_message="End point seems to be a leaf instead of a CollectionType instance",
) -> dict | list:
    """Helper fuction making sure the camdidate is a dict or list"""
    if isinstance(candidate, (dict, list)):
        return candidate
    #
    raise TypeError(error_message)


class Structure:
    """A data structure, immutable by default, ..."""

    def __init__(
        self,
        original_data_structure: StructureDataType,
        separator: str = commons.DOT,
    ) -> None:
        """Always store a deep copy of data"""
        if isinstance(original_data_structure, Structure):
            self.__data = copy.deepcopy(original_data_structure.data)
        else:
            self.__data = copy.deepcopy(original_data_structure)
        #
        try:
            self.__cache: cache.ParsingCache = _SINGLETON_CACHES[separator]
        except KeyError:
            self.__cache = _SINGLETON_CACHES.setdefault(
                separator, cache.ParsingCache(separator=separator)
            )
        #

    @property
    def data(self) -> commons.ValueType:
        """access to data"""
        return self.get(())

    @property
    def is_mutable(self) -> bool:
        """Return True only from on mutable subclasses"""
        return False

    @property
    def parsing_cache(self) -> cache.ParsingCache:
        """access to the internal cache"""
        return self.__cache

    def __getitem__(self, full_path: commons.IndexType) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        return self.get(full_path)

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}({self.data!r},"
            f" separator={self.parsing_cache.separator!r})"
        )

    def __eq__(self, other) -> bool:
        """Equality test"""
        return all(
            (
                self.data == other.data,
                self.is_mutable == other.is_mutable,
                self.parsing_cache.separator == other.parsing_cache.separator,
            )
        )

    def __get_substructure(self, segments: commons.SegmentsTuple) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        if segments:
            substructure = commons.full_traverse(self.__data, segments)
        else:
            substructure = self.__data
        #
        if self.is_mutable:
            return substructure
        #
        return copy.deepcopy(substructure)

    def get(self, full_path: commons.IndexType) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        return self.__get_substructure(self.__cache[full_path])

    def get_with_default(
        self, full_path: commons.IndexType, default: commons.ValueType
    ) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        try:
            return self.__get_substructure(self.__cache[full_path])
        except (KeyError, IndexError):
            return default
        #

    def iter_canonical_endpoints(self) -> Iterator[str]:
        """Iterate over the canonical endpoints of the data structure"""
        for segments in commons.iter_paths(self.data):
            yield self.parsing_cache.canonical(segments)
        #


class MutableStructure(Structure):
    """A mutable data structure, immutable by default, ..."""

    def __init__(
        self,
        original_data_structure: StructureDataType,
        separator: str = commons.DOT,
    ) -> None:
        """Store the data as-is"""
        super().__init__(original_data_structure, separator=separator)
        self.__mutable = True

    @property
    def is_mutable(self) -> bool:
        """Return True on mutable instances"""
        return self.__mutable

    def freeze(self) -> list[str]:
        """Make the instance immutable and return a list of strings
        describing the effects for debugging purposes
        """
        class_name = self.__class__.__name__
        if self.is_mutable:
            self.__mutable = False
            return [
                f"{class_name} instance changed to immutable",
                "the .get() method will from now on"
                " return a deep copy of the found substructure",
            ]
        #
        return [f"No change, {class_name} instance had already been immutable"]

    def __setitem__(self, full_path: str, new_value: commons.ValueType) -> None:
        """Store a new value. Build the intermediate structure if required."""
        self.update(full_path, new_value, fail_on_missing_keys=False)

    def __delitem__(self, full_path: str) -> None:
        """Delete the specified substructure"""
        self.delete(full_path)

    def __collection_and_key(
        self,
        full_path: commons.IndexType,
    ) -> tuple[commons.ValueType, commons.ValueType]:
        """Return the collection at the last but one path segment,
        and the key determined by the last segment
        """
        segments = self.parsing_cache[full_path]
        if len(segments) < 1:
            raise IndexError(
                f"Minimum one path component is required, but got only {segments!r}"
            )
        #
        partial_traversal_path = segments[:-1]
        return enforce_dict_or_list(
            commons.full_traverse(self.data, partial_traversal_path)
        ), segments[-1]

    def delete(self, full_path: commons.IndexType) -> None:
        """Delete the substructure at full_path"""
        subcollection, key = self.__collection_and_key(full_path)
        del enforce_dict_or_list(subcollection)[key]  # type: ignore[arg-type]

    def update(
        self,
        full_path: commons.IndexType,
        new_value: commons.ValueType,
        fail_on_missing_keys: bool = False,
    ) -> None:
        """Modify the data structure in place setting self[full_path] to new_value"""
        if fail_on_missing_keys:
            # shortcut: regard the full path only
            subcollection, key = self.__collection_and_key(full_path)
        else:
            # slow traversal - search the existing path part,
            # and build a new substructure
            # so in the resulting structure there will be the full path available
            segments = self.parsing_cache[full_path]
            if not segments:
                raise ValueError("Cannot modify with an empty path")
            #
            subcollection, remaining_segments = commons.partial_traverse(
                self.data,
                segments,
                min_remaining_segments=1,
                fail_on_missing_keys=False,
            )
            if len(remaining_segments) > 1:
                # build intermediate path
                still_remaining_segments = list(remaining_segments)
                while len(still_remaining_segments) > 1:
                    key = still_remaining_segments.pop(0)
                    subcollection[key] = {}
                    subcollection = subcollection[key]
                #
                key = still_remaining_segments.pop(0)
            else:
                key = remaining_segments[0]
            #
        #
        enforce_dict_or_list(subcollection)[key] = new_value  # type: ignore[index]


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
