"""[||-PureSet-||]
ΛΛΛ Gabriel Maia @gabrielmsilva00 - UERJ - Electric Engineering Undergraduate.
=== A simple collection type for homogeneous, immutable and ordered sequences.

○○○ References and auxiliary material:
••• Black, code formatting;
∙∙∙ pypi.org/project/black/
••• Merlin AI, debugging;
∙∙∙ getmerlin.in/chat
"""

from __future__ import annotations
from copy import deepcopy
from functools import total_ordering
from collections.abc import Sequence
from typing import Any, TypeVar, Union, Optional, Callable, Iterator, overload

# ------------------------------------------------------------
__title__ = "pureset"
__desc__ = "An immutable, homogeneous, and ordered collection type for Python."
__version__ = "1.0.250704.2"
__author__ = "gabrielmsilva00"
__contact__ = "gabrielmaia.silva00@gmail.com"
__repo__ = "github.com/gabrielmsilva00/pureset"
__license__ = "Apache License 2.0"

__all__ = ["PureSet"]


T = TypeVar("T")


def get_signature(obj) -> Union[type, tuple]:
    SIMPLE_TYPES = PureSet.SIMPLE_TYPES
    if obj is None:
        return type(None)
    obj_type = type(obj)

    if obj_type in SIMPLE_TYPES:
        return obj_type

    if isinstance(obj, dict):
        return (dict, {k: get_signature(v) for k, v in sorted(obj.items())})

    if hasattr(obj, "__dict__") or hasattr(obj, "__slots__"):
        props = {
            name: get_signature(getattr(obj, name))
            for name in dir(obj)
            if not (
                name.startswith("_")
                or name.endswith("_")
                or callable(getattr(obj, name))
            )
        }
        if props:
            return (obj_type, props)

    if hasattr(obj, "__iter__") and obj_type not in (str, bytes, type):
        types = []
        last_type = None
        last_count = 0

        for item in obj:
            current_type = get_signature(item)
            if current_type == last_type:
                last_count += 1
            else:
                if last_type is not None:
                    types.append(
                        (last_type, last_count) if last_count > 1 else last_type
                    )
                last_type = current_type
                last_count = 1

        if last_type is not None:
            types.append((last_type, last_count) if last_count > 1 else last_type)

        if len(types) == 1:
            return (tuple, types[0])
        return (tuple, *types)

    if (
        hasattr(obj, "__len__")
        and hasattr(obj, "__getitem__")
        and obj_type not in (str, bytes, type)
    ):
        element_types = [get_signature(x) for x in obj]
        current_type = element_types[0]
        count = 1
        types = []

        for elem_type in element_types[1:]:
            if elem_type == current_type:
                count += 1
            else:
                types.append((current_type, count) if count > 1 else current_type)
                current_type = elem_type
                count = 1

        types.append((current_type, count) if count > 1 else current_type)

        return (obj_type, types[0] if len(types) == 1 else tuple(types))

    return obj_type


@total_ordering
class PureSet(Sequence[T]):
    __slots__ = ("_items", "_set", "_hashable", "_signature", "__weakref__")
    SIMPLE_TYPES: frozenset[type] = frozenset({int, float, str, bytes, bool, complex})

    def __init__(self, *args: T) -> None:
        if not args:
            self._items = ()
            self._set = frozenset()
            self._hashable = True
            self._signature = None
            return
        sig = get_signature(args[0])
        for i, item in enumerate(args):
            if get_signature(item) != sig:
                raise TypeError(
                    f"Incompatible element type or shape at position {i+1}:\nExp: {sig};\nGot: {get_signature(item)}"
                )
        self._signature = sig
        try:
            hash(args[0])
            hashable = True
        except TypeError:
            hashable = False
        self._hashable = hashable
        if hashable:
            seen = set()
            unique_items = []
            for item in args:
                if item not in seen:
                    seen.add(item)
                    unique_items.append(item)
        else:
            unique_items = []
            for item in args:
                if item not in unique_items:
                    unique_items.append(item)
        self._items = tuple(unique_items)
        self._set = frozenset(self._items) if hashable else None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__slots__:
            # Allow on initialization only
            object.__setattr__(self, name, value)
        else:
            raise AttributeError(f"{self.__class__.__name__} is immutable")

    @property
    def items(self) -> tuple[T, ...]:
        return self._items

    @property
    def set(self) -> Optional[frozenset]:
        return self._set

    @property
    def hashable(self) -> bool:
        return self._hashable

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
        <class '__main__.C'>
        """
        return self._signature

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
        if self._items:
            return (self.__class__, self._items)
        else:
            return (self.__class__, ())

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
        if self._items:
            return self.__class__(*self._items)
        else:
            return self.__class__()

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
        if self._items:
            new_items = tuple(deepcopy(item, memo) for item in self._items)
            return self.__class__(*new_items)
        else:
            return self.__class__()

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
        return len(self._items)

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
        return iter(self._items)

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
        return hash((type(self), self._items))

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
        if not self._items:
            return f"{self.__class__.__name__}()"
        return f"{self.__class__.__name__}({', '.join(map(repr, self._items))})"

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
        if not self._items:
            return f"{self.__class__.__name__}()"
        items_str = ", ".join(repr(item) for item in self._items[:10])
        if len(self._items) > 10:
            items_str += f", ... ({len(self._items) - 10} more items)"
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
        if self._hashable and self._set is not None:
            return item in self._set
        return item in self._items

    def __getitem__(self, idx: Union[int, slice, T]) -> Union[T, PureSet[T]]:
        """Get element by index, slice, or value lookup.

        Parameters
        ----------
        idx : Union[int, slice, T]
            Index, slice, or value to retrieve

        Returns
        -------
        Union[T, PureSet[T]]
            Single element or new PureSet (for slices)

        Raises
        ------
        IndexError
            If integer index is out of range
        KeyError
            If value is not found

        Examples
        --------
        >>> ps = PureSet(10, 20, 30, 40)
        >>> ps[0]
        10
        >>> ps[-1]
        40
        >>> ps[1:3]
        PureSet(20, 30)
        """
        if isinstance(idx, int):
            return self._items[idx]
        elif isinstance(idx, slice):
            return self.__class__(*self._items[idx])
        else:
            if idx in self:
                return idx
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
        return isinstance(other, PureSet) and self._items == other._items

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
        >>> PureSet(1, 2) <= PureSet(1, 2)
        True
        """
        if not isinstance(other, PureSet):
            return NotImplemented
        return self._items < other._items

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
        if not isinstance(other, PureSet):
            return NotImplemented
        if self.signature and other.signature:
            if self.signature != other.signature:
                raise TypeError(
                    f"Cannot concatenate PureSets with different element types: "
                    f"Exp: {self.signature}\nGot: {other.signature}"
                )
        if not self._items:
            return other
        if not other._items:
            return self
        combined = list(self._items) + list(other._items)
        return self.__class__(*combined)

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
        if not isinstance(n, int):
            return NotImplemented
        if n <= 0:
            return self.__class__()
        if n == 1:
            return self
        repeated = list(self._items) * n
        return self.__class__(*repeated)

    def __rmul__(self, n: int) -> PureSet[T]:
        """Right multiplication (n * PureSet).

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
        >>> 3 * PureSet(1, 2)
        PureSet(1, 2)
        >>> 0 * PureSet(1, 2)
        PureSet()
        """
        return self.__mul__(n)

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
        >>> ps.pos(10)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        IndexError: Index 10 out of range for length 3
        """
        try:
            return self._items[index]
        except IndexError:
            raise IndexError(f"Index {index} out of range for length {len(self)}")

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
        >>> ps.index(10, 1, 3)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        ValueError: 10 not in range [1:3]
        """
        if value not in self:
            raise ValueError(f"{value!r} is not in {self.__class__.__name__}")
        try:
            if stop is None:
                return self._items.index(value, start)
            else:
                return self._items.index(value, start, stop)
        except ValueError:
            raise ValueError(f"{value!r} not in range [{start}:{stop}]")

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
        return sep.join(map(str, self._items))

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
        return self.__class__(*reversed(self._items))

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
        return list(self._items)

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
        return self._items

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
        >>> ps.to_frozenset()  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        TypeError: Cannot convert unhashable elements to frozenset
        """
        if not self._hashable:
            raise TypeError("Cannot convert unhashable elements to frozenset")
        return self._set

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
        >>> ps1.compatible(ps_str)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        TypeError: Incompatible element types: int and str
        """
        if not isinstance(other, PureSet):
            raise TypeError(f"Expected PureSet, got '{type(other)}'")
        if self._items and other._items:
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
        if not other._items:
            return self
        if not self._items:
            return other
        if self._hashable and other._hashable:
            result = list(self._items)
            self_set = self._set
            for item in other._items:
                if item not in self_set:
                    result.append(item)
            return self.__class__(*result)
        result = list(self._items)
        for item in other._items:
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
        if self._hashable and other._hashable:
            if len(self) <= len(other):
                return self.__class__(*(x for x in self._items if x in other._set))
            else:
                return self.__class__(*(x for x in other._items if x in self._set))
        if len(self) <= len(other):
            return self.__class__(*(x for x in self._items if x in other))
        else:
            return self.__class__(*(x for x in other._items if x in self))

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
        if self._hashable and other._hashable:
            return self.__class__(*(x for x in self._items if x not in other._set))
        return self.__class__(*(x for x in self._items if x not in other))

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
        if self._hashable and other._hashable:
            self_set = self._set
            other_set = other._set
            result = [x for x in self._items if x not in other_set]
            result.extend(x for x in other._items if x not in self_set)
            return self.__class__(*result)
        result = [x for x in self._items if x not in other]
        result.extend(x for x in other._items if x not in self)
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
        filtered = [item for item in self._items if predicate(item)]
        return self.__class__(*filtered)

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
        mapped = [function(item) for item in self._items]
        return self.__class__(*mapped)

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
        return self._items[0] if self._items else default

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
        return self._items[-1] if self._items else default

    def sorted(
        self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False
    ) -> PureSet[T]:
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
        sorted_items = sorted(self._items, key=key, reverse=reverse)
        return self.__class__(*sorted_items)

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
        return item if item in self._items else default


if __name__ == "__main__":
    import doctest

    try:
        import black

        with open(__file__, "r+") as f:
            src = f.read()
            f.seek(0)
            f.write(black.format_str(src, mode=black.FileMode()))
            f.truncate()
    finally:
        doctest.testmod()
