# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Functions to add variable(s) to an xpress problem."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, overload

import xpress as xp

from .._index_sets import Elem1DT, ElemNDT, IndexSet1D, IndexSetND
from .._param_dicts import ParamDict1D, ParamDictND, ParamT
from ._var_dicts import VarDict1D, VarDictND


def _paramdictNd_as_attr(
    indexset: IndexSetND[ElemNDT],
    attr: ParamDictND[ElemNDT, ParamT],
    attr_type: Literal['lb', 'ub', 'threshold'],
) -> ParamDictND[ElemNDT, ParamT]:
    """Use ParamDictND as xpress variable attribute.

    Parameters
    ----------
    indexset : IndexSetND
        Index-set for defining the variables.
    attr : ParamDictND
        ParamDict to be used as the attribute.
    attr_type : str
        Attribute type, ``'lb'`` or ``'ub'`` or ``'threshold'``.

    Returns
    -------
    ParamDictND
        ParamDictND that can be used as xpress variable attribute for the `problem.addVariables`
        method.

    Raises
    ------
    ValueError
        ParamDict keys and indexset have tuple elements of different lengths.
    """
    if (not attr) or (attr and attr._indexset._tuplelen == indexset._tuplelen):
        return attr
    else:
        raise ValueError(f'{attr_type} keys and indexset have tuple elements of different lengths')


def _preprocess_attr(
    indexset: IndexSet1D[Elem1DT] | IndexSetND[ElemNDT],
    attr: int
    | float
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, ParamT]
    | Mapping[ElemNDT, ParamT],
    attr_type: Literal['lb', 'ub', 'threshold'],
) -> (
    int
    | float
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, ParamT]
    | Mapping[ElemNDT, ParamT]
):
    """Preprocess xpress variable attribute.

    Parameters
    ----------
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables.
    attr : Mapping or ParamDict
        Variable attribute.
    attr_type : str
        Attribute type, ``'lb'`` or ``'ub'`` or ``'threshold'``.

    Returns
    -------
    Mapping or ParamDict
        Xpress variable attribute for the `problem.addVariables` method.

    Raises
    ------
    ValueError
        ParamDict keys and indexset have tuple elements of different lengths.
    TypeError
        If paramdict is ParamDictND and indexset is IndexSet1D, or vice versa.
    """
    # Validate if ParamDict is used as variable attribute
    if isinstance(attr, ParamDict1D):
        if isinstance(indexset, IndexSet1D):
            return attr
        else:
            raise TypeError(f'`{attr_type}` should be ParamDictND when indexset is IndexSetND')
    elif isinstance(attr, ParamDictND):
        if isinstance(indexset, IndexSetND):
            return _paramdictNd_as_attr(indexset, attr, attr_type)
        else:
            raise TypeError(f'`{attr_type}` should be ParamDict1D when indexset is IndexSet1D')
    # Let xpress handle everything else, so return as is
    else:
        return attr


@overload
def addVariables(  # numpydoc ignore=GL08
    problem: xp.problem,
    indexset: IndexSet1D[Elem1DT],
    name: str | None = ...,
    lb: int | float | ParamDict1D[Elem1DT, ParamT] | Mapping[Elem1DT, int | float] = ...,
    ub: int | float | ParamDict1D[Elem1DT, ParamT] | Mapping[Elem1DT, int | float] = ...,
    threshold: int | float | ParamDict1D[Elem1DT, ParamT] | Mapping[Elem1DT, int | float] = ...,
    vartype: int = ...,
) -> VarDict1D[Elem1DT, xp.var]: ...


@overload
def addVariables(  # numpydoc ignore=GL08
    problem: xp.problem,
    indexset: IndexSetND[ElemNDT],
    name: str | None = ...,
    lb: int | float | ParamDictND[ElemNDT, ParamT] | Mapping[ElemNDT, int | float] = ...,
    ub: int | float | ParamDictND[ElemNDT, ParamT] | Mapping[ElemNDT, int | float] = ...,
    threshold: int | float | ParamDictND[ElemNDT, ParamT] | Mapping[ElemNDT, int | float] = ...,
    vartype: int = ...,
) -> VarDictND[ElemNDT, xp.var]: ...


def addVariables(
    problem: xp.problem,
    indexset: IndexSet1D[Elem1DT] | IndexSetND[ElemNDT],
    name: str | None = 'x',
    lb: int
    | float
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float] = 0,
    ub: int
    | float
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float] = xp.infinity,
    threshold: int
    | float
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float] = 1,
    vartype: int = xp.continuous,
) -> VarDict1D[Elem1DT, xp.var] | VarDictND[ElemNDT, xp.var]:
    """Create and add multiple variables (corresponding to an index-set) to the xpress problem.

    This function extends xpress's `problem.addVariables` method by wrapping it and returning
    VarDict1D/VarDictND data structures - that can efficiently sum subsets of variables with
    a user-friendly syntax based on wildcard patterns.

    Parameters
    ----------
    problem : xpress.problem
        Xpress problem.
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables. The ``name``/``names`` attribute of
        IndexSet1D/IndexSetND will be set as the ``key_name``/``key_names`` attribute of
        VarDict1D/VarDictND.
    name : str, optional
        Variable name, by default ``'x'``. It will also be used as the ``value_name`` attribute of
        VarDict1D/VarDictND.
    lb : int or float or dict or ParamDict, optional
        Lower bound, in one of the following forms:

        * A number - if all variables share the same lower bound.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the lower bound; will fallback to the default for index-set elements
          not found in dict/ParamDict keys.

        Default is ``0.0``.
    ub : int or float or dict or ParamDict, optional
        Upper bound, in one of the following forms:

        * A number - if all variables share the same upper bound.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the upper bound; will fallback to the default for index-set elements
          not found in dict/ParamDict keys.

        Default is ``1.0`` for binary variable type and ``infinity`` for other types.
    threshold : int or float or dict or ParamDict, optional
        Threshold, in one of the following forms:

        * A number - if all variables share the same objective coefficient.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the objective coefficient; will fallback to the default for index-set
          elements not found in dict/ParamDict keys.

        Only applies to semi-continuous, semi-integer, and partially integer variables; it must be
        between its lower and its upper bound. Default is ``1``.
    vartype : int
        Variable type, in one of the following forms:

        * ``xpress.continuous``
        * ``xpress.binary``
        * ``xpress.integer``
        * ``xpress.semicontinuous``
        * ``xpress.semiinteger``
        * ``xpress.partiallyinteger``

        Default is ``xpress.continuous``.

    Returns
    -------
    VarDict1D or VarDictND

    Raises
    ------
    ValueError
        If the index-set is empty.

    Examples
    --------
    Create xpress problem:

    >>> import xpress as xp
    >>> import warnings
    >>> warnings.filterwarnings('ignore', category=xp.LicenseWarning)

    >>> prob = xp.problem()

    Create index-sets:

    >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')
    >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

    Add variables:

    >>> node_select = addVariables(prob, nodes, name='select', vartype=xp.binary)
    >>> node_select
    VarDict1D: node -> select
    {'A': select(A), 'B': select(B), 'C': select(C)}

    >>> arc_flow = addVariables(prob, arcs, name='flow', ub=10, vartype=xp.continuous)
    >>> arc_flow
    VarDictND: (ori, des) -> flow
    {('A', 'B'): flow(('A', 'B')),
     ('B', 'C'): flow(('B', 'C')),
     ('C', 'B'): flow(('C', 'B'))}
    """
    if not isinstance(problem, xp.problem):
        raise TypeError('`problem` should be xp.problem')
    if not isinstance(indexset, IndexSet1D | IndexSetND):
        raise TypeError('`indexset` should be either IndexSet1D or IndexSetND')
    if not indexset:
        raise ValueError(f'{indexset.__class__.__name__} is empty')

    scalar_lb = isinstance(lb, int | float)
    scalar_ub = isinstance(ub, int | float)
    scalar_th = isinstance(threshold, int | float)
    if scalar_lb and scalar_ub and scalar_th:
        xp_var_dict = problem.addVariables(
            indexset, name=name, lb=lb, ub=ub, threshold=threshold, vartype=vartype
        )
    else:
        lb = _preprocess_attr(indexset, lb, 'lb')  # type: ignore[arg-type]
        ub = _preprocess_attr(indexset, ub, 'ub')  # type: ignore[arg-type]
        threshold = _preprocess_attr(indexset, threshold, 'threshold')  # type: ignore[arg-type]
        # Using type ignore as mypy cannot deduce typevars.
        xp_var_dict = {
            elem: problem.addVariable(
                name=f'{name}({elem})',
                lb=lb if scalar_lb else lb.get(elem, 0),  # type: ignore
                ub=ub if scalar_ub else ub.get(elem, xp.infinity),  # type: ignore
                threshold=threshold if scalar_th else threshold.get(elem, 1),  # type: ignore
                # Using type ignore as mypy cannot deduce that lb / ub / threshold would reduce to
                # paramdicts or mappings. Moreover, mypy also complains about the type of defaults
                # provided with respect to the typevars in class def.
                vartype=vartype,
            )
            for elem in indexset
        }

    value_name = name if isinstance(name, str) else None

    if isinstance(indexset, IndexSet1D):
        return VarDict1D._create(
            xp_var_dict, indexset, problem=problem, vartype=vartype, value_name=value_name
        )
    return VarDictND._create(
        xp_var_dict, indexset, problem=problem, vartype=vartype, value_name=value_name
    )
