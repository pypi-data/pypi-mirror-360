# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""
The `opti-extensions` package.

A collection of custom data structures and user-friendly functions for mathematical optimization
modeling with docplex, gurobipy, and xpress.
"""

__version__ = '1.1.0'

# Package functionality
from ._index_sets import IndexSet1D, IndexSetND
from ._pandas_accessors import DataFrameAccessor as _DataFrameAccessor
from ._pandas_accessors import IndexAccessor as _IndexAccessor
from ._pandas_accessors import SeriesAccessor as _SeriesAccessor
from ._param_dicts import ParamDict1D, ParamDictND

# Register custom accessors if pandas is available
try:
    import pandas as _pd

    _pd.api.extensions.register_series_accessor('opti')(_SeriesAccessor)
    _pd.api.extensions.register_dataframe_accessor('opti')(_DataFrameAccessor)
    _pd.api.extensions.register_index_accessor('opti')(_IndexAccessor)

except ImportError:
    pass

# Public API
__all__ = ['IndexSet1D', 'IndexSetND', 'ParamDict1D', 'ParamDictND']
