"""
pureset.py
==========

A robust, immutable, homogeneous, and ordered collection type for Python, blending the best features of sets, tuples, and sequences.

Overview
--------
PureSet is a collection class designed to provide intuitive, error-resistant handling of unique elements of the same type or "shape".
It guarantees immutability after construction, preserves insertion order, and enforces homogeneity and uniqueness of its elements.

Features
--------
- **Immutability:** Once instantiated, elements cannot be altered, added, or removed.
- **Homogeneity:** All elements must be of the same type or recursively matching structure/signature.
- **Uniqueness:** Duplicate elements are automatically removed while preserving order.
- **Order Preservation:** Elements remember the order of initial insertion.
- **Hashable-aware:** Supports hash-based operations when appropriate, with graceful fallback for unhashable content.
- **Rich API:** Fully featured, including pickling, copying, comparison, concatenation, set-like operations (union, intersection, etc.), mapping/filtering, robust indexing, and deep introspection of element types.

Typical Use Cases
-----------------
- Symbolic or configuration sets whose membership and order must never change.
- Mathematical or dataset domains where the type and identity of each element are strictly controlled.
- Hashable, deterministic sets for functional programming, caching, and reproducible computing.

Examples
--------
>>> PureSet(1, 2, 3)
PureSet(1, 2, 3)
>>> PureSet([1, 2], [3, 4])
PureSet([1, 2], [3, 4])
>>> PureSet()
PureSet()
>>> PureSet(1, 2, 2, 3)
PureSet(1, 2, 3)
>>> PureSet(1, 'a')
Traceback (most recent call last):
    ...
TypeError: Incompatible element type or shape at position 2:
Exp: <class 'int'>;
Got: <class 'str'>

Author & License
----------------
Gabriel Maia (@gabrielmsilva00)  
Electric Engineering Undergraduate, UERJ  
Apache License 2.0

Links
-----
Repository: https://github.com/gabrielmsilva00/pureset  
Contact:    gabrielmaia.silva00@gmail.com
"""

from __future__ import annotations
from copy import deepcopy
from functools import total_ordering
from collections import UserList, UserDict, UserString, deque, ChainMap, Counter, OrderedDict, defaultdict
from collections.abc import Sequence, Mapping, Set
from numbers import Number
from enum import Enum
from array import array
from typing import Any, TypeVar, Union, Optional, Callable, Hashable, Iterator, overload
from types import MappingProxyType

__title__   = "pureset"
__desc__    = "An immutable, homogeneous, and ordered collection type for Python."
__version__ = "1.1.250706.0"
__author__  = "gabrielmsilva00"
__contact__ = "gabrielmaia.silva00@gmail.com"
__repo__    = "github.com/gabrielmsilva00/pureset"
__license__ = "Apache License 2.0"
__all__     = ["PureSet"]

T = TypeVar("T")


@total_ordering
class PureSet(Sequence[T]):
    """
    An immutable, homogeneous, and ordered collection type for unique elements.

    PureSet is a powerful sequence/set hybrid designed to combine the mathematical concept of a set
    (uniqueness, unordered) with tuple-like immutability and sequence-like ordered access. Element
    type uniformity is strictly enforced, and complex nested data-structures are verified by recursive
    structural signature checks.

    Key Features
    ------------
    - **Immutability:** The collection is fixed after construction; mutation operations (assignment/deletion)
      are prevented at the instance level.
    - **Homogeneity:** All elements share the same type, or, for compound types, identical nested structure.
      A detailed 'signature' property exposes the uniformity constraints.
    - **Unique Elements:** Duplicate entries (by value) are automatically eliminated (the first occurrence persists).
    - **Order Preservation:** Elements maintain their insertion order, unlike mathematical sets.
    - **Hashability Awareness:** Handles both hashable and unhashable element types gracefully,
      affecting internal optimization and conversion to frozenset.
    - **Collection API:** Supports rich Pythonic behavior: indexing, slicing, iteration, comparison,
      ordering, concatenation, set-style union/intersection/difference/xor, mapping, filtering, and utilities.
    - **Signature Inspection:** Offers deep introspection of type/structure via `signature`, usable in dynamic code.
    - **Whole-object Hashing:** Hashes are stable and based on tuple-element order and type.

    Examples
    --------
    >>> PureSet(1, 2, 3)
    PureSet(1, 2, 3)
    >>> PureSet([1, 2], [3, 4])
    PureSet([1, 2], [3, 4])
    >>> PureSet(1, 1, 2, 2, 3, 3)
    PureSet(1, 2, 3)
    >>> PureSet()
    PureSet()
    >>> PureSet(1, "a")
    Traceback (most recent call last):
        ...
    TypeError: Incompatible element type or shape at position 2:
    Exp: <class 'int'>;
    Got: <class 'str'>

    Attributes
    ----------
    items : tuple
        The internal immutable tuple containing all unique elements.
    set : frozenset or None
        A frozenset view of the elements (for hashable types only).
    hashable : bool
        Whether the PureSet’s elements are hashable.
    signature : object
        The type/structural signature shared by all elements.

    Notes
    -----
    PureSet can be used wherever an immutable, unique, homogeneous, and order-preserving collection is needed.
    It is especially useful for deterministic indexable sets, functional programming, mathematical constructs,
    hashable containers, and as a safer (type-checked) alternative to tuples, sets, and lists for certain domains.

    For more details, see individual method docstrings.
    """
    __slots__ = (
        "_items",
        "_signature",
        "_restored_cache",
        "_items_set",
        "__weakref__",
    )
    def __init__(self, *args: T) -> None:
        if not args:
            self._items = ()
            self._signature = None
            self._restored_cache = None
            return

        PRIMITIVE = (int, float, bool, str, bytes, frozenset, type)
        T0 = type(args[0])

        if all(isinstance(x, T0) for x in args) and T0 in PRIMITIVE:
            self._signature = T0
            self._items = tuple(dict.fromkeys(args))
            self._restored_cache = None
            return

        self._signature = PureSet.get_signature(args[0])
        for i, item in enumerate(args):
            sig = PureSet.get_signature(item)
            if sig != self._signature:
                raise TypeError(
                    f"Incompatible element type or shape at position {i + 1}:\nExp: {self._signature};\nGot: {sig}"
                )

        frozen_args = tuple(PureSet.freeze(item) for item in args)

        try: hashable = all(hash(x) is not None for x in frozen_args)
        except Exception: hashable = False

        if hashable:
            self._items = tuple(dict.fromkeys(frozen_args))
            self._restored_cache = None

        else:
            seen = []
            unique_items = []
            for item in frozen_args:
                if item not in seen:
                    seen.append(item)
                    unique_items.append(item)
            self._items = tuple(unique_items)
            self._restored_cache = None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__slots__: object.__setattr__(self, name, value)
        else: raise AttributeError(f"{self.__class__.__name__} is immutable")

    @property
    def items(self) -> tuple[T, ...]: return self._items

    @property
    def signature(self) -> Any:
        """General, standardized signature for the PureSet's elements.
        Examples
        --------
        >>> PureSet(1, 2, 3).signature
        <class 'int'>
        >>> PureSet({"x": 1, "y": 2}, {"x": 0, "y": 5}).signature
        (<class 'dict'>, {'x': <class 'int'>, 'y': <class 'int'>})
        >>> class C: pass
        >>> PureSet(C(), C()).signature
        Traceback (most recent call last):
            ...
        TypeError: Cannot safely freeze object of type <class '__main__.C'> for PureSet.
        """
        return self._signature

    @property
    def restored(self):
        """
        Returns a tuple of each element deeply restored to its original class/shape,
        reconstructing the original user-facing objects (deepcopy-like).
        """
        if not hasattr(self, "_restored_cache") or self._restored_cache is None:
            self._restored_cache = tuple(PureSet.restore(o) for o in self._items)
        return self._restored_cache

    def __reduce__(self) -> tuple:
        """Support for pickling/unpickling.

        Returns
        -------
        tuple
            Tuple containing class and arguments for reconstruction

        Examples
        --------
        >>> import pickle
        >>> ps = PureSet(1, 2, 3)
        >>> ps2 = pickle.loads(pickle.dumps(ps))
        >>> ps == ps2
        True
        >>> empty = PureSet()
        >>> empty2 = pickle.loads(pickle.dumps(empty))
        >>> empty == empty2
        True
        """
        if self.restored: return (self.__class__, self.restored)
        else: return (self.__class__, ())

    def __copy__(self) -> PureSet[T]:
        """Create a shallow copy of the PureSet.

        Returns
        -------
        PureSet[T]
            A new PureSet with the same elements

        Examples
        --------
        >>> from copy import copy
        >>> ps = PureSet(1, 2, 3)
        >>> ps_copy = copy(ps)
        >>> ps == ps_copy
        True
        >>> ps is ps_copy
        False
        """
        if self.restored: return self.__class__(*self.restored)
        else: return self.__class__()

    def __deepcopy__(self, memo: dict[int, Any]) -> PureSet[T]:
        """Create a deep copy of the PureSet.

        Parameters
        ----------
        memo : dict[int, Any]
            Memoization dictionary for circular reference handling

        Returns
        -------
        PureSet[T]
            A new PureSet with deeply copied elements

        Examples
        --------
        >>> from copy import deepcopy
        >>> ps = PureSet([1, 2], [3, 4])
        >>> ps_deep = deepcopy(ps)
        >>> ps == ps_deep
        True
        >>> ps[0] is ps_deep[0]
        False
        """
        if self.restored: return self.__class__(*tuple(deepcopy(item, memo) for item in self.restored))
        else: return self.__class__()

    def __len__(self) -> int:
        """Return the number of elements in the PureSet.

        Returns
        -------
        int
            Number of unique elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3, 2, 1)
        >>> len(ps)
        3
        >>> len(PureSet())
        0
        """
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the elements.

        Returns
        -------
        Iterator[T]
            Iterator yielding elements in order

        Examples
        --------
        >>> ps = PureSet(3, 1, 4, 1, 5)
        >>> list(ps)
        [3, 1, 4, 5]
        >>> for x in PureSet(1, 2, 3):
        ...     print(x)
        1
        2
        3
        """
        return iter(self.restored)

    def __hash__(self) -> int:
        """Return hash value for the PureSet.

        Returns
        -------
        int
            Hash value based on type and elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> isinstance(hash(ps), int)
        True
        >>> ps1 = PureSet(1, 2, 3)
        >>> ps2 = PureSet(1, 2, 3)
        >>> hash(ps1) == hash(ps2)
        True
        """
        return hash((type(self), self.items))

    def __repr__(self) -> str:
        """Return detailed string representation.

        Returns
        -------
        str
            Representation showing all elements

        Examples
        --------
        >>> PureSet(1, 2, 3)
        PureSet(1, 2, 3)
        >>> PureSet()
        PureSet()
        """
        if not self.restored: return f"{self.__class__.__name__}()"
        return f"{self.__class__.__name__}({', '.join(map(repr, self.restored))})"

    def __str__(self) -> str:
        """Return human-readable string representation.

        Returns
        -------
        str
            Formatted string, truncated for large sets

        Examples
        --------
        >>> print(PureSet(1, 2, 3))
        PureSet(1, 2, 3)
        >>> print(PureSet(*range(15)))
        PureSet(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, ... (5 more items))
        """
        if not self.restored: return f"{self.__class__.__name__}()"
        items_str = ", ".join(repr(item) for item in self.restored[:10])
        if len(self.restored) > 10: items_str += f", ... ({len(self.restored) - 10} more items)"
        return f"{self.__class__.__name__}({items_str})"

    def __contains__(self, item: object) -> bool:
        """Check if item is in the PureSet.

        Parameters
        ----------
        item : object
            The item to check for membership

        Returns
        -------
        bool
            True if item exists, False otherwise

        Examples
        --------
        >>> ps = PureSet(1, 2, 3, 4, 5)
        >>> 3 in ps
        True
        >>> 10 in ps
        False
        >>> ps = PureSet([1, 2], [3, 4])
        >>> [1, 2] in ps
        True
        """
        frozen = PureSet.freeze(item)
        try:
            if not hasattr(self, "_items_set"):
                self._items_set = set(self._items)
            return frozen in self._items_set
        except TypeError:
            return frozen in self._items

    def __getitem__(self, idx: Union[int, slice, T]) -> Union[T, 'PureSet[T]']:
        """
        Get element by index, slice, or value lookup.
        Restores the original object via deep-restore from the frozen form.
        """
        if isinstance(idx, int):
            return PureSet.restore(self._items[idx])

        elif isinstance(idx, slice):
            return self.__class__(*(PureSet.restore(x) for x in self._items[idx]))

        else:
            frozen = PureSet.freeze(idx)
            for item in self._items:
                if item == frozen:
                    return PureSet.restore(item)
            raise KeyError(f"Value {idx!r} not found in {self.__class__.__name__}")

    def __eq__(self, other: object) -> bool:
        """Check equality with another PureSet.

        Parameters
        ----------
        other : object
            Object to compare with

        Returns
        -------
        bool
            True if equal, False otherwise

        Examples
        --------
        >>> PureSet(1, 2, 3) == PureSet(1, 2, 3)
        True
        >>> PureSet(1, 2, 3) == PureSet(3, 2, 1)
        False
        >>> PureSet(1, 2) == [1, 2]
        False
        """
        return isinstance(other, PureSet) and self.items == other.items

    def __lt__(self, other: PureSet[T]) -> bool:
        """Check if this PureSet is less than another.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to compare with

        Returns
        -------
        bool
            True if lexicographically less than other

        Examples
        --------
        >>> PureSet(1, 2) < PureSet(1, 3)
        True
        >>> PureSet(1, 2, 3) < PureSet(1, 2)
        False
        """
        if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
        return self.restored < other.restored

    def __le__(self, other: PureSet[T]) -> bool:
        """Check if this PureSet is less than another.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to compare with

        Returns
        -------
        bool
            True if lexicographically less than or equal to other

        Examples
        --------
        >>> PureSet(1, 2) <= PureSet(1, 2)
        True
        >>> PureSet(20) <= PureSet(3, 6, 9)
        False
        """
        if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
        return self.restored <= other.restored

    def __gt__(self, other: PureSet[T]) -> bool:
        """Check if this PureSet is greater than another.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to compare with

        Returns
        -------
        bool
            True if lexicographically greater than other

        Examples
        --------
        >>> PureSet(1, 2) > PureSet(1, 3)
        False
        >>> PureSet(1, 2, 3) > PureSet(1, 2)
        True
        """
        if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
        return self.restored > other.restored

    def __ge__(self, other: PureSet[T]) -> bool:
        """Check if this PureSet is greater than or equal to another.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to compare with

        Returns
        -------
        bool
            True if lexicographically greater than or equal to other

        Examples
        --------
        >>> PureSet(15) >= PureSet(1, 2, 3, 4, 5)
        True
        >>> PureSet(-30) >= PureSet(-1, 0, 1)
        False
        """
        if not isinstance(other, PureSet): raise TypeError("Cannot compare PureSet with non-PureSet")
        return self.restored >= other.restored

    def __add__(self, other: PureSet[T]) -> PureSet[T]:
        """Concatenate two PureSets.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to concatenate with

        Returns
        -------
        PureSet[T]
            New PureSet with elements from both

        Raises
        ------
        TypeError
            If element types are incompatible

        Examples
        --------
        >>> PureSet(1, 2) + PureSet(3, 4)
        PureSet(1, 2, 3, 4)
        >>> PureSet(1, 2) + PureSet(2, 3)
        PureSet(1, 2, 3)
        >>> PureSet() + PureSet(1, 2)
        PureSet(1, 2)
        """
        if not isinstance(other, PureSet): raise TypeError("Cannot concatenate PureSet with non-PureSet")

        if self.signature and other.signature:
            if self.signature != other.signature:
                raise TypeError(
                    f"Cannot concatenate PureSets with different element types: "
                    f"Exp: {self.signature}\nGot: {other.signature}"
                )

        if not self.restored: return other
        if not other.restored: return self
        return self.__class__(*list(self.restored) + list(other.restored))

    def __mul__(self, n: int) -> PureSet[T]:
        """Repeat elements n times.

        Parameters
        ----------
        n : int
            Number of repetitions

        Returns
        -------
        PureSet[T]
            New PureSet with repeated elements

        Examples
        --------
        >>> PureSet(1, 2) * 3
        PureSet(1, 2)
        >>> PureSet(1, 2) * 0
        PureSet()
        >>> PureSet(1, 2) * -1
        PureSet()
        """
        if not isinstance(n, int): raise TypeError("Repetitions must be an integer")
        return self if n > 0 else self.__class__()

    def pos(self, index: int) -> T:
        """Return element at position index.

        Parameters
        ----------
        index : int
            Position index

        Returns
        -------
        T
            Element at the given position

        Raises
        ------
        IndexError
            If index is out of range

        Examples
        --------
        >>> ps = PureSet(10, 20, 30)
        >>> ps.pos(0)
        10
        >>> ps.pos(-1)
        30
        >>> ps.pos(10)
        Traceback (most recent call last):
            ...
        IndexError: Index 10 out of range for length 3
        """
        try: return self.restored[index]
        except IndexError: raise IndexError(f"Index {index} out of range for length {len(self)}")

    def index(self, value: T, start: int = 0, stop: Optional[int] = None) -> int:
        """Return index of first occurrence of value.

        Parameters
        ----------
        value : T
            Value to find
        start : int, optional
            Start position for search (default: 0)
        stop : Optional[int], optional
            End position for search (default: None)

        Returns
        -------
        int
            Index of the value

        Raises
        ------
        ValueError
            If value is not found

        Examples
        --------
        >>> ps = PureSet(10, 20, 30, 40)
        >>> ps.index(20)
        1
        >>> ps.index(30, 1)
        2
        >>> ps.index(10, 1, 3)
        Traceback (most recent call last):
            ...
        ValueError: 10 not in range [1:3]
        """
        if value not in self: raise ValueError(f"{value!r} is not in {self.__class__.__name__}")

        try:
            if stop is None: return self.restored.index(value, start)
            else: return self.restored.index(value, start, stop)

        except ValueError: raise ValueError(f"{value!r} not in range [{start}:{stop}]")

    def count(self, value: T) -> int:
        """Return 1 if value exists, 0 otherwise.

        Parameters
        ----------
        value : T
            Value to count

        Returns
        -------
        int
            1 if present, 0 if not

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.count(2)
        1
        >>> ps.count(5)
        0
        """
        return 1 if value in self else 0

    def join(self, sep: str) -> str:
        """Return string representation joined by sep.

        Parameters
        ----------
        sep : str
            Separator between elements

        Returns
        -------
        str
            String representation

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.join(",")
        '1,2,3'
        """
        return sep.join(map(str, self.restored))

    def reverse(self) -> PureSet[T]:
        """Return new PureSet with reversed order.

        Returns
        -------
        PureSet[T]
            New PureSet with elements in reverse order

        Examples
        --------
        >>> ps = PureSet(1, 2, 3, 4)
        >>> ps.reverse()
        PureSet(4, 3, 2, 1)
        >>> PureSet().reverse()
        PureSet()
        """
        return self.__class__(*reversed(self.restored))

    def to_list(self) -> list[T]:
        """Convert to list.

        Returns
        -------
        list[T]
            List containing all elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.to_list()
        [1, 2, 3]
        >>> type(ps.to_list())
        <class 'list'>
        """
        return list(self.restored)

    def to_tuple(self) -> tuple[T, ...]:
        """Return internal tuple.

        Returns
        -------
        tuple[T, ...]
            Tuple containing all elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.to_tuple()
        (1, 2, 3)
        >>> type(ps.to_tuple())
        <class 'tuple'>
        """
        return self.restored

    def to_frozenset(self) -> frozenset[T]:
        """Return frozenset of elements.

        Returns
        -------
        frozenset[T]
            Frozenset containing all elements

        Raises
        ------
        TypeError
            If elements are not hashable

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.to_frozenset()
        frozenset({1, 2, 3})
        >>> ps = PureSet([1, 2], [3, 4])
        >>> ps.to_frozenset()
        Traceback (most recent call last):
            ...
        TypeError: Elements are not hashable
        """
        try: return frozenset(self.restored)
        except TypeError: raise TypeError("Elements are not hashable")

    def compatible(self, other: PureSet[T]) -> PureSet[T]:
        """Validate compatibility with another PureSet.

        Parameters
        ----------
        other : PureSet[T]
            PureSet to check compatibility with

        Returns
        -------
        PureSet[T]
            The same PureSet if compatible

        Raises
        ------
        TypeError
            If not a PureSet or incompatible types

        Examples
        --------
        >>> ps1 = PureSet(1, 2, 3)
        >>> ps2 = PureSet(4, 5, 6)
        >>> ps1.compatible(ps2) == ps2
        True
        >>> ps_str = PureSet("a", "b")
        >>> ps1.compatible(ps_str)
        Traceback (most recent call last):
            ...
        TypeError: Incompatible element types:
        Exp: <class 'int'>
        Got: <class 'str'>
        """
        if not isinstance(other, PureSet): raise TypeError(f"Expected PureSet, got '{type(other)}'")

        if self.restored and other.restored:
            if self.signature != other.signature:
                raise TypeError(
                    f"Incompatible element types:\nExp: {self.signature}"
                    f"\nGot: {other.signature}"
                )

        return other

    def __or__(self, other: PureSet[T]) -> PureSet[T]:
        """Union operation (self | other).

        Parameters
        ----------
        other : PureSet[T]
            PureSet to union with

        Returns
        -------
        PureSet[T]
            New PureSet containing elements from both

        Examples
        --------
        >>> PureSet(1, 2, 3) | PureSet(3, 4, 5)
        PureSet(1, 2, 3, 4, 5)
        >>> PureSet() | PureSet(1, 2)
        PureSet(1, 2)
        >>> PureSet([1, 2], [3, 4]) | PureSet([3, 4], [5, 6])
        PureSet([1, 2], [3, 4], [5, 6])
        """
        other = self.compatible(other)
        if not other.restored: return self
        if not self.restored: return other

        result = list(self.restored)

        for item in other.restored:
            if item not in self:
                result.append(item)

        return self.__class__(*result)

    def __and__(self, other: PureSet[T]) -> PureSet[T]:
        """Intersection operation (self & other).

        Parameters
        ----------
        other : PureSet[T]
            PureSet to intersect with

        Returns
        -------
        PureSet[T]
            New PureSet with common elements

        Examples
        --------
        >>> PureSet(1, 2, 3, 4) & PureSet(3, 4, 5, 6)
        PureSet(3, 4)
        >>> PureSet(1, 2) & PureSet(3, 4)
        PureSet()
        >>> PureSet([1, 2], [3, 4]) & PureSet([3, 4], [5, 6])
        PureSet([3, 4])
        """
        other = self.compatible(other)

        try:
            set_other = set(other._items)
            return self.__class__(*(PureSet.restore(x) for x in self._items if x in set_other))

        except TypeError:
            return self.__class__(*(x for x in self.restored if x in other))

    def __sub__(self, other: PureSet[T]) -> PureSet[T]:
        """Difference operation (self - other).

        Parameters
        ----------
        other : PureSet[T]
            PureSet to subtract

        Returns
        -------
        PureSet[T]
            New PureSet with elements in self but not in other

        Examples
        --------
        >>> PureSet(1, 2, 3, 4) - PureSet(3, 4, 5)
        PureSet(1, 2)
        >>> PureSet(1, 2) - PureSet(1, 2, 3)
        PureSet()
        >>> PureSet([1, 2], [3, 4]) - PureSet([3, 4])
        PureSet([1, 2])
        """
        other = self.compatible(other)

        try:
            set_other = set(other._items)
            return self.__class__(*(PureSet.restore(x) for x in self._items if x not in set_other))

        except TypeError:
            return self.__class__(*(x for x in self.restored if x not in other))

    def __xor__(self, other: PureSet[T]) -> PureSet[T]:
        """Symmetric difference operation (self ^ other).

        Parameters
        ----------
        other : PureSet[T]
            PureSet for symmetric difference

        Returns
        -------
        PureSet[T]
            New PureSet with elements in either but not both

        Examples
        --------
        >>> PureSet(1, 2, 3) ^ PureSet(3, 4, 5)
        PureSet(1, 2, 4, 5)
        >>> PureSet(1, 2) ^ PureSet(3, 4)
        PureSet(1, 2, 3, 4)
        >>> PureSet(1, 2) ^ PureSet(1, 2)
        PureSet()
        """
        other = self.compatible(other)

        result = [x for x in self.restored if x not in other]
        result.extend(x for x in other.restored if x not in self)
        return self.__class__(*result)

    def filter(self, predicate: Callable[[T], bool]) -> PureSet[T]:
        """Return new PureSet with elements that satisfy predicate.

        Parameters
        ----------
        predicate : Callable[[T], bool]
            Function to test each element

        Returns
        -------
        PureSet[T]
            New PureSet with filtered elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3, 4, 5)
        >>> ps.filter(lambda x: x % 2 == 0)
        PureSet(2, 4)
        >>> ps.filter(lambda x: x > 3)
        PureSet(4, 5)
        >>> ps.filter(lambda x: x > 10)
        PureSet()
        """
        return self.__class__(*filter(predicate, self.restored))

    def map(self, function: Callable[[T], Any]) -> PureSet[Any]:
        """Apply function to all elements and return new PureSet.

        Note: The resulting elements must all be of the same type.

        Parameters
        ----------
        function : Callable[[T], Any]
            Function to apply to each element

        Returns
        -------
        PureSet[Any]
            New PureSet with mapped elements

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.map(lambda x: x * 2)
        PureSet(2, 4, 6)
        >>> ps.map(str)
        PureSet('1', '2', '3')
        >>> PureSet("a", "b", "c").map(str.upper)
        PureSet('A', 'B', 'C')
        """
        return self.__class__(*map(function, self.restored))

    def first(self, default: Optional[T] = None) -> Optional[T]:
        """Return first element or default if empty.

        Parameters
        ----------
        default : Optional[T], optional
            Value to return if empty (default: None)

        Returns
        -------
        Optional[T]
            First element or default value

        Examples
        --------
        >>> ps = PureSet(10, 20, 30)
        >>> ps.first()
        10
        >>> PureSet().first()

        >>> PureSet().first("empty")
        'empty'
        """
        return self.restored[0] if self.restored else default

    def last(self, default: Optional[T] = None) -> Optional[T]:
        """Return last element or default if empty.

        Parameters
        ----------
        default : Optional[T], optional
            Value to return if empty (default: None)

        Returns
        -------
        Optional[T]
            Last element or default value

        Examples
        --------
        >>> ps = PureSet(10, 20, 30)
        >>> ps.last()
        30
        >>> PureSet().last()

        >>> PureSet().last("empty")
        'empty'
        """
        return self.restored[-1] if self.restored else default

    def sorted(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> PureSet[T]:
        """Return new PureSet with sorted elements.

        Parameters
        ----------
        key : Optional[Callable[[T], Any]], optional
            Function to extract comparison key (default: None)
        reverse : bool, optional
            Sort in descending order if True (default: False)

        Returns
        -------
        PureSet[T]
            New PureSet with sorted elements

        Examples
        --------
        >>> ps = PureSet(3, 1, 4, 1, 5, 9)
        >>> ps.sorted()
        PureSet(1, 3, 4, 5, 9)
        >>> ps.sorted(reverse=True)
        PureSet(9, 5, 4, 3, 1)
        >>> PureSet("banana", "pie", "a").sorted(key=len)
        PureSet('a', 'pie', 'banana')
        """
        return self.__class__(*sorted(self.restored, key=key, reverse=reverse))

    def unique(self) -> PureSet[T]:
        """Return self (elements are always unique in PureSet).

        Returns
        -------
        PureSet[T]
            Returns self unchanged

        Examples
        --------
        >>> ps = PureSet(1, 2, 3)
        >>> ps.unique() is ps
        True
        >>> PureSet(1, 1, 2, 2, 3, 3).unique()
        PureSet(1, 2, 3)
        """
        return self

    def get(self, item: T, default: Optional[T] = None) -> T:
        """Return item or default if not found.

        Parameters
        ----------
        item : T
            Item to search for
        default : Optional[T], optional
            Value to return if item is not found (default: None)

        Returns
        -------
        T
            Item or default value

        Examples
        --------
        >>> ps = PureSet(10, 20, 30)
        >>> ps.get(20)
        20
        >>> ps.get(40, "not found")
        'not found'
        """
        return item if item in self.restored else default

    @staticmethod
    def get_signature(obj: object) -> Union[type, tuple]:
        """Get the signature of a given object.

        Parameters
        ----------
        obj : object
            Object to get the signature of

        Returns
        -------
        Union[type, tuple]
            The signature of the object

        Notes
        -----
        The signature is a tuple of the object type and the signatures of its
        properties or elements if it is a container.

        Examples
        --------
        >>> PureSet.get_signature(1)
        <class 'int'>
        >>> PureSet.get_signature('a')
        <class 'str'>
        >>> PureSet.get_signature(b'a')
        <class 'bytes'>
        >>> PureSet.get_signature([1, 2, 3])
        (<class 'list'>, (<class 'int'>, 3))
        >>> PureSet.get_signature((1, 2, 3))
        (<class 'tuple'>, (<class 'int'>, 3))
        >>> PureSet.get_signature({'a': 1, 'b': 2})
        (<class 'dict'>, {'a': <class 'int'>, 'b': <class 'int'>})
        >>> PureSet.get_signature({'a': 1, 'b': {'c': 2}})
        (<class 'dict'>, {'a': <class 'int'>, 'b': (<class 'dict'>, {'c': <class 'int'>})})
        >>> PureSet.get_signature({'a': 1, 'b': [2, 3]})
        (<class 'dict'>, {'a': <class 'int'>, 'b': (<class 'list'>, (<class 'int'>, 2))})
        """
        if obj is None: return type(None)

        try:
            import numpy as np
            import pandas as pd
            if isinstance(obj, np.ndarray):
                return (np.ndarray, obj.shape, str(obj.dtype))
            if isinstance(obj, np.generic):
                return type(obj)
            if isinstance(obj, pd.Series):
                return (pd.Series, str(obj.dtype), len(obj))
            if isinstance(obj, pd.DataFrame):
                return (pd.DataFrame, tuple(obj.columns), tuple(str(dt) for dt in obj.dtypes), obj.shape)
            if isinstance(obj, pd.Index):
                return (pd.Index, str(obj.dtype), len(obj))
        except ImportError:
            pass

        obj_type = type(obj)
        if obj_type in (int, float, complex, bool, str, bytes): return obj_type

        if isinstance(obj, dict): return (dict, {k: PureSet.get_signature(v) for k, v in sorted(obj.items())})

        if hasattr(obj, "__dict__") or hasattr(obj, "__slots__"):
            props = {
                name: PureSet.get_signature(getattr(obj, name))
                for name in dir(obj)
                if not (
                    name.startswith("_")
                    or name.endswith("_")
                    or callable(getattr(obj, name))
                )
            }

            if props: return (obj_type, props)

        if hasattr(obj, "__iter__") and obj_type not in (str, bytes, type):
            types       = []
            last_type   = None
            last_count  = 0

            for item in obj:
                current_type = PureSet.get_signature(item)
                if current_type == last_type: last_count += 1
                else:
                    if last_type is not None:
                        types.append(
                            (last_type, last_count) if last_count > 1 else last_type
                        )

                    last_type   = current_type
                    last_count  = 1

            if last_type is not None: types.append((last_type, last_count) if last_count > 1 else last_type)

            if len(types) == 1: return (obj_type, types[0])
            return (obj_type, *types)

        if (
            hasattr(obj, "__len__")
            and hasattr(obj, "__getitem__")
            and obj_type not in (str, bytes, type)
        ):
            element_types   = [PureSet.get_signature(x) for x in obj]
            current_type    = element_types[0]
            count           = 1
            types           = []

            for elem_type in element_types[1:]:
                if elem_type == current_type: count += 1
                else:
                    types.append((current_type, count) if count > 1 else current_type)
                    current_type = elem_type
                    count = 1

            types.append((current_type, count) if count > 1 else current_type)
            return (obj_type, types[0] if len(types) == 1 else tuple(types))

        return obj_type

    @staticmethod
    def freeze(obj: object, seen: Optional[Set] = None) -> Hashable:
        """
        Recursively freeze any object to a deeply immutable, hashable representation
        for PureSet. Used to enforce canonical uniqueness, immutability, and reliable hashing.
        - Atoms (numbers, str, bytes, type, frozenset, bool) are returned as-is.
        - Enum values are stored as (enum type, value).
        - PureSet is frozen as (PureSet, tuple of frozen elements).
        - NamedTuple as (type, tuple of frozen fields in declared order).
        - Tuples, lists, sets, mappings/Sequence are tagged with type and contain frozen items.
        - Dataclasses and __slots__ classes are frozen as (type, tuple of (name, frozen_value)).
        - Standard user classes (__dict__) as (type, tuple of (attr, frozen_value)).
        - Cyclical references raise ValueError.
        Examples
        --------
        >>> PureSet.freeze(42)
        42
        >>> PureSet.freeze('foo')
        'foo'
        >>> from enum import Enum
        >>> class Color(Enum): RED=1; GREEN=2
        >>> PureSet.freeze(Color.RED)
        (<enum 'Color'>, 1)
        >>> PureSet.freeze([1, 2, 3])
        (<class 'list'>, (1, 2, 3))
        >>> PureSet.freeze((1, 2, 3))
        (<class 'tuple'>, (1, 2, 3))
        >>> PureSet.freeze({1, 2, 3})
        (<class 'set'>, (1, 2, 3))
        >>> PureSet.freeze({'a': 1, 'b': 2})
        (<class 'dict'>, (('a', 1), ('b', 2)))
        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', 'x y')
        >>> PureSet.freeze(Point(1, 2))
        (<class '__main__.Point'>, (1, 2))
        >>> class A: pass
        >>> PureSet.freeze(A())[:1]
        Traceback (most recent call last):
            ...
        TypeError: Cannot safely freeze object of type <class '__main__.A'> for PureSet.
        >>> a = []; a.append(a)
        >>> PureSet.freeze(a)
        Traceback (most recent call last):
            ...
        ValueError: Cyclical reference detected
        >>> ps = PureSet(PureSet(1, 2), PureSet(3, 4))
        >>> PureSet.freeze(ps)
        (<class '__main__.PureSet'>, ((<class '__main__.PureSet'>, (1, 2)), (<class '__main__.PureSet'>, (3, 4))))
        """
        if seen is None: seen = set()
        obj_id = id(obj)
        if obj_id in seen: raise ValueError("Cyclical reference detected")
        seen.add(obj_id)
        try:
            try:
                import numpy as np
            except ImportError:
                np = None
            if np is not None:
                if isinstance(obj, np.ndarray):
                    return (np.ndarray, (obj.shape, str(obj.dtype), obj.tobytes()))
                if isinstance(obj, np.generic):
                    return (type(obj), obj.item())
            try:
                import pandas as pd
            except ImportError:
                pd = None
            if pd is not None:
                if isinstance(obj, pd.Series):
                    return (pd.Series, (obj.dtype.name, tuple(obj.index), tuple(obj.values)))
                if isinstance(obj, pd.DataFrame):
                    return (pd.DataFrame, (tuple(obj.columns), tuple(obj.dtypes.astype(str)), tuple(obj.index), tuple(map(tuple, obj.values))))
                if isinstance(obj, pd.Index):
                    return (pd.Index, (obj.dtype.name, tuple(obj)))
            if isinstance(obj, PureSet):
                return (PureSet, tuple(PureSet.freeze(x, seen) for x in obj.restored))
            if obj is None or isinstance(obj, (Number, bool, str, bytes, frozenset, type)):
                return obj
            if isinstance(obj, range):
                return (range, (obj.start, obj.stop, obj.step))
            if isinstance(obj, memoryview):
                return (memoryview, obj.tobytes())
            if isinstance(obj, array):
                return (array, (obj.typecode, obj.tobytes()))
            if isinstance(obj, UserString):
                return (UserString, PureSet.freeze(obj.data, seen))
            if isinstance(obj, UserList):
                return (UserList, tuple(PureSet.freeze(x, seen) for x in obj))
            if isinstance(obj, UserDict):
                return (UserDict, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
            if isinstance(obj, deque):
                return (deque, tuple(PureSet.freeze(x, seen) for x in obj))
            if isinstance(obj, ChainMap):
                return (ChainMap, tuple(PureSet.freeze(m, seen) for m in obj.maps))
            if isinstance(obj, Counter):
                return (Counter, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
            if isinstance(obj, OrderedDict):
                return (OrderedDict, tuple((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items()))
            if isinstance(obj, defaultdict):
                factory = obj.default_factory.__name__ if obj.default_factory else None
                return (
                    defaultdict,
                    (factory, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
                )
            if isinstance(obj, Enum):
                return (type(obj), obj.value)
            if isinstance(obj, tuple) and hasattr(obj, "_fields"):
                return (type(obj), tuple(PureSet.freeze(getattr(obj, f), seen) for f in obj._fields))
            if isinstance(obj, tuple):
                return (tuple, tuple(PureSet.freeze(x, seen) for x in obj))
            if isinstance(obj, list):
                return (list, tuple(PureSet.freeze(x, seen) for x in obj))
            if isinstance(obj, set):
                return (set, tuple(sorted(PureSet.freeze(x, seen) for x in obj)))
            if isinstance(obj, dict):
                return (dict, tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
            if isinstance(obj, Mapping):
                return (type(obj), tuple(sorted((PureSet.freeze(k, seen), PureSet.freeze(v, seen)) for k, v in obj.items())))
            if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, tuple, list, PureSet, UserString, deque)):
                return (type(obj), tuple(PureSet.freeze(x, seen) for x in obj))
            if isinstance(obj, Set) and not isinstance(obj, (set, frozenset, PureSet)):
                return (type(obj), tuple(sorted(PureSet.freeze(x, seen) for x in obj)))
            if hasattr(obj, '__dataclass_fields__'):
                field_names = sorted(f.name for f in obj.__dataclass_fields__.values())
                return (type(obj), tuple((f, PureSet.freeze(getattr(obj, f), seen)) for f in field_names))
            if hasattr(obj, '__slots__'):
                slot_fields = [
                    (s, PureSet.freeze(getattr(obj, s), seen))
                    for s in sorted(getattr(obj, '__slots__', ()))
                    if hasattr(obj, s)
                ]
                if slot_fields:
                    return (type(obj), tuple(slot_fields))
            if hasattr(obj, '__dict__'):
                fields = [
                    (k, PureSet.freeze(v, seen))
                    for k, v in sorted(vars(obj).items())
                    if not (k.startswith('__') and k.endswith('__')) and not callable(getattr(obj, k))
                ]
                if fields:
                    return (type(obj), tuple(fields))
            raise TypeError(f"Cannot safely freeze object of type {type(obj)} for PureSet.")
        finally:
            seen.remove(obj_id)

    @staticmethod
    def restore(obj: tuple[T, object]) -> T:
        """
        Restore an object from its frozen, hashable PureSet representation.

        Handles all canonical outputs from .freeze, rebuilding not just built-ins
        but also PureSet, NamedTuple, Enums, dataclasses, __slots__, and user classes.

        Examples
        --------
        >>> PureSet.restore(42)
        42
        >>> PureSet.restore((list, (1, 2, 3)))
        [1, 2, 3]
        >>> PureSet.restore((tuple, (4, 5, 6)))
        (4, 5, 6)
        >>> PureSet.restore((set, (7, 8))) == set((7, 8))
        True
        >>> PureSet.restore((dict, (('x', 10), ('y', 20))))
        {'x': 10, 'y': 20}
        >>> from enum import Enum
        >>> class Color(Enum): RED=1; GREEN=2
        >>> PureSet.restore((Color, 1))
        <Color.RED: 1>
        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', 'x y')
        >>> PureSet.restore((Point, (3, 4)))
        Point(x=3, y=4)
        >>> class S:
        ...   def __init__(self): self.a = 7
        >>> inst = PureSet.restore((S, (('a', 7),)))
        >>> type(inst) is S and inst.a == 7
        True
        >>> PureSet.restore((PureSet, ((tuple, (1, 2)), (tuple, (3, 4)))))
        PureSet((1, 2), (3, 4))
        """
        try: import pandas as pd
        except ImportError: pd = None
        try: import numpy as np
        except ImportError: np = None
        if obj is None or isinstance(obj, (Number, bool, str, bytes, frozenset, type)):
            return obj
        if isinstance(obj, tuple) and len(obj) == 2:
            kind, content = obj
            if np is not None:
                if kind is np.ndarray:
                    shape, dtype, bts = content
                    return np.frombuffer(bts, dtype=dtype).reshape(shape)
                if np and issubclass(kind, np.generic):
                    return kind(content)
            if pd is not None:
                if kind is pd.Series:
                    dtype_name, idx, vals = content
                    return pd.Series(list(vals), index=list(idx), dtype=dtype_name)
                if kind is pd.DataFrame:
                    cols, dtypes, idx, rows = content
                    import numpy as np
                    arr = np.array(rows)
                    df = pd.DataFrame(arr, columns=cols, index=idx)
                    for c, dtype in zip(cols, dtypes):
                        df[c] = df[c].astype(dtype)
                    return df
                if kind is pd.Index:
                    dtype_name, vals = content
                    return pd.Index(list(vals), dtype=dtype_name)
            if kind is PureSet:
                return PureSet(*(PureSet.restore(x) for x in content))
            if kind is UserString:
                return UserString(PureSet.restore(content))
            if kind is UserList:
                return UserList([PureSet.restore(x) for x in content])
            if kind is UserDict:
                return UserDict({PureSet.restore(k): PureSet.restore(v) for k, v in content})
            if kind is deque:
                return deque([PureSet.restore(x) for x in content])
            if kind is ChainMap:
                return ChainMap(*[PureSet.restore(m) for m in content])
            if kind is Counter:
                return Counter({PureSet.restore(k): PureSet.restore(v) for k, v in content})
            if kind is OrderedDict:
                return OrderedDict((PureSet.restore(k), PureSet.restore(v)) for k, v in content)
            if kind is defaultdict:
                _, items = content
                d = defaultdict(None)
                d.update({PureSet.restore(k): PureSet.restore(v) for k, v in items})
                return d
            if kind is range:
                s, e, st = content
                return range(s, e, st)
            if kind is memoryview:
                return memoryview(PureSet.restore(content))
            if kind is array:
                tc, bts = content
                return array(tc, bts)
            if isinstance(kind, type) and issubclass(kind, Enum):
                return kind(content)
            if isinstance(kind, type) and hasattr(kind, "_fields"):
                return kind(*(PureSet.restore(x) for x in content))
            if kind is tuple:
                return tuple(PureSet.restore(x) for x in content)
            if kind is list:
                return [PureSet.restore(x) for x in content]
            if kind is set:
                return set(PureSet.restore(x) for x in content)
            if kind is dict:
                return {PureSet.restore(k): PureSet.restore(v) for k, v in content}
            if isinstance(kind, type) and issubclass(kind, Mapping):
                return kind((PureSet.restore(k), PureSet.restore(v)) for k, v in content)
            if isinstance(kind, type) and issubclass(kind, Sequence) and not hasattr(kind, "_fields"):
                return kind(PureSet.restore(x) for x in content)
            if isinstance(kind, type) and issubclass(kind, Set):
                return kind(PureSet.restore(x) for x in content)
            if hasattr(kind, '__dataclass_fields__'):
                field_data = {k: PureSet.restore(v) for k, v in content}
                return kind(**field_data)
            if isinstance(kind, type):
                inst = kind.__new__(kind)
                for k, v in content:
                    if not (k.startswith('__') and k.endswith('__')):
                        setattr(inst, k, PureSet.restore(v))
                return inst
        if isinstance(obj, tuple):
            return tuple(PureSet.restore(x) for x in obj)
        return obj

if __name__ == "__main__":
    import doctest
    doctest.testmod()
