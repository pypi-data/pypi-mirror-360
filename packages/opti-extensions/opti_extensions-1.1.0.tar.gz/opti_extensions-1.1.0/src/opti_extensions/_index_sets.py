# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""IndexSet data structures."""

from __future__ import annotations

import inspect
import sys
from collections import defaultdict
from collections.abc import Callable, Collection, Iterable, Iterator, MutableSequence, Sequence
from datetime import date, datetime
from itertools import product
from operator import itemgetter
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    NoReturn,
    SupportsIndex,
    TypeAlias,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import Self, Unpack, override

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
    from pandas import Timestamp

ElemT = TypeVar('ElemT')
Elem1DT = TypeVar('Elem1DT')
ElemNDT = TypeVar('ElemNDT', bound=tuple[Any, ...])
IndexGroup: TypeAlias = defaultdict[tuple[Any, ...], list[ElemT]]

_T1 = TypeVar('_T1', str, int, date, datetime, 'Timestamp')
_T2 = TypeVar('_T2', str, int, date, datetime, 'Timestamp')
_T3 = TypeVar('_T3', str, int, date, datetime, 'Timestamp')
_T4 = TypeVar('_T4', str, int, date, datetime, 'Timestamp')
_T5 = TypeVar('_T5', str, int, date, datetime, 'Timestamp')


class IndexSetBase(Generic[ElemT]):
    """Base class for custom list-like data structures to define index-sets.

    Provides implementations for:
    1. Mutable sequence operations from `builtins.list`, while preventing duplicates.
    2. Rich comparison operations from `builtins.set`.

    Parameters
    ----------
    elems : list, optional
        Elements to be encapsulated in the IndexSet.

    Raises
    ------
    ValueError
        If any element in input is invalid.
    ValueError
        If the input includes duplicate elements.
    """

    # Private attributes
    # ------------------
    # _list : list
    #     List of elements for mutable sequence operations.
    # _set : set
    #     Set of elements for preventing duplicates, faster `in` lookup, and rich comparisons.

    __slots__ = ('_list', '_set')

    def __init__(self, elems: list[ElemT] | None = None) -> None:
        if elems is not None:
            if self._validate_elements(elems):
                self._set: set[ElemT] = self._ensure_no_duplicates(elems)
                self._list: list[ElemT] = elems
        else:
            self._set = set()
            """Set of elements for preventing duplicates, faster `in` lookup, and rich
            comparisons."""
            self._list = []
            """List of elements for mutable sequence operations."""

    def __repr__(self) -> str:
        # Printable string representation.
        return self._list.__repr__()

    def _ensure_no_duplicates(self, elems: list[ElemT]) -> set[ElemT]:
        """Ensure that a list of elements has no duplicates and coerce it to a set.

        Parameters
        ----------
        elems : list

        Returns
        -------
        set

        Raises
        ------
        ValueError
            If the list has duplicates.
        """
        unique = set(elems)
        if len(elems) > len(unique):
            raise ValueError(f'input introduced duplicates in {self.__class__.__name__}')
        return unique

    def _validate_elements(self, elems: list[ElemT]) -> bool:
        """Validate all elements of a list.

        Parameters
        ----------
        elems : list

        Returns
        -------
        bool
        """
        # Add specific checks in subclasses by overloading this method
        # No checks in the base class; so always return True
        return True  # pragma: no cover

    def _remove_elements(self, elems: list[ElemT]) -> None:
        """Remove elements from the IndexSet.

        Parameters
        ----------
        elems : list
        """
        self._set.difference_update(elems)

    def _raise_op_not_supported_err(self, op_name: str) -> NoReturn:
        """Raise a type error for an unsupported operation.

        Parameters
        ----------
        op_name : str
        """
        raise TypeError(
            f'`{op_name}` is only supported between two instances of {self.__class__.__name__}'
        )

    def __lt__(self, other: Self, /) -> bool:
        # Rich comparison `self < other' (proper subset), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('<')
        return self._set < other._set

    def __le__(self, other: Self, /) -> bool:
        # Rich comparison `self <= other` (subset), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('<=')
        return self._set <= other._set

    def __eq__(self, other: object, /) -> bool:
        # Rich comparison `self == other` (equivalence), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('==')
        return self._set == other._set

    def __ne__(self, other: object, /) -> bool:
        # Rich comparison `self != other` (non-equivalence), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('!=')
        return self._set != other._set

    def __gt__(self, other: Self, /) -> bool:
        # Rich comparison `self > other` (proper superset), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('>')
        return self._set > other._set

    def __ge__(self, other: Self, /) -> bool:
        # Rich comparison `self >= other` (superset), if other is also of the same type.
        if not isinstance(other, self.__class__):
            self._raise_op_not_supported_err('>=')
        return self._set >= other._set

    def __add__(self, other: Iterable[Any], /) -> Self:
        # Concatenate `self` with `other` and return a new instance.
        if other:  # is pouplated
            try:
                lst_other = list(other)
            except TypeError:
                raise TypeError(
                    f'can only concatenate an iterable to {self.__class__.__name__}'
                ) from None
            if self._list:  # is pouplated
                if self._validate_elements(lst_other):
                    return self.__class__(self._list + lst_other)
            return self.__class__(lst_other)
        return self.__class__(self._list)

    def __iadd__(self, other: Iterable[Any], /) -> Self:
        # Concatenate `self` with `other`, in-place.
        if other:  # is pouplated
            try:
                lst_other = list(other)
            except TypeError:
                raise TypeError(
                    f'can only concatenate an iterable to {self.__class__.__name__}'
                ) from None
            if self._validate_elements(lst_other):
                added = self._list + lst_other
                self._set = self._ensure_no_duplicates(added)
                self._list = added
        return self

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> ElemT: ...

    @overload
    def __getitem__(self, index: slice, /) -> list[ElemT]: ...

    def __getitem__(self, index: SupportsIndex | slice, /) -> ElemT | list[ElemT]:
        # Get element(s) at particular position index or slice.
        try:
            return self._list[index]
        except IndexError:
            raise IndexError('position index out of range') from None
        except TypeError:
            raise TypeError(
                f'position indices must be integers or slices, not {type(index).__name__}'
            ) from None

    def _setitem_idx(self, index: SupportsIndex, elem: ElemT, /) -> None:
        # __setitem__ implementation for `index` input.
        lst_elem = [elem]
        if self._validate_elements(lst_elem):
            try:
                old: ElemT = self._list[index]  # access old elem at given position index
            except IndexError:
                raise IndexError('position index out of range') from None
            try:
                self._list[index] = elem
                self._set = self._ensure_no_duplicates(self._list)
            except ValueError:
                self._list[index] = old  # restore the old element
                raise

    def _setitem_slice(self, index: slice, elem: Iterable[ElemT], /) -> None:
        # __setitem__ implementation for `slice` input.
        try:
            lst_elem = list(elem)
        except TypeError:
            raise TypeError('can only assign an iterable') from None
        if self._validate_elements(lst_elem):
            new = lst_elem
            old = self._list.copy()  # copy the list before changing
            try:
                self._list[index] = new
                self._set = self._ensure_no_duplicates(self._list)
            except ValueError:
                self._list = old  # restore the list
                raise

    @overload
    def __setitem__(self, index: SupportsIndex, elem: ElemT, /) -> None: ...

    @overload
    def __setitem__(self, index: slice, elem: Iterable[ElemT], /) -> None: ...

    def __setitem__(self, index: SupportsIndex | slice, elem: ElemT | Iterable[ElemT], /) -> None:
        # Assign element(s) at particular position index or slice.
        match index:
            case SupportsIndex():
                self._setitem_idx(index, cast('ElemT', elem))
            case slice():
                self._setitem_slice(index, cast('Iterable[ElemT]', elem))
            case _:
                raise TypeError(
                    f'position indices must be integers or slices, not {type(index).__name__}'
                )

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        # Remove element(s) at particular position index or slice.
        try:
            match index:
                case SupportsIndex():
                    old_single = self._list[index]  # save old element
                    self._remove_elements([old_single])
                case slice():
                    old_multiple = self._list[index]  # save old elements
                    self._remove_elements(old_multiple)
                case _:
                    raise TypeError(
                        f'position indices must be integers or slices, not {type(index).__name__}'
                    )
            del self._list[index]
        except IndexError:
            raise IndexError('position index out of range') from None

    def __contains__(self, elem: ElemT, /) -> bool:
        # Set membership test: `element in self`.
        return self._set.__contains__(elem)

    def __iter__(self) -> Iterator[ElemT]:
        # Iterate over `self`.
        return iter(self._list)

    def __reversed__(self) -> Iterator[ElemT]:
        # Iterate over `self` in reverse.
        return reversed(self._list)

    def __len__(self) -> int:
        # Get the length of `self`.
        return len(self._list)

    def index(
        self, elem: ElemT, start: SupportsIndex = 0, end: SupportsIndex = sys.maxsize, /
    ) -> int:
        """Get the position index of an element in the IndexSet.

        Parameters
        ----------
        elem : element
        start : int, default ``0`` (beginning of the IndexSet)
            Start searching from this index.
        end : int, default ``sys.maxsize`` (effectively, end of the IndexSet)
            Search up to this index.

        Returns
        -------
        int

        Raises
        ------
        ValueError
            If the element is not found.
        """
        try:
            return self._list.index(elem, start, end)
        except ValueError:
            raise ValueError(f'`{elem}` not in {self.__class__.__name__}') from None

    def append(self, elem: ElemT, /) -> None:
        """Append an element to the end of the IndexSet, in-place.

        Parameters
        ----------
        elem : element

        Raises
        ------
        ValueError
            If the element is invalid.
        ValueError
            If the element is already present in the IndexSet (introduces a duplicate).
        """
        new = [elem]
        if self._validate_elements(new):
            self._set = self._ensure_no_duplicates(self._list + new)
            self._list.append(elem)

    def extend(self, elems: Iterable[ElemT], /) -> None:
        """Extend the IndexSet by appending elements from an iterable, in-place.

        Parameters
        ----------
        elems : iterable

        Raises
        ------
        ValueError
            If any element is invalid.
        ValueError
            If any element is already present in the IndexSet (introduces duplicate(s)).
        """
        try:
            new = list(elems)
        except TypeError:
            raise TypeError(f'can only extend {self.__class__.__name__} with an iterable') from None
        if self._validate_elements(new):
            self._set = self._ensure_no_duplicates(self._list + new)
            self._list.extend(new)

    def insert(self, index: SupportsIndex, elem: ElemT, /) -> None:
        """Insert an element at a position index in the IndexSet.

        Parameters
        ----------
        index : int
        elem : element

        Raises
        ------
        ValueError
            If the element is invalid.
        ValueError
            If the element is already present in the IndexSet (introduces a duplicate).
        """
        match index:
            case int():
                elems = [elem]
                if self._validate_elements(elems):
                    self._set = self._ensure_no_duplicates(self._list + elems)
                    self._list.insert(index, elem)
            case _:
                raise TypeError(f'position index must be an integer, not {type(index).__name__}')

    def remove(self, elem: ElemT, /) -> None:
        """Remove an element from the IndexSet, in-place.

        Parameters
        ----------
        elem : element

        Raises
        ------
        ValueError
            If the element is not present in the IndexSet.
        """
        try:
            self._list.remove(elem)
            self._remove_elements([elem])
        except ValueError:
            raise ValueError(f'`{elem}` not in {self.__class__.__name__}') from None

    def pop(self, index: int = -1, /) -> ElemT:
        """Remove and return the element at a position index in the IndexSet.

        Parameters
        ----------
        index : int, default ``-1`` (last element)

        Returns
        -------
        element

        Raises
        ------
        IndexError
            If the IndexSet is empty.
        IndexError
            If position index is out of range.
        """
        # Don't need to override the error message from list class
        elem = self._list.pop(index)
        self._remove_elements([elem])
        return elem

    def clear(self) -> None:
        """Remove all elements from the IndexSet."""
        if self._list:  # is pouplated
            self._list.clear()
            self._set.clear()

    def sort(
        self,
        *,
        key: Callable[[ElemT], SupportsRichComparison] | None = None,
        reverse: bool = False,
    ) -> None:
        """Sort the IndexSet in ascending order, in-place.

        Parameters
        ----------
        key : function, optional
            Function to be applied to each element to get comparison keys for sorting order, by
            default ``None``.
        reverse : bool, default ``False``
            Whether to sort in descending order.

        Raises
        ------
        TypeError
            When the IndexSet has non-comparable elements i.e., heterogeneous data types like `int`
            and `str` within the same IndexSet.
        """
        self._list.sort(key=key, reverse=reverse)

    def reverse(self) -> None:
        """Reverse the order of elements of the IndexSet, in-place."""
        self._list.reverse()


class IndexSet1D(IndexSetBase[Elem1DT]):
    """Custom list-like data structure to define index-sets with 1-dim scalar elements.

    Requires all elements to be unique scalars (such as `int`, `str`, `Timestamp`, etc.).
    Supports all mutable sequence operations from `builtins.list` and rich comparisons from
    `builtins.set`.

    Parameters
    ----------
    iterable : iterable, optional
        Input data to be encapsulated in the IndexSet.
    name : str, optional
        Name to refer to 1-dim scalar elements - not used internally, and solely for user
        reference.

    Raises
    ------
    TypeError
        If the input contains non-scalar element(s) (any iterable except string).
    ValueError
        If the input includes (or creates) duplicate elements.

    See Also
    --------
    IndexSetND : For N-dim tuple elements.

    Examples
    --------
    Constructing empty to populate later:

    >>> IndexSet1D()
    IndexSet1D:
    []

    Constructing with an iterable:

    >>> IndexSet1D(range(3))
    IndexSet1D:
    [0, 1, 2]

    >>> IndexSet1D(['Delhi', 'Seattle', 'Tokyo'], name='CITY')
    IndexSet1D: (CITY)
    ['Delhi', 'Seattle', 'Tokyo']
    """

    # Private attributes
    # ------------------
    # _list : list
    #     List of elements for mutable sequence operations.
    # _set : set
    #     Set of elements for identifying duplicates, faster `in` lookup, and rich comparisons.

    __slots__ = ('_name',)

    def __init__(
        self, iterable: Iterable[Elem1DT] | None = None, /, *, name: str | None = None
    ) -> None:
        self.name = name

        if iterable is not None:
            try:
                elems = list(iterable)
            except TypeError:
                raise TypeError(f'{self.__class__.__name__} expected an iterable input') from None

            super().__init__(elems)

        else:
            super().__init__(None)

    @property
    def name(self) -> str | None:
        """Name to refer to 1-dim scalar elements.

        Not used internally, and solely for user reference.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        match value:
            case None | str():
                self._name = value
            case _:
                raise TypeError('`name` should be a string')

    def _get_repr_header(self) -> str:
        # Header for repr.
        if self.name is not None:
            return f'{self.__class__.__name__}: ({self.name})'
        else:
            return f'{self.__class__.__name__}:'

    def __repr__(self) -> str:
        # Printable string representation.
        return f'{self._get_repr_header()}\n{self._list.__repr__()}'

    def _repr_pretty_(self, p, cycle: bool) -> None:  # type: ignore[no-untyped-def]
        # Pretty repr for IPython.
        # https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#extending
        # Since IPython is not typed, we'll add a type ignore comment here
        # The annotation for arg `p` is `IPython.lib.pretty.RepresentationPrinter`
        p.text(f'{self._get_repr_header()}\n')
        p.pretty(self._list)

    @staticmethod
    def _check_allscalars(elems: list[Elem1DT]) -> None:
        """Check if a list contains all 1-dim scalar elements (no iterables except string).

        Parameters
        ----------
        elems : list

        Raises
        ------
        TypeError
            If the list contains non-scalar element(s) (any iterable except string).
        """
        if any((isinstance(x, Iterable) and not isinstance(x, str)) for x in elems):
            raise TypeError('input introduced non-scalar element(s) (no iterables except string)')

    @override
    def _validate_elements(self, elems: list[Elem1DT]) -> bool:
        """Validate all elements of a list.

        Validation includes the following checks:
        * If all elements are 1-dim scalars (no iterables except string).

        Parameters
        ----------
        elems : list

        Returns
        -------
        bool

        Raises
        ------
        TypeError
            If the list contains non-scalar element(s) (any iterable except string).
        """
        self._check_allscalars(elems)
        return True

    # Inheriting from Generic causes `inspect.signature` to return the signature of Generic's
    # `__new__` for this class (instead of its own `__init__`). This side-effect leads to an
    # incorrect call signature and return annotation output when calling `help` function for
    # this class. So we amend it by defining `__signature__`.
    __signature__ = inspect.Signature(
        parameters=list(inspect.signature(__init__).parameters.values())[1:],  # skip `self` arg
        return_annotation=inspect.signature(__init__).return_annotation,
    )


class IndexSetND(IndexSetBase[ElemNDT]):
    """Custom list-like data structure to define index-sets with N-dim tuple elements.

    Requires all elements to be unique tuples of the same length, each containing 'N' scalars (such
    as `int`, `str`, `Timestamp`, etc.). Supports all mutable sequence operations from
    `builtins.list` and rich comparisons from `builtins.set`. Allows efficient selection of subsets
    using wildcard patterns with the `subset` method and position indices with the `squeeze` method.

    Parameters
    ----------
    *iterables : iterable, optional
        Input data to be encapsulated in the IndexSet, in one of the following forms:

        * An iterable of unique tuples of the same length, each containing 'N' scalars.
        * An iterable of unique tuple-like containers of the same length, each containing 'N'
          scalars - will be coerced to tuples.
        * An arbitrary number of iterables of scalars or K-dim tuple-like containers or a mix of
          both - will enumerate all possible combinations and construct tuples composed of 'N'
          scalars.

        See examples below.

    names : sequence[str], optional
        Names to refer to each dimension of N-dim tuple elements - not used internally, and solely
        for user reference.

    Raises
    ------
    TypeError
        If input includes (or creates) non-tuple element(s).
    ValueError
        If input includes (or creates) tuple elements of different lengths.
    ValueError
        If input includes (or creates) duplicate elements.

    See Also
    --------
    IndexSet1D : For 1-dim scalar elements.

    Examples
    --------
    Constructing empty to populate later:

    >>> IndexSetND()
    IndexSetND:
    []

    Constructing with a list of tuples:

    >>> IndexSetND(
    ...     [('chair', 0), ('chair', 1), ('chair', 2), ('desk', 0), ('desk', 1), ('desk', 2)],
    ...     names=['PRODUCT', 'PERIOD'],
    ... )
    IndexSetND: (PRODUCT, PERIOD)
    [('chair', 0), ('chair', 1), ('chair', 2), ('desk', 0), ('desk', 1), ('desk', 2)]

    Constructing with an arbitrary number of iterables to enumerate all possible combinations:

    >>> IndexSetND(range(2), range(2), range(2))
    IndexSetND:
    [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]

    >>> IndexSetND(['chair', 'desk'], range(3), names=['PRODUCT', 'PERIOD'])
    IndexSetND: (PRODUCT, PERIOD)
    [('chair', 0), ('chair', 1), ('chair', 2), ('desk', 0), ('desk', 1), ('desk', 2)]

    >>> IndexSetND(
    ...     [('chair', 'WH-A'), ('chair', 'WH-B'), ('desk', 'WH-B')],
    ...     range(2),
    ...     names=['PRODUCT', 'WAREHOUSE', 'PERIOD'],
    ... )
    IndexSetND: (PRODUCT, WAREHOUSE, PERIOD)
    [('chair', 'WH-A', 0),
     ('chair', 'WH-A', 1),
     ('chair', 'WH-B', 0),
     ('chair', 'WH-B', 1),
     ('desk', 'WH-B', 0),
     ('desk', 'WH-B', 1)]
    """

    # Private attributes
    # ------------------
    # _list : list
    #     List of elements for mutable sequence operations.
    # _set : set
    #     Set of elements for identifying duplicates, faster `in` lookup, and rich comparisons.
    # _tuplelen : int
    #     Length of each tuple element.
    # _index_groups : dict[tuple, defaultdict[tuple, list]]
    #     Cache of index groups for efficient `subset` and `squeeze` operations.
    #     * Keys:   Unique combinations of tuple element values at given dimension indices.
    #     * Values: Tuple elements corresponding to the combination, if any (or an empty list
    #               otherwise).

    __slots__ = ('_names', '_tuplelen', '_index_groups')

    @overload  # 2
    def __init__(
        self: IndexSetND[tuple[_T1, _T2]],
        __iterable: Iterable[tuple[_T1, _T2]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 2 = 1 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[_T2],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 3
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3]],
        __iterable: Iterable[tuple[_T1, _T2, _T3]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 3 = 2 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3]],
        __iterable1: Iterable[tuple[_T1, _T2]],
        __iterable2: Iterable[_T3],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 3 = 1 + 2
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[tuple[_T2, _T3]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 3 = 1 + 1 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[_T2],
        __iterable3: Iterable[_T3],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable: Iterable[tuple[_T1, _T2, _T3, _T4]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 3 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[tuple[_T1, _T2, _T3]],
        __iterable2: Iterable[_T4],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 2 + 2
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[tuple[_T1, _T2]],
        __iterable2: Iterable[tuple[_T3, _T4]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 2 + 1 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[tuple[_T1, _T2]],
        __iterable2: Iterable[_T3],
        __iterable3: Iterable[_T4],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 1 + 3
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[tuple[_T2, _T3, _T4]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 1 + 2 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[tuple[_T2, _T3]],
        __iterable3: Iterable[_T4],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 4 = 1 + 1 + 1 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[_T2],
        __iterable3: Iterable[_T3],
        __iterable4: Iterable[_T4],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 5
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4, _T5]],
        __iterable: Iterable[tuple[_T1, _T2, _T3, _T4, _T5]],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # 5 = 1 + 1 + 1 + 1 + 1
    def __init__(
        self: IndexSetND[tuple[_T1, _T2, _T3, _T4, _T5]],
        __iterable1: Iterable[_T1],
        __iterable2: Iterable[_T2],
        __iterable3: Iterable[_T3],
        __iterable4: Iterable[_T4],
        __iterable5: Iterable[_T5],
        *,
        names: Sequence[str] | None = ...,
    ) -> None: ...

    @overload  # catch-all for everything else
    def __init__(
        self: IndexSetND[tuple[Any, ...]],
        *iterables: Iterable[Any],
        names: Sequence[str] | None = ...,
    ) -> None: ...

    def __init__(self, *iterables: Iterable[Any], names: Sequence[str] | None = None) -> None:
        self.names = names

        self._index_groups: dict[tuple[int, ...], IndexGroup[ElemNDT]] = {}
        """Cache of index groups for efficient `subset` and `squeeze` operations."""

        self._tuplelen: int
        """Length of each tuple element."""

        if iterables:  # is populated
            type_error_msg = f'{self.__class__.__name__} expected iterable input(s)'

            if len(iterables) > 1:
                try:
                    elems: list[tuple[Any, ...]] = list(product(*iterables))
                except TypeError:
                    raise TypeError(type_error_msg) from None

                if elems:  # is populated
                    # if product combinations are nested iterables, flatten to tuple elements
                    if any(isinstance(i, Iterable) and not isinstance(i, str) for i in elems[0]):
                        elems = [tuple(self._flatten(x)) for x in elems]

            else:
                try:
                    elems = list(*iterables)
                except TypeError:
                    raise TypeError(type_error_msg) from None

                # if elements are non-tuple iterables, coerce them to tuple elements
                if elems and all(
                    not isinstance(elem, tuple)
                    and not isinstance(elem, str)
                    and isinstance(elem, Collection)
                    for elem in elems
                ):
                    elems = [tuple(elem) for elem in elems]

            if elems:  # is populated
                super().__init__(cast('list[ElemNDT]', elems))
            else:
                super().__init__(None)

        else:
            super().__init__(None)

    @property
    def names(self) -> Sequence[str] | None:
        """Names to refer to each dimension of N-dim tuple elements.

        Not used internally, and solely for user reference.

        Returns
        -------
        sequence[str]
        """
        return self._names

    @names.setter
    def names(self, value: Sequence[str] | None) -> None:
        match value:
            case None:
                self._names = None
            case str():
                raise TypeError('`names` should be a sequence of strings')
            case Sequence() if all(isinstance(name, str) for name in value):
                self._names = list(value)
            case _:
                raise TypeError('`names` should be a sequence of strings')

    def _get_repr_header(self) -> str:
        # Header for repr.
        if self.names is not None:
            return f'{self.__class__.__name__}: ({", ".join(self.names)})'
        else:
            return f'{self.__class__.__name__}:'

    def __repr__(self) -> str:
        # Printable string representation.
        return f'{self._get_repr_header()}\n{self._list.__repr__()}'

    def _repr_pretty_(self, p, cycle: bool) -> None:  # type: ignore[no-untyped-def]
        # Pretty repr for IPython.
        # https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#extending
        # Since IPython is not typed, we'll add a type ignore comment here
        # The annotation for arg `p` is `IPython.lib.pretty.RepresentationPrinter`
        p.text(f'{self._get_repr_header()}\n')
        p.pretty(self._list)

    def __le__(self, other: Self | tuple[IndexSet1D[Any], ...], /) -> bool:
        """Rich comparison method as a subset check: self <= other.

        Parameters
        ----------
        other : IndexSetND or tuple[IndexSet1D, ...]

        Returns
        -------
        bool

        Raises
        ------
        TypeError
            If checked with an object that's not IndexSetND or a tuple of IndexSet1D
        LookupError
            If the IndexSetND is empty and checked with a tuple of IndexSet1D
        ValueError
            If checked with a tuple of IndexSet1D that is not the same length as the elements of
            the IndexSetND

        Examples
        --------
        >>> vals = IndexSet1D(range(10))
        >>> all_combinations = IndexSetND(vals, vals)
        >>> sparse_combinations = IndexSetND([(0, 0), (1, 4), (3, 1), (9, 6), (9, 9)])

        Direct subset check with another IndexSetND

        >>> sparse_combinations <= all_combinations
        True

        Subset check with a tuple of two IndexSet1D

        >>> sparse_combinations <= (vals, vals)
        True

        >>> fewer_vals = IndexSet1D(range(4))
        >>> sparse_combinations <= (fewer_vals, fewer_vals)
        False
        """
        if isinstance(other, self.__class__):
            return self._set <= other._set

        elif isinstance(other, tuple) and all(isinstance(x, IndexSet1D) for x in other):
            if not self:  # not populated
                raise LookupError(f'{self.__class__.__name__} is empty')
            if self._tuplelen != len(other):
                raise ValueError(
                    'tuple of IndexSet1D must be of the same length as the elements of '
                    f'{self.__class__.__name__}'
                )
            for i, vals in enumerate(other):
                if self.squeeze(i) <= vals:  # 1-dim subset check
                    continue
                else:
                    return False
            return True

        else:
            raise TypeError(
                f'`<=` is only supported with {self.__class__.__name__} or a tuple of IndexSet1D'
            )

    @staticmethod
    def _flatten(iterable: Iterable[Any]) -> Iterable[Any]:
        """Recursively flatten a nested iterable.

        Parameters
        ----------
        iterable : iterable
            Nested iterable.

        Yields
        ------
        Any
            Scalar values from the nested iterable.

        Examples
        --------
        >>> tuple(IndexSetND._flatten([0, (1, 2, (3, 4))]))
        (0, 1, 2, 3, 4)
        """
        for val in iterable:
            if isinstance(val, Iterable) and not isinstance(val, str):
                yield from IndexSetND._flatten(val)
            else:
                yield val

    @staticmethod
    def _check_alltuples(elems: list[ElemNDT]) -> None:
        """Check if all elements of a list are tuples.

        Parameters
        ----------
        elems : list

        Raises
        ------
        TypeError
            If the list contains non-tuple element(s).
        """
        if any(not isinstance(x, tuple) for x in elems):
            raise TypeError('input introduced non-tuple element(s)')

    @staticmethod
    def _check_tuplelen(elems: list[ElemNDT]) -> int:
        """Check if all tuple elements in a list are of same length, and return the length.

        Parameters
        ----------
        elems : list

        Returns
        -------
        int

        Raises
        ------
        ValueError
            If the list contains tuple elements of different lengths.
        """
        len_elems = map(len, elems)
        if len(set(len_elems)) > 1:
            raise ValueError('all tuple elements must be of same length')
        return len(elems[0])

    @override
    def _validate_elements(self, elems: list[ElemNDT]) -> bool:
        """Validate all elements of a list.

        Validation includes the following checks:
        * If the list contains non-tuple element(s).
        * If all tuple elements are of the same length.

        Parameters
        ----------
        elems : list

        Returns
        -------
        bool

        Raises
        ------
        TypeError
            If the list contains non-tuple element(s).
        ValueError
            If the list contains tuple elements of different lengths.
        """
        self._check_alltuples(elems)

        if hasattr(self, '_tuplelen'):
            if self._tuplelen != self._check_tuplelen(elems):
                raise ValueError(
                    'input introduced tuple element(s) of different length (should be '
                    f'{self._tuplelen})'
                )
        else:
            self._tuplelen = self._check_tuplelen(elems)

        return True

    @override
    def _ensure_no_duplicates(self, elems: list[ElemNDT]) -> set[ElemNDT]:
        """Ensure that a list of elements has no duplicates and return a set of them.

        Parameters
        ----------
        elems : list

        Returns
        -------
        set

        Raises
        ------
        ValueError
            If the list of elements has any duplicates.

        Notes
        -----
        This method is called either when new elements are added to the IndexSet or when some of its
        elements are updated. Given that adding new elements will modify the IndexSet, we'll reset
        the following private attributes:
        (1) _index_groups : Clear this dict and reconstruct when the user calls `subset` or
            `squeeze`rather than defining a complicated logic to update it.
        """
        unique = super()._ensure_no_duplicates(elems)

        if self._index_groups:  # is pouplated
            self._index_groups.clear()

        return unique

    @override
    def _remove_elements(self, elems: list[ElemNDT]) -> None:
        """Remove elements from the IndexSet.

        Parameters
        ----------
        elems : list

        Notes
        -----
        Given that removing elements will modify the IndexSet, we'll reset the following private
        attributes:
        (1) `_index_groups`: Clear this dict and reconstruct when the user calls `subset` or
            `squeeze` rather than defining a complicated logic to update it.
        (2) `_tuplelen`: Delete this attribute if all elements are removed from the IndexSet and
            redefine when the user adds new elements.
        """
        super()._remove_elements(elems)

        if self._index_groups:  # is pouplated
            self._index_groups.clear()

        if not self._list:  # is empty
            del self._tuplelen

    @override
    def clear(self) -> None:
        """Remove all elements from the IndexSet."""
        # Notes
        # -----
        # Given that removing elements will modify the IndexSet, we'll reset the following private
        # attributes:
        # (1) `_index_groups`: Clear this dict and reconstruct when the user calls `subset` or
        #     `squeeze` rather than defining a complicated logic to update it.
        # (2) `_tuplelen`: Delete this attribute if all elements are removed from the IndexSet and
        #     redefine when the user adds new elements.

        super().clear()

        if self._index_groups:  # is pouplated
            self._index_groups.clear()

        try:
            del self._tuplelen
        except AttributeError:
            pass

    def _groupby(self, *indices: int) -> IndexGroup[ElemNDT]:
        """Group subsets of the IndexSet that correspond to given dimension indices.

        This method does not apply any validation checks and only includes the core logic of the
        functionality.

        Parameters
        ----------
        *indices : int
            Dimension indices i.e., position indices of N-dim to group.

        Returns
        -------
        defaultdict[tuple, list[tuple]]
            * Keys: Unique combinations of N-dim tuple element values at given dimension indices.
            * Values: Tuple elements corresponding to the keys, if any (or an empty list otherwise).

        Examples
        --------
        >>> triple = IndexSetND([('A', 0, 0), ('A', 1, 2), ('B', 1, 2)])

        Group by the first dimension index:

        >>> triple._groupby(0)
        defaultdict(<class 'list'>, {('A',): [('A', 0, 0), ('A', 1, 2)], ('B',): [('B', 1, 2)]})

        Group by the second and third dimension indices:

        >>> triple._groupby(1, 2)
        defaultdict(<class 'list'>, {(0, 0): [('A', 0, 0)], (1, 2): [('A', 1, 2), ('B', 1, 2)]})
        """
        # If index group is cached
        if indices in self._index_groups:
            return self._index_groups[indices]

        # Create new grouping otherwise, and cache for future use
        group: IndexGroup[ElemNDT] = defaultdict(list)
        if len(indices) == 1:
            for elem in self._list:
                group[(itemgetter(*indices)(elem),)].append(elem)
        else:
            for elem in self._list:
                group[itemgetter(*indices)(elem)].append(elem)
        self._index_groups[indices] = group

        return group

    def subset(self, *pattern: Any) -> list[ElemNDT]:
        """Get a subset of the IndexSet with a wildcard pattern.

        Parameters
        ----------
        *pattern : Any
            The pattern requires one value for each dimension of the N-dim tuple key. The
            single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        list

        Raises
        ------
        LookupError
            If the IndexSet is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple elements.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> triple = IndexSetND([(0, 7, 'A'), (0, 8, 'B'), (0, 9, 'B'), (1, 7, 'A'), (1, 8, 'B')])

        Select the subset having ``0`` at the first dimension index.

        >>> triple.subset(0, '*', '*')
        [(0, 7, 'A'), (0, 8, 'B'), (0, 9, 'B')]

        Select the subset having ``0`` at the first and ``'B'`` at the third dimension index:

        >>> triple.subset(0, '*', 'B')
        [(0, 8, 'B'), (0, 9, 'B')]
        """
        if not self._list:  # is empty
            raise LookupError(f'{self.__class__.__name__} is empty')

        if any((isinstance(v, Iterable) and not isinstance(v, str)) for v in pattern):
            raise TypeError('pattern values must be scalars (no iterables except string)')

        if len(pattern) != self._tuplelen:
            raise ValueError('pattern length must be the same as that of N-dim tuple elements')

        indices = tuple(i for i, v in enumerate(pattern) if v != '*')  # Wildcard filtering
        if len(indices) == 0:
            raise ValueError('pattern cannot have all wildcards')
        if len(indices) == self._tuplelen:
            raise ValueError('pattern cannot have no wildcards')

        given = tuple(v for v in pattern if v != '*')  # Wildcard filtering

        # Use get instead of __getitem__ because we don't want to update the defaultdict[list] (with
        # an empty list) for keys that are not preset prior to returning the empty list. Can
        # directly return an empty list with get instead.
        return self._groupby(*indices).get(given, list())

    @overload
    def squeeze(  # numpydoc ignore=GL08
        self, *indices: Unpack[tuple[int]], names: Sequence[str] | None = ...
    ) -> IndexSet1D[Any]: ...

    @overload
    def squeeze(  # numpydoc ignore=GL08
        self,
        *indices: Unpack[tuple[int, int, Unpack[tuple[int, ...]]]],
        names: Sequence[str] | None = ...,
    ) -> IndexSetND[tuple[Any, ...]]: ...

    def squeeze(
        self, *indices: int, names: Sequence[str] | None = None
    ) -> IndexSet1D[Any] | IndexSetND[tuple[Any, ...]]:
        """Squeeze the IndexSet for given dimension indices to get a new IndexSet.

        Parameters
        ----------
        *indices : int
            Dimension indices i.e., position indices of N-dim to squeeze.
        names : sequence[str], optional
            Names to refer to each dimension of the squeezed elements.

        Returns
        -------
        IndexSet1D or IndexSetND

        Raises
        ------
        LookupError
            If the IndexSet is empty.
        ValueError
            If no dimension index is given or all dimension indices are given.
        ValueError
            If any dimension index is invalid (exceeds the length of N-dim tuple element).
        ValueError
            If the `names` sequence has multiple elements when squeezing for one dimension index.

        Examples
        --------
        >>> triple = IndexSetND([('A', 0, 0), ('A', 1, 2), ('B', 1, 2)])

        Squeeze for the first dimension index:

        >>> triple.squeeze(0, names=['letter'])
        IndexSet1D: (letter)
        ['A', 'B']

        Squeeze for the second and third dimension indices:

        >>> triple.squeeze(1, 2, names=['one', 'two'])
        IndexSetND: (one, two)
        [(0, 0), (1, 2)]
        """
        # Error checks only if method called externally
        if not self._list:  # is empty
            raise LookupError(f'{self.__class__.__name__} is empty')

        if not all(isinstance(idx, int) for idx in indices):
            raise TypeError('dimension indices should be integers')
        if len(indices) == 0:
            raise ValueError('dimension indices are required')
        invalid = [idx for idx in indices if idx not in range(self._tuplelen)]
        if invalid:
            raise ValueError(
                f'dimension indices {invalid} are invalid.. {self.__class__.__name__} has elements '
                f'of length {self._tuplelen}'
            )
        if len(indices) == self._tuplelen:
            raise ValueError(
                '`squeeze` does not work with all dimension indices; use the '
                f'{self.__class__.__name__} directly'
            )

        grouped = self._groupby(*indices)

        # if multiple indices, encapsulate in IndexSetND
        if len(indices) > 1:
            return IndexSetND(grouped, names=names)

        # if only one index, encapsulate in IndexSet1D
        if names:
            if len(names) > 1:
                raise ValueError(
                    '`names` should have only one name when squeezing for one dimension index'
                )
            name = names[0]
        else:
            name = None

        return IndexSet1D((key[0] for key in grouped), name=name)

    # Overriding `__new__` for this class causes `inspect.signature` to return the signature of
    # `__new__` for this class (instead of `__init__`). This side-effect leads to an incorrect
    # call signature and return annotation output when calling `help` function for this class.
    # So we amend it by defining `__signature__`.
    __signature__ = inspect.Signature(
        parameters=list(inspect.signature(__init__).parameters.values())[1:],  # skip `self` arg
        return_annotation=inspect.signature(__init__).return_annotation,
    )


# Register as virtual subclass of collections.abc.MutableSequence
MutableSequence.register(IndexSet1D)
MutableSequence.register(IndexSetND)
