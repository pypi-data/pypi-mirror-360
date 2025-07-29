# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Common methods for custom dict subclasses having IndexSet keys."""

from __future__ import annotations

from collections import abc
from collections.abc import Sequence
from operator import itemgetter
from typing import Any, Generic, Literal, NoReturn, Protocol, TypeVar

from ._index_sets import Elem1DT, ElemNDT, ElemT, IndexSetBase, IndexSetND

_KT_contra = TypeVar('_KT_contra', contravariant=True)
_VT_co = TypeVar('_VT_co', covariant=True)


class SupportsGetItem(Protocol[_KT_contra, _VT_co]):
    def __contains__(self, __x: Any) -> bool: ...
    def __getitem__(self, __key: _KT_contra) -> _VT_co: ...


ValT = TypeVar('ValT')
DefaultT = TypeVar('DefaultT')


class DictBaseMixin(Generic[ElemT, ValT]):
    """Base mixin class to define common methods for `dict` subclasses."""

    _indexset: IndexSetBase[ElemT]

    def _raise_not_supported_err(self, method_name: str) -> NoReturn:
        """Raise an attribute error for any unsupported method.

        Parameters
        ----------
        method_name : str
        """
        raise AttributeError(f'`{method_name}` is not supported by {self.__class__.__name__}')

    def _reraise_exc_from_indexset(
        self, exception: Exception, /, *, caller: Literal['IndexSet1D', 'IndexSetND'] | None = None
    ) -> NoReturn:
        """Do not cascade to indexset trace; modify it's exception message and spit it directly.

        Parameters
        ----------
        exception : Exception
        caller : str - "IndexSet1D" or "IndexSetND", optional
        """
        msg = exception.args[0]
        msg = msg.replace('element', 'key')
        try:
            msg = msg.replace(self._indexset.__class__.__name__, self.__class__.__name__)
        except AttributeError:
            if caller:
                msg = msg.replace(caller, self.__class__.__name__)
        raise exception.__class__(msg) from None


class Dict1DMixin(DictBaseMixin[Elem1DT, ValT]):
    """Mixin class to define common methods for `dict` subclasses with 1-dim scalar keys."""

    _key_name: str | None
    _value_name: str | None

    @property
    def key_name(self) -> str | None:
        """Name to refer to 1-dim scalar keys.

        Not used internally, and solely for user reference.

        Returns
        -------
        str
        """
        return self._key_name

    @key_name.setter
    def key_name(self, new: str | None) -> None:
        match new:
            case None | str():
                self._key_name = new
            case _:
                raise TypeError('`key_name` should be a string')

    @property
    def value_name(self) -> str | None:
        """Name to refer to Dict values.

        Not used internally, and solely for user reference.

        Returns
        -------
        str
        """
        return self._value_name

    @value_name.setter
    def value_name(self, new: str | None) -> None:
        match new:
            case None | str():
                self._value_name = new
            case _:
                raise TypeError('`value_name` should be a string')

    def _get_repr_header(self) -> str:
        # Header for repr.
        if self.key_name is not None and self.value_name is not None:
            return f'{self.__class__.__name__}: {self.key_name} -> {self.value_name}'
        else:
            return f'{self.__class__.__name__}:'


class DictNDMixin(DictBaseMixin[ElemNDT, ValT], SupportsGetItem[ElemNDT, ValT]):
    """Mixin class to define common methods for `dict` subclasses with N-dim scalar keys."""

    _key_names: Sequence[str] | None
    _value_name: str | None
    _indexset: IndexSetND[ElemNDT]

    @property
    def key_names(self) -> Sequence[str] | None:
        """Names to refer to each dimension of N-dim tuple keys.

        Not used internally, and solely for user reference.

        Returns
        -------
        sequence[str]
        """
        return self._key_names

    @key_names.setter
    def key_names(self, new: Sequence[str] | None) -> None:
        match new:
            case None:
                self._key_names = None
            case str():
                raise TypeError('`key_names` should be a sequence of strings')
            case abc.Sequence() if all(isinstance(name, str) for name in new):
                self._key_names = list(new)
            case _:
                raise TypeError('`key_names` should be a sequence of strings')

    @property
    def value_name(self) -> str | None:
        """Name to refer to Dict values.

        Not used internally, and solely for user reference.

        Returns
        -------
        str
        """
        return self._value_name

    @value_name.setter
    def value_name(self, new: str | None) -> None:
        match new:
            case None | str():
                self._value_name = new
            case _:
                raise TypeError('`value_name` should be a string')

    def _get_repr_header(self) -> str:
        # Header for repr.
        if self.key_names is not None and self.value_name is not None:
            return f'{self.__class__.__name__}: ({", ".join(self.key_names)}) -> {self.value_name}'
        else:
            return f'{self.__class__.__name__}:'

    def subset_keys(self, *pattern: Any) -> list[ElemNDT]:
        """Get a subset of the N-dim tuple keys of the Dict with a wildcard pattern.

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
            If the Dict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.
        """
        try:
            return self._indexset.subset(*pattern)
        except Exception as exc:
            self._reraise_exc_from_indexset(exc)

    def subset_values(self, *pattern: Any) -> list[ValT]:
        """Get Dict values for all keys that match the wildcard pattern.

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
            If the Dict is empty.
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.
        """
        keys = self.subset_keys(*pattern)
        match len(keys):
            case 0:
                res: list[ValT] = []
            case 1:
                res = [self[keys[0]]]
            case _:
                res = list(itemgetter(*keys)(self))

        return res
