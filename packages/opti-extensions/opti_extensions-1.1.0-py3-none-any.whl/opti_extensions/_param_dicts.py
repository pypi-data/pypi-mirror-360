# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""ParamDict data structures."""

from __future__ import annotations

import statistics
from collections import abc
from collections.abc import Callable, Iterable, MutableMapping, Sequence
from functools import partial
from typing import Any, Literal, NoReturn, TypeVar, cast, overload

from ._dict_mixins import DefaultT, Dict1DMixin, DictBaseMixin, DictNDMixin
from ._index_sets import Elem1DT, ElemNDT, ElemT, IndexSet1D, IndexSetBase, IndexSetND

ParamT = TypeVar('ParamT', bound=int | float)


class _RAISE_KEYERROR:
    __slots__ = ()


_raise_keyerror = _RAISE_KEYERROR()


_builtin_op: dict[str, Callable[..., int | float]] = {
    'sum': sum,
    'min': partial(min, default=0),
    'max': partial(max, default=0),
}


class ParamDictBase(dict[ElemT, ParamT], DictBaseMixin[ElemT, ParamT]):
    """Base class for custom subclasses of `dict` to define parameters.

    Provides runtime type checks to ensure parameter values are `int` or `float`.

    Parameters
    ----------
    mapping : dict or dict-like mapping, optional
        Input data to be encapsulated in the ParamDict.
    indexset : IndexSetBase
        Keys of mapping encapsulated in an IndexSet.
    """

    # Private attributes
    # ------------------
    # _indexset : IndexSetBase
    #     Index-set of keys.

    __slots__ = ('_indexset',)

    def __init__(
        self, mapping: MutableMapping[ElemT, ParamT], /, *, indexset: IndexSetBase[ElemT]
    ) -> None:
        if any(not self._is_valid_value_type(x) for x in mapping.values()):
            raise TypeError("input mapping's values should be either int or float")

        self._indexset = indexset
        """Index-set of keys."""

        super().__init__(mapping)

    @staticmethod
    def _is_valid_value_type(value: ParamT) -> bool:
        """Check if the type of a value is valid (either int or float) or not.

        Parameters
        ----------
        value : Any

        Returns
        -------
        bool
        """
        return isinstance(value, int | float)

    def __setitem__(self, key: ElemT, value: ParamT, /) -> None:
        # Set `self[key]` to `value`.
        if self._is_valid_value_type(value):
            if key in self._indexset:
                super().__setitem__(key, value)
            else:
                try:
                    self._indexset.append(key)
                    super().__setitem__(key, value)
                except Exception as exc:
                    self._reraise_exc_from_indexset(exc)
        else:
            raise TypeError('`value` should be either int or float')

    def __delitem__(self, key: ElemT, /) -> None:
        # Remove `self[key]`.
        super().__delitem__(key)
        self._indexset.remove(key)

    def clear(self) -> None:
        """Remove all items from the ParamDict."""
        super().clear()
        self._indexset.clear()

    def copy(self) -> NoReturn:
        """Not supported by ParamDict."""
        self._raise_not_supported_err('copy')

    @overload
    def get(self, key: ElemT, default: None = ..., /) -> ParamT | None: ...  # numpydoc ignore=GL08

    @overload
    def get(self, key: ElemT, default: ParamT = ..., /) -> ParamT: ...  # numpydoc ignore=GL08

    @overload
    def get(
        self, key: ElemT, default: DefaultT = ..., /
    ) -> ParamT | DefaultT: ...  # numpydoc ignore=GL08

    def get(self, key: ElemT, default: DefaultT | None = None, /) -> ParamT | DefaultT | None:
        """Get the parameter value for the specified key, or the default if not found.

        Parameters
        ----------
        key : key
        default : Any, optional

        Returns
        -------
        int or float or ``default``
        """
        return super().get(key, default)

    @overload
    def pop(self, key: ElemT, /) -> ParamT: ...  # numpydoc ignore=GL08

    @overload
    def pop(
        self, key: ElemT, default: DefaultT, /
    ) -> ParamT | DefaultT: ...  # numpydoc ignore=GL08

    def pop(
        self, key: ElemT, default: DefaultT | _RAISE_KEYERROR = _raise_keyerror, /
    ) -> ParamT | DefaultT:
        """Remove the specified key and return it's parameter value, or the default if not found.

        Parameters
        ----------
        key : key
        default : int or float, optional

        Returns
        -------
        int or float or ``default``

        Raises
        ------
        KeyError
            If key not found in the ParamDict.
        """
        if key in self:
            self._indexset.remove(key)
        if isinstance(default, _RAISE_KEYERROR):
            return super().pop(key)
        else:
            return super().pop(key, default)

    def popitem(self) -> tuple[ElemT, ParamT]:
        """Remove and return the last inserted key and parameter value pair from the ParamDict.

        Returns
        -------
        (key, int or float)
            Tuple of key, parameter value.
        """
        item = super().popitem()
        self._indexset.remove(item[0])
        return item

    def setdefault(self, key: ElemT, default: ParamT, /) -> ParamT:
        """Get the parameter value for the specified key, or the default if not found.

        If the key is not found, insert it with the parameter value of default in the ParamDict.

        Parameters
        ----------
        key : key
        default : int or float

        Returns
        -------
        int or float
        """
        if self._is_valid_value_type(default):
            if key not in self._indexset:
                try:
                    self._indexset.append(key)
                except Exception as exc:
                    self._reraise_exc_from_indexset(exc)
            return super().setdefault(key, default)
        raise TypeError('`default` should be either int or float')

    def update(self, *args: Any, **kwargs: Any) -> NoReturn:
        """Not supported by ParamDict."""
        self._raise_not_supported_err('update')

    @classmethod
    def fromkeys(cls, keys: Any, value: Any = None, /) -> NoReturn:
        """Not supported by ParamDict."""
        raise AttributeError(f'`fromkeys` is not supported by {cls.__name__}')

    def _check_for_calc_stat(self, stat_func: str) -> None:
        """Perform validation checks before calculating a statistic with parameter values.

        Parameters
        ----------
        stat_func : str
            Either `'sum'`, `'min'`, `'max'` or the name of the statistical function from the
            `statistics` module of the standard library.

        Raises
        ------
        ValueError
            If `stat_func` not found in the `statistics` module.
        StatisticsError
            If the ParamDict is empty.
        """
        if stat_func not in ('sum', 'min', 'max') and not hasattr(statistics, stat_func):
            raise ValueError('Given `stat_func` not found in the `statistics` module')
        if not self:
            raise statistics.StatisticsError(
                'Cannot calculate `%s` as the ParamDict is empty', stat_func
            )

    def _calc_stat_all(self, stat_func: str) -> int | float:
        """Calculate a statistic with all parameter values.

        Supports sum, min, max, and any statistical function provided in the `statistics` module of
        the standard library.

        Parameters
        ----------
        stat_func : str
            Either `'sum'`, `'min'`, `'max'` or the name of the statistical function from the
            `statistics` module of the standard library.

        Returns
        -------
        int or float
        """
        if stat_func in ('sum', 'min', 'max'):
            res: int | float = _builtin_op[stat_func](self.values())
        else:
            res = getattr(statistics, stat_func)(self.values())

        return res


class ParamDict1D(ParamDictBase[Elem1DT, ParamT], Dict1DMixin[Elem1DT, ParamT]):
    """Custom subclass of `dict` to define parameters with 1-dim scalar keys.

    Requires all keys to be unique scalars (such as `int`, `str`, `pd.Timestamp`, etc.) and all
    values to be `int` or `float`.

    Parameters
    ----------
    mapping : dict or dict-like mapping, optional
        Input data to be encapsulated in the ParamDict.
    key_name : str, optional
        Name to refer to 1-dim scalar keys - not used internally, and solely for user reference.
    value_name : str, optional
        Name to refer to parameter values - not used internally, and solely for user reference.

    Raises
    ------
    TypeError
        If input includes key(s) that are not scalar (any iterable except string).
    TypeError
        If input includes value(s) that are not int or float.

    See Also
    --------
    ParamDictND : For N-dim tuple keys.

    Examples
    --------
    Constructing empty to populate later:

    >>> ParamDict1D()
    ParamDict1D:
    {}

    Constructing with a mapping:

    >>> ParamDict1D(
    ...     {'JAN': 31, 'FEB': 28, 'MAR': 31},
    ...     key_name='MONTH',
    ...     value_name='DAYS',
    ... )
    ParamDict1D: MONTH -> DAYS
    {'JAN': 31, 'FEB': 28, 'MAR': 31}
    """

    # Private attributes
    # ------------------
    # _indexset : IndexSet1D
    #     Index-set of 1-dim scalar keys.

    __slots__ = ('_key_name', '_value_name')

    def __init__(
        self,
        mapping: MutableMapping[Elem1DT, ParamT] | None = None,
        /,
        *,
        key_name: str | None = None,
        value_name: str | None = None,
    ) -> None:
        self.key_name = key_name
        self.value_name = value_name

        if mapping is None:
            mapping = {}
            self._indexset: IndexSet1D[Elem1DT] = IndexSet1D(name=self.key_name)
            """Index-set of 1-dim scalar keys."""
        else:
            if not isinstance(mapping, abc.MutableMapping):
                raise TypeError('input should be a dict or dict-like mapping')
            try:
                self._indexset = IndexSet1D(mapping, name=self.key_name)
            except Exception as exc:
                self._reraise_exc_from_indexset(exc, caller='IndexSet1D')

        super().__init__(mapping, indexset=self._indexset)

    def __repr__(self) -> str:
        # Printable string representation.
        return f'{self._get_repr_header()}\n{super().__repr__()}'

    def _repr_pretty_(self, p, cycle: bool) -> None:  # type: ignore[no-untyped-def]
        # Pretty repr for IPython.
        # https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#extending
        # Since IPython is not typed, we'll add a type ignore comment here
        # The annotation for arg `p` is `IPython.lib.pretty.RepresentationPrinter`
        p.text(f'{self._get_repr_header()}\n')
        p.pretty(dict(self))

    def lookup(self, key: Elem1DT) -> ParamT | Literal[0]:
        """Get the parameter value for the specified key, or zero if it is not found.

        Parameters
        ----------
        key : key

        Returns
        -------
        int or float

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.lookup('chair')
        100
        >>> inventory.lookup('desk')
        0
        """
        return super().get(key, 0)

    def _calc_stat(self, stat_func: str) -> int | float:
        """Calculate a statistic with all parameter values.

        Supports sum, min, max, and any statistical function provided in the `statistics` module of
        the standard library.

        Parameters
        ----------
        stat_func : str
            Either `'sum'`, `'min'`, `'max'` or the name of the statistical function from the
            `statistics` module of the standard library.

        Returns
        -------
        int or float

        Raises
        ------
        ValueError
            If `stat_func` not found in the `statistics` module.
        StatisticsError
            If the ParamDict is empty.
        """
        self._check_for_calc_stat(stat_func)
        res = self._calc_stat_all(stat_func)

        return res

    def sum(self) -> int | float:
        """Calculate the sum of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.sum()
        118
        """
        return self._calc_stat('sum')

    def min(self) -> int | float:
        """Calculate the minimum of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.min()
        3
        """
        return self._calc_stat('min')

    def max(self) -> int | float:
        """Calculate the maximum of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.max()
        100
        """
        return self._calc_stat('max')

    def mean(self) -> int | float:
        """Calculate the mean of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.mean()
        29.5
        """
        return self._calc_stat('mean')

    def median(self) -> int | float:
        """Calculate the median of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.median()
        7.5
        """
        return self._calc_stat('median')

    def median_high(self) -> int | float:
        """Calculate the high median of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.median_high()
        10
        """
        return self._calc_stat('median_high')

    def median_low(self) -> int | float:
        """Calculate the low median of parameter values.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.

        Examples
        --------
        >>> inventory = ParamDict1D({'chair': 100, 'table': 10, 'shelf': 5, 'sofa': 3})
        >>> inventory.median_low()
        5
        """
        return self._calc_stat('median_low')


class ParamDictND(ParamDictBase[ElemNDT, ParamT], DictNDMixin[ElemNDT, ParamT]):
    """Custom subclass of `dict` to define parameters with N-dim tuple keys.

    Requires all keys to be unique tuples of the same length, each containing 'N' scalars (such as
    `int`, `str`, `pd.Timestamp`, etc.) and all values to be `int` or `float`.

    Parameters
    ----------
    mapping : dict or dict-like mapping, optional
        Input data to be encapsulated in the ParamDict.
    key_names : sequence[str], optional
        Names to refer to each dimension of N-dim tuple keys - not used internally but solely for
        user reference.
    value_name : str, optional
        Name to refer to parameter values - not used internally, and solely for user reference.

    Raises
    ------
    TypeError
        If input includes key(s) that are not tuples.
    ValueError
        If input includes tuple keys of different lengths.
    TypeError
        If input includes values that are not int or float.

    See Also
    --------
    ParamDict1D : For 1-dim scalar keys.

    Examples
    --------
    Constructing empty to populate later:

    >>> ParamDictND()
    ParamDictND:
    {}

    Constructing with a mapping:

    >>> ParamDictND(
    ...     {('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15},
    ...     key_names=('ORI', 'DES'),
    ...     value_name='DEMAND',
    ... )
    ParamDictND: (ORI, DES) -> DEMAND
    {('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15}
    """

    # Private attributes
    # ------------------
    # _indexset : IndexSetND
    #     Index-set of N-dim tuple keys.

    __slots__ = ('_key_names', '_value_name')

    def __init__(
        self,
        mapping: MutableMapping[ElemNDT, ParamT] | None = None,
        /,
        *,
        key_names: Sequence[str] | None = None,
        value_name: str | None = None,
    ) -> None:
        self.key_names = key_names
        self.value_name = value_name

        if mapping is None:
            mapping = {}
            self._indexset = cast('IndexSetND[ElemNDT]', IndexSetND(names=self.key_names))
            """Index-set of N-dim tuple keys."""
        else:
            if not isinstance(mapping, abc.MutableMapping):
                raise TypeError('input should be a dict or dict-like mapping')
            try:
                self._indexset = IndexSetND(mapping, names=self.key_names)
            except Exception as exc:
                self._reraise_exc_from_indexset(exc, caller='IndexSetND')

        super().__init__(mapping, indexset=self._indexset)

    def __repr__(self) -> str:
        # Printable string representation.
        return f'{self._get_repr_header()}\n{super().__repr__()}'

    def _repr_pretty_(self, p, cycle: bool) -> None:  # type: ignore[no-untyped-def]
        # Pretty repr for IPython.
        # https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#extending
        # Since IPython is not typed, we'll add a type ignore comment here
        # The annotation for arg `p` is `IPython.lib.pretty.RepresentationPrinter`
        p.text(f'{self._get_repr_header()}\n')
        p.pretty(dict(self))

    def lookup(self, *key: Any) -> ParamT | Literal[0]:
        """Get the parameter value for the specified key, or zero if it is not found.

        Parameters
        ----------
        *key : key

        Returns
        -------
        int or float

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})
        >>> demand.lookup('A', 'B')
        10
        >>> demand.lookup('B', 'A')
        0
        """
        if any((isinstance(k, Iterable) and not isinstance(k, str)) for k in key):
            raise TypeError('lookup key must be scalars (no iterables except string)')
        if len(key) != self._indexset._tuplelen:
            raise ValueError('lookup key length must be the same as that of N-dim tuple keys')
        return super().get(cast('ElemNDT', key), 0)

    def _calc_stat(self, *pattern: Any, stat_func: str) -> int | float:
        """Calculate a statistic with all parameter values or a subset based on wildcard pattern.

        Supports sum, min, max, and any statistical function provided in the `statistics` module of
        the standard library.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.
        stat_func : str
            Either `'sum'`, `'min'`, `'max'` or the name of the statistical function from the
            `statistics` module of the standard library.

        Returns
        -------
        int or float

        Raises
        ------
        ValueError
            If `stat_func` not found in the `statistics` module.
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.
        """
        self._check_for_calc_stat(stat_func)
        if stat_func in ('sum', 'min', 'max') and pattern:
            res: int | float = _builtin_op[stat_func](self.subset_values(*pattern))
        elif pattern:
            try:
                res = getattr(statistics, stat_func)(self.subset_values(*pattern))
            except statistics.StatisticsError:
                res = 0
        else:
            res = self._calc_stat_all(stat_func)

        return res

    def sum(self, *pattern: Any) -> int | float:
        """Calculate the sum of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Sum of all parameter values:

        >>> demand.sum()
        61

        Sum of a subset based on wildcard pattern:

        >>> demand.sum('A', '*')
        25
        >>> demand.sum('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='sum')

    def min(self, *pattern: Any) -> int | float:
        """Calculate the minimum of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Minimum of all parameter values:

        >>> demand.min()
        10

        Minimum of a subset based on wildcard pattern:

        >>> demand.min('A', '*')
        10
        >>> demand.min('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='min')

    def max(self, *pattern: Any) -> int | float:
        """Calculate the maximum of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Maximum of all parameter values:

        >>> demand.max()
        20

        Maximum of a subset based on wildcard pattern:

        >>> demand.max('A', '*')
        15
        >>> demand.max('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='max')

    def mean(self, *pattern: Any) -> int | float:
        """Calculate the mean of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Mean of all parameter values:

        >>> demand.mean()
        15.25

        Mean of a subset based on wildcard pattern:

        >>> demand.mean('A', '*')
        12.5
        >>> demand.mean('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='mean')

    def median(self, *pattern: Any) -> int | float:
        """Calculate the median of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Median of all parameter values:

        >>> demand.median()
        15.5

        Median of a subset based on wildcard pattern:

        >>> demand.median('A', '*')
        12.5
        >>> demand.median('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='median')

    def median_high(self, *pattern: Any) -> int | float:
        """Calculate the high median of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        High median of all parameter values:

        >>> demand.median_high()
        16

        High median of a subset based on wildcard pattern:

        >>> demand.median_high('A', '*')
        15
        >>> demand.median_high('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='median_high')

    def median_low(self, *pattern: Any) -> int | float:
        """Calculate the low median of all parameter values or a subset based on wildcard pattern.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        int or float

        Raises
        ------
        StatisticsError
            If the ParamDict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        >>> demand = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20, ('A', 'C'): 15, ('C', 'A'): 16})

        Low median of all parameter values:

        >>> demand.median_low()
        15

        Low median of a subset based on wildcard pattern:

        >>> demand.median_low('A', '*')
        10
        >>> demand.median_low('*', 'A')
        16
        """
        return self._calc_stat(*pattern, stat_func='median_low')
