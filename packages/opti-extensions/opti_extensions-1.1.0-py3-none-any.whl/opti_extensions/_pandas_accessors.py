# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Accessors to cast pandas Series/DataFrame/Index into IndexSet and ParamDict data structures."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ._index_sets import IndexSet1D, IndexSetND
from ._param_dicts import ParamDict1D, ParamDictND

if TYPE_CHECKING:
    from pandas import DataFrame, Index, Series


def _check_empty(pd_obj: Series[Any] | DataFrame | Index[Any]) -> None:
    """Raise a ValueError is a pandas object is empty.

    Parameters
    ----------
    pd_obj : Series or DataFrame or Index
    """
    if pd_obj.empty:
        raise ValueError(f'{pd_obj.__class__.__name__} is empty')


def _check_duplicate_idx(pd_obj: Series[Any] | DataFrame) -> None:
    """Raise a ValueError is a pandas object has duplicate index-label(s).

    Parameters
    ----------
    pd_obj : Series or DataFrame
    """
    if pd_obj.index.size > len(set(pd_obj.index)):
        raise ValueError(f'{pd_obj.__class__.__name__} has duplicate index-label(s)')


class DataFrameAccessor:
    """Accessor to cast pandas DataFrame into IndexSet1D/IndexSetND and ParamDict1D/ParamDictND.

    Parameters
    ----------
    df : DataFrame
    """

    def __init__(self, df: DataFrame):
        _check_empty(df)
        self._df = df

    def to_indexset(self) -> IndexSet1D[Any] | IndexSetND[tuple[Any, ...]]:
        """Cast a DataFrame into an IndexSet1D/IndexSetND.

        Note: The `opti-extensions` package has to be imported first to use this method with
        `pandas`.

        Returns
        -------
        IndexSet1D or IndexSetND
            * A single-column DataFrame will be cast into an IndexSet1D consisting of its column
              values. The column name will be set as the `IndexSet1D.name` attribute (as str).
            * A multi-column DataFrame will be cast into an IndexSetND consisting of tuples, each
              containing row values. The column names will be set as the `IndexSetND.names`
              attribute (as list[str]).

        Raises
        ------
        ValueError
            If the DataFrame is empty.
        TypeError
            If the DataFrame has non-scalar value(s) (any iterable except string).
        ValueError
            If the DataFrame has duplicate rows.

        See Also
        --------
        pandas.Series.opti.to_indexset : Cast a Series into an IndexSet1D.
        pandas.Index.opti.to_indexset : Cast an Index into an IndexSet1D/IndexSetND.

        Examples
        --------
        >>> import pandas as pd
        >>> import opti_extensions  # required to access this method

        Casting a single-column DataFrame into an IndexSet1D

        >>> warehouses = pd.DataFrame(['WH-A', 'WH-B', 'WH-C'], columns=['WAREHOUSE'])
        >>> warehouses
          WAREHOUSE
        0      WH-A
        1      WH-B
        2      WH-C

        >>> warehouses.opti.to_indexset()
        IndexSet1D: (WAREHOUSE)
        ['WH-A', 'WH-B', 'WH-C']

        Casting a multi-column DataFrame into an IndexSetND

        >>> df = pd.DataFrame(
        ...     {
        ...         'PRODUCT': ['chair', 'chair', 'desk', 'desk'],
        ...         'WAREHOUSE': ['WH-A', 'WH-B', 'WH-B', 'WH-C'],
        ...         'PERIOD': [0, 1, 0, 1],
        ...     }
        ... )
        >>> df
          PRODUCT WAREHOUSE  PERIOD
        0   chair      WH-A       0
        1   chair      WH-B       1
        2    desk      WH-B       0
        3    desk      WH-C       1

        >>> df.opti.to_indexset()
        IndexSetND: (PRODUCT, WAREHOUSE, PERIOD)
        [('chair', 'WH-A', 0),
         ('chair', 'WH-B', 1),
         ('desk', 'WH-B', 0),
         ('desk', 'WH-C', 1)]

        >>> df.set_index('WAREHOUSE')[['PRODUCT', 'PERIOD']].opti.to_indexset()
        IndexSetND: (PRODUCT, PERIOD)
        [('chair', 0),
         ('chair', 1),
         ('desk', 0),
         ('desk', 1)]
        """
        if self._df.columns.size > 1:  # multi-column df
            vals_to_check = (
                self._df.select_dtypes(exclude=['number', 'datetime', 'datetimetz', 'timedelta'])
                .to_numpy()
                .flat
            )
            if any(isinstance(i, Iterable) and not isinstance(i, str) for i in vals_to_check):
                raise TypeError('DataFrame has non-scalar value(s) (no iterables except string)')

            names = (
                None
                if any(x is None for x in self._df.columns)
                else list(map(str, self._df.columns))
            )
            return IndexSetND(self._df.to_records(index=False).tolist(), names=names)

        else:  # single-column df
            return IndexSet1D(self._df.iloc[:, 0].tolist(), name=str(self._df.columns[0]))

    def to_paramdict(
        self,
    ) -> ParamDict1D[Any, int | float] | ParamDictND[tuple[Any, ...], int | float]:
        """Cast a single-column DataFrame into a ParamDict1D/ParamDictND.

        Note: The `opti-extensions` package has to be imported first to use this method with
        `pandas`.

        Returns
        -------
        ParamDict1D or ParamDictND
            * A single-index, single-column DataFrame will be cast into a ParamDict1D having index
              label as keys and column values as values. The index name will be set as the
              `ParamDict1D.key_name` attribute (as str). The column name will be set as the
              `ParamDict1D.value_name` attribute (as str).
            * A multi-index, single-column DataFrame will be cast into a ParamDictND having tuple of
              index labels as keys and column values as values. The multi-index names will be set as
              the `ParamDictND.key_names` attribute (as list[str]). The column name will be set as
              the `ParamDict1D.value_name` attribute (as str).

        Raises
        ------
        ValueError
            If the DataFrame is empty.
        ValueError
            If the DataFrame has multiple columns.
        ValueError
            If the DataFrame has duplicate index label(s).
        TypeError
            If the DataFrame has index label(s) that are not scalar (any iterable except string).
        TypeError
            If the DataFrame column values are not int or float.

        See Also
        --------
        pandas.Series.opti.to_paramdict : Cast a Series into a ParamDict1D/ParamDictND.

        Examples
        --------
        >>> import pandas as pd
        >>> import opti_extensions  # required to access this method

        Casting a single-index, single-column DataFrame into a ParamDict1D

        >>> inventory = pd.DataFrame({'PRODUCT': ['chair', 'desk'], 'UNITS': [200, 500]})
        >>> inventory
          PRODUCT  UNITS
        0   chair    200
        1    desk    500
        >>> inventory_units = inventory.set_index('PRODUCT')
        >>> inventory_units
                 UNITS
        PRODUCT
        chair      200
        desk       500

        >>> inventory_units.opti.to_paramdict()
        ParamDict1D: PRODUCT -> UNITS
        {'chair': 200, 'desk': 500}

        Casting a multi-index, single-column DataFrame into a ParamDictND

        >>> routes = pd.DataFrame(
        ...     {
        ...         'ORI': ['Delhi', 'Delhi', 'Seattle', 'Tokyo'],
        ...         'DES': ['Seattle', 'Tokyo', 'Tokyo', 'Delhi'],
        ...         'DIST': [11303, 5836, 7695, 5830],
        ...     }
        ... )
        >>> routes
               ORI      DES   DIST
        0    Delhi  Seattle  11303
        1    Delhi    Tokyo   5836
        2  Seattle    Tokyo   7695
        3    Tokyo    Delhi   5830
        >>> routes_dist = routes.set_index(['ORI', 'DES'])
        >>> routes_dist
                          DIST
        ORI     DES
        Delhi   Seattle  11303
                Tokyo     5836
        Seattle Tokyo     7695
        Tokyo   Delhi     5830

        >>> routes_dist.opti.to_paramdict()
        ParamDictND: (ORI, DES) -> DIST
        {('Delhi', 'Seattle'): 11303,
         ('Delhi', 'Tokyo'): 5836,
         ('Seattle', 'Tokyo'): 7695,
         ('Tokyo', 'Delhi'): 5830}
        """
        _check_duplicate_idx(self._df)

        if self._df.columns.size == 1:  # single-column df
            if self._df.index.nlevels > 1:  # multi-level index
                key_names = (
                    None
                    if any(x is None for x in self._df.index.names)
                    else list(map(str, self._df.index.names))
                )
                return ParamDictND(
                    self._df.iloc[:, 0].to_dict(),
                    key_names=key_names,
                    value_name=str(self._df.columns[0]),
                )

            else:  # single-level index
                key_name = None if self._df.index.name is None else str(self._df.index.name)
                return ParamDict1D(
                    self._df.iloc[:, 0].to_dict(),
                    key_name=key_name,
                    value_name=str(self._df.columns[0]),
                )

        else:  # multi-column df
            raise ValueError('`to_paramdict` does not support multi-column DataFrame')


class SeriesAccessor:
    """Accessor to cast pandas Series into IndexSet1D and ParamDict1D/ParamDictND.

    Parameters
    ----------
    series : Series
    """

    def __init__(self, series: Series[Any]):
        _check_empty(series)
        self._series = series

    def to_indexset(self) -> IndexSet1D[Any]:
        """Cast a Series into an IndexSet1D.

        Note: The `opti-extensions` package has to be imported first to use this method with
        `pandas`.

        Returns
        -------
        IndexSet1D
            * A Series will be cast into an IndexSet1D consisting of its values. The Series name
              will be set as the IndexSet1D.name attribute (as str).

        Raises
        ------
        ValueError
            If the Series is empty.
        TypeError
            If the Series has non-scalar value(s) (any iterable except string).
        ValueError
            If the Series has duplicate values.

        See Also
        --------
        pandas.DataFrame.opti.to_indexset : Cast a DataFrame into an IndexSet1D/IndexSetND.
        pandas.Index.opti.to_indexset : Cast an Index into an IndexSet1D/IndexSetND.

        Examples
        --------
        >>> import pandas as pd
        >>> import opti_extensions  # required to access this method

        Casting a Series into an IndexSet1D:

        >>> cities = pd.Series(['Delhi', 'Seattle', 'Tokyo'], name='CITY')
        >>> cities
        0      Delhi
        1    Seattle
        2      Tokyo
        Name: CITY, dtype: object

        >>> cities.opti.to_indexset()
        IndexSet1D: (CITY)
        ['Delhi', 'Seattle', 'Tokyo']
        """
        name = None if self._series.name is None else str(self._series.name)
        return IndexSet1D(self._series, name=name)

    def to_paramdict(
        self,
    ) -> ParamDict1D[Any, int | float] | ParamDictND[tuple[Any, ...], int | float]:
        """Cast a Series into a ParamDict1D/ParamDictND.

        Note: The `opti-extensions` package has to be imported first to use this method with
        `pandas`.

        Returns
        -------
        ParamDict1D or ParamDictND
            * A single-index Series will be cast into a ParamDict1D having index label as keys and
              Series values as values. The index name will be set as the `ParamDict1D.key_name`
              attribute (as str). The Series name will be set as the `ParamDict1D.value_name`
              attribute (as str).
            * A multi-index Series will be cast into a ParamDictND having tuple of index labels as
              keys and Series values as values. The multi-index names will be set as the
              `ParamDictND.key_names` attribute (as list[str]). The Series name will be set as the
              `ParamDict1D.value_name` attribute (as str).

        Raises
        ------
        ValueError
            If the Series is empty.
        ValueError
            If the Series has duplicate index label(s).
        TypeError
            If the Series has index label(s) that are not scalar (any iterable except string).
        TypeError
            If the Series values are not int or float.

        See Also
        --------
        pandas.DataFrame.opti.to_paramdict : Cast a single-column DataFrame into a ParamDict1D/
            ParamDictND.

        Examples
        --------
        >>> import pandas as pd
        >>> import opti_extensions  # required to access this method

        Casting a single-index Series into a ParamDict1D

        >>> inventory = pd.DataFrame({'PRODUCT': ['chair', 'desk'], 'UNITS': [200, 500]})
        >>> inventory
          PRODUCT  UNITS
        0   chair    200
        1    desk    500
        >>> inventory_units = inventory.set_index('PRODUCT')
        >>> inventory_units
                 UNITS
        PRODUCT
        chair      200
        desk       500

        >>> inventory_units.UNITS.opti.to_paramdict()
        ParamDict1D: PRODUCT -> UNITS
        {'chair': 200, 'desk': 500}

        Casting a multi-index Series into a ParamDictND

        >>> routes = pd.DataFrame(
        ...     {
        ...         'ORI': ['Delhi', 'Delhi', 'Seattle', 'Tokyo'],
        ...         'DES': ['Seattle', 'Tokyo', 'Tokyo', 'Delhi'],
        ...         'DIST': [11303, 5836, 7695, 5830],
        ...     }
        ... )
        >>> routes
               ORI      DES   DIST
        0    Delhi  Seattle  11303
        1    Delhi    Tokyo   5836
        2  Seattle    Tokyo   7695
        3    Tokyo    Delhi   5830
        >>> routes_dist = routes.set_index(['ORI', 'DES'])
        >>> routes_dist
                          DIST
        ORI     DES
        Delhi   Seattle  11303
                Tokyo     5836
        Seattle Tokyo     7695
        Tokyo   Delhi     5830

        >>> routes_dist.DIST.opti.to_paramdict()
        ParamDictND: (ORI, DES) -> DIST
        {('Delhi', 'Seattle'): 11303,
         ('Delhi', 'Tokyo'): 5836,
         ('Seattle', 'Tokyo'): 7695,
         ('Tokyo', 'Delhi'): 5830}
        """
        _check_duplicate_idx(self._series)

        value_name = None if self._series.name is None else str(self._series.name)

        if self._series.index.nlevels > 1:  # multi-level index
            key_names = (
                None
                if any(x is None for x in self._series.index.names)
                else list(map(str, self._series.index.names))
            )
            return ParamDictND(self._series.to_dict(), key_names=key_names, value_name=value_name)

        else:  # single-level index
            key_name = None if self._series.index.name is None else str(self._series.index.name)
            return ParamDict1D(self._series.to_dict(), key_name=key_name, value_name=value_name)


class IndexAccessor:
    """Accessor to cast pandas Index into IndexSet1D/IndexSetND.

    Parameters
    ----------
    idx : Index
    """

    def __init__(self, idx: Index[Any]):
        _check_empty(idx)
        self._idx = idx

    def to_indexset(self) -> IndexSet1D[Any] | IndexSetND[tuple[Any, ...]]:
        """Cast an Index into an IndexSet1D/IndexSetND.

        Note: The `opti-extensions` package has to be imported first to use this method with
        `pandas`.

        Returns
        -------
        IndexSet1D or IndexSetND
            * A single-level index will be cast into an IndexSet1D consisting of its values. The
              index name will be set as the `IndexSet1D.name` attribute (as str).
            * A multi-level index will be cast into an IndexSetND consisting of its values. The
              column names will be set as the `IndexSetND.names` attribute (as list[str]).

        Raises
        ------
        ValueError
            If the Index is empty.
        TypeError
            If the Index has non-scalar value(s) (any iterable except string).
        ValueError
            If the Index has duplicate values.

        See Also
        --------
        pandas.Series.opti.to_indexset : Cast a Series into an IndexSet1D.
        pandas.DataFrame.opti.to_indexset : Cast a DataFrame into an IndexSet1D/IndexSetND.

        Examples
        --------
        >>> import pandas as pd
        >>> import opti_extensions  # required to access this method

        Casting a DataFrame's single-level row index into an IndexSet1D:

        >>> warehouses = pd.DataFrame(
        ...     [10, 10, 5],
        ...     index=pd.Index(['WH-A', 'WH-B', 'WH-C'], name='WAREHOUSE'),
        ...     columns=['INVENTORY'],
        ... )
        >>> warehouses
                   INVENTORY
        WAREHOUSE
        WH-A              10
        WH-B              10
        WH-C               5

        >>> warehouses.index.opti.to_indexset()
        IndexSet1D: (WAREHOUSE)
        ['WH-A', 'WH-B', 'WH-C']

        Casting a DataFrame's multi-level row index into an IndexSetND:

        >>> warehouses = pd.DataFrame(
        ...     [10, 10, 5],
        ...     index=pd.MultiIndex.from_tuples(
        ...         [('EAST', 'WH-A'), ('EAST', 'WH-B'), ('WEST', 'WH-C')],
        ...         names=('ZONE', 'WAREHOUSE'),
        ...     ),
        ...     columns=['CAPACITY'],
        ... )
        >>> warehouses
                        CAPACITY
        ZONE WAREHOUSE
        EAST WH-A             10
             WH-B             10
        WEST WH-C              5

        >>> warehouses.index.opti.to_indexset()
        IndexSetND: (ZONE, WAREHOUSE)
        [('EAST', 'WH-A'), ('EAST', 'WH-B'), ('WEST', 'WH-C')]

        Casting a DataFrame's single-level column index into an IndexSet1D:

        >>> warehouses = pd.DataFrame(
        ...     {'WH-A': [10], 'WH-B': [10], 'WH-C': [5]}, index=['CAPACITY']
        ... ).rename_axis('WAREHOUSE', axis=1)
        >>> warehouses
        WAREHOUSE  WH-A  WH-B  WH-C
        CAPACITY     10    10     5

        >>> warehouses.columns.opti.to_indexset()
        IndexSet1D: (WAREHOUSE)
        ['WH-A', 'WH-B', 'WH-C']

        Casting a DataFrame's multi-level column index into an IndexSetND:

        >>> warehouses = pd.DataFrame(
        ...     {('EAST', 'WH-A'): [10], ('EAST', 'WH-B'): [10], ('WEST', 'WH-C'): [5]},
        ...     index=['CAPACITY'],
        ... ).rename_axis(('ZONE', 'WAREHOUSE'), axis=1)
        >>> warehouses
        ZONE      EAST      WEST
        WAREHOUSE WH-A WH-B WH-C
        CAPACITY    10   10    5

        >>> warehouses.columns.opti.to_indexset()
        IndexSetND: (ZONE, WAREHOUSE)
        [('EAST', 'WH-A'), ('EAST', 'WH-B'), ('WEST', 'WH-C')]

        Casting a Series' single-level index into an IndexSet1D:

        >>> cities = pd.Series(
        ...     ['A', 'B', 'C'],
        ...     index=pd.Index(['Delhi', 'Seattle', 'Tokyo'], name='CITY'),
        ...     name='ID',
        ... )
        >>> cities
        CITY
        Delhi      A
        Seattle    B
        Tokyo      C
        Name: ID, dtype: object

        >>> cities.index.opti.to_indexset()
        IndexSet1D: (CITY)
        ['Delhi', 'Seattle', 'Tokyo']

        Casting a Series' multi-level index into an IndexSetND:

        >>> cities = pd.Series(
        ...     ['A', 'B', 'C'],
        ...     index=(('Asia', 'Delhi'), ('Americas', 'Seattle'), ('Asia', 'Tokyo')),
        ...     name='ID',
        ... ).rename_axis(['ZONE', 'CITY'])
        >>> cities
        ZONE      CITY
        Asia      Delhi      A
        Americas  Seattle    B
        Asia      Tokyo      C
        Name: ID, dtype: object

        >>> cities.index.opti.to_indexset()
        IndexSetND: (ZONE, CITY)
        [('Asia', 'Delhi'), ('Americas', 'Seattle'), ('Asia', 'Tokyo')]
        """
        if self._idx.nlevels > 1:  # multi-level index
            names = (
                None if any(x is None for x in self._idx.names) else list(map(str, self._idx.names))
            )
            return IndexSetND(self._idx, names=names)

        else:
            name = None if self._idx.name is None else str(self._idx.name)
            return IndexSet1D(self._idx, name=name)
