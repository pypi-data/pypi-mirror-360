# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""
The `opti-extensions` package.

`docplex`-specific functionality.
"""

# Check required dependencies
from importlib.util import find_spec as _find_spec

if _find_spec('docplex') is None:
    raise ImportError('Unable to import required dependency: docplex')

# Package functionality
from ._model_funcs import print_problem_stats, print_solution_quality_stats, runseeds, solve
from ._tuning_funcs import batch_tune, tune
from ._var_dicts import VarDict1D, VarDictND
from ._var_funcs import add_variable, add_variables

# Public API
__all__ = [
    'print_problem_stats',
    'print_solution_quality_stats',
    'runseeds',
    'solve',
    'batch_tune',
    'tune',
    'VarDict1D',
    'VarDictND',
    'add_variable',
    'add_variables',
]
