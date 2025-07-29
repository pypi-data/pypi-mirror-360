# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""
The `opti-extensions` package.

`gurobipy`-specific functionality.
"""

# Check required dependencies
from importlib.util import find_spec as _find_spec

if _find_spec('gurobipy') is None:
    raise ImportError('Unable to import required dependency: gurobipy')

# Package functionality
from ._var_dicts import VarDict1D, VarDictND
from ._var_funcs import addVars

# Public API
__all__ = ['VarDict1D', 'VarDictND', 'addVars']
