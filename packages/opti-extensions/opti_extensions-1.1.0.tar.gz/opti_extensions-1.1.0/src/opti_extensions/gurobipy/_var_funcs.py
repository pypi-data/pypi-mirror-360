# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Functions to add variable(s) to a gurobipy model."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal, overload

from gurobipy import GRB, Model, Var

from .._index_sets import Elem1DT, ElemNDT, IndexSet1D, IndexSetND
from .._param_dicts import ParamDict1D, ParamDictND, ParamT
from ._var_dicts import VarDict1D, VarDictND


def _paramdictNd_as_attr(
    indexset: IndexSetND[ElemNDT],
    attr: ParamDictND[ElemNDT, ParamT],
    attr_type: Literal['lb', 'ub', 'obj'],
) -> ParamDictND[ElemNDT, ParamT]:
    """Use ParamDictND as gurobipy variable attribute.

    Parameters
    ----------
    indexset : IndexSetND
        Index-set for defining the variables.
    attr : ParamDictND
        ParamDict to be used as the attribute.
    attr_type : str
        Attribute type, ``'lb'`` or ``'ub'`` or ``'obj'``.

    Returns
    -------
    ParamDictND
        ParamDictND that can be used as gurobipy variable attribute for the `Model.addVars` method.

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
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float],
    attr_type: Literal['lb', 'ub', 'obj'],
) -> (
    int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float]
):
    """Preprocess gurobipy variable attribute.

    Parameters
    ----------
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables.
    attr : int or float or Sequence or Mapping or ParamDict
        Variable attribute.
    attr_type : str
        Attribute type, ``'lb'`` or ``'ub'`` or ``'obj'``.

    Returns
    -------
    int or float or Sequence or Mapping or ParamDict
        The gurobipy variable attribute for the `Model.addVars` method.

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
    # Let gurobipy handle everything else, so return as is
    else:
        return attr


@overload
def addVars(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSet1D[Elem1DT],
    lb: int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | Mapping[Elem1DT, int | float] = ...,
    ub: int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | Mapping[Elem1DT, int | float] = ...,
    obj: int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | Mapping[Elem1DT, int | float] = ...,
    vtype: str = ...,
    name: str = ...,
) -> VarDict1D[Elem1DT, Var]: ...


@overload
def addVars(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSetND[ElemNDT],
    lb: int
    | float
    | Sequence[int | float]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[ElemNDT, int | float] = ...,
    ub: int
    | float
    | Sequence[int | float]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[ElemNDT, int | float] = ...,
    obj: int
    | float
    | Sequence[int | float]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[ElemNDT, int | float] = ...,
    vtype: str = ...,
    name: str = ...,
) -> VarDictND[ElemNDT, Var]: ...


def addVars(
    model: Model,
    indexset: IndexSet1D[Elem1DT] | IndexSetND[ElemNDT],
    lb: int
    | float
    | Sequence[int | float]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT] = 0.0,
    ub: int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float] = float('inf'),
    obj: int
    | float
    | Sequence[int | float]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | Mapping[Elem1DT, int | float]
    | Mapping[ElemNDT, int | float] = 0.0,
    vtype: str = GRB.CONTINUOUS,
    name: str = '',
) -> VarDict1D[Elem1DT, Var] | VarDictND[ElemNDT, Var]:
    """Create and add multiple variables (corresponding to an index-set) to the gurobipy model.

    This function extends gurobipy's `Model.addVars` method by wrapping it and returning
    VarDict1D/VarDictND data structures - that can efficiently sum subsets of variables with
    a user-friendly syntax based on wildcard patterns.

    Parameters
    ----------
    model : gurobipy.Model
        The gurobipy model.
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables. The ``name``/``names`` attribute of
        IndexSet1D/IndexSetND will be set as the ``key_name``/``key_names`` attribute of
        VarDict1D/VarDictND.
    lb : int or float or sequence or dict or ParamDict, optional
        Lower bound, in one of the following forms:

        * A number - if all variables share the same lower bound.
        * A sequence of numbers - one for each variable.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the lower bound; will fallback to the default for index-set elements
          not found in dict/ParamDict keys.

        Default is ``0.0``.
    ub : int or float or sequence or dict or ParamDict, optional
        Upper bound, in one of the following forms:

        * A number - if all variables share the same upper bound.
        * A sequence of numbers - one for each variable.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the upper bound; will fallback to the default for index-set elements
          not found in dict/ParamDict keys.

        Default is ``1.0`` for binary variable type and ``infinity`` for other types.
    obj : int or float or sequence or dict or ParamDict, optional
        Objective coefficient, in one of the following forms:

        * A number - if all variables share the same objective coefficient.
        * A sequence of numbers - one for each variable.
        * A dict/ParamDict - with keys following the same structute as the index-set elements and
          values representing the objective coefficient; will fallback to the default for index-set
          elements not found in dict/ParamDict keys.

        Default is ``0.0``.
    vtype : str, optional
        Variable type, in one of the following forms:

        * ``GRB.CONTINUOUS``
        * ``GRB.BINARY``
        * ``GRB.INTEGER``
        * ``GRB.SEMICONT``
        * ``GRB.SEMIINT``

        Default is ``GRB.CONTINUOUS``.
    name : str, optional
        Variable name, by default empty string. It will also be used as the ``value_name`` attribute
        of VarDict1D/VarDictND.

    Returns
    -------
    VarDict1D or VarDictND

    Raises
    ------
    ValueError
        If the index-set is empty.

    Examples
    --------
    Create gurobipy model:

    >>> from gurobipy import Model
    >>> mdl = Model()

    Create index-sets:

    >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')
    >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

    Add variables:

    >>> node_select = addVars(mdl, nodes, vtype=GRB.BINARY, name='select')
    >>> mdl.update()
    >>> node_select
    VarDict1D: node -> select
    {'A': <gurobi.Var select[A]>, 'B': <gurobi.Var select[B]>, 'C': <gurobi.Var select[C]>}

    >>> arc_flow = addVars(mdl, arcs, ub=10, vtype=GRB.CONTINUOUS, name='flow')
    >>> mdl.update()
    >>> arc_flow
    VarDictND: (ori, des) -> flow
    {('A', 'B'): <gurobi.Var flow[A,B]>,
     ('B', 'C'): <gurobi.Var flow[B,C]>,
     ('C', 'B'): <gurobi.Var flow[C,B]>}
    """
    if not isinstance(model, Model):
        raise TypeError('`model` should be gurobipy.Model')
    if not isinstance(indexset, IndexSet1D | IndexSetND):
        raise TypeError('`indexset` should be either IndexSet1D or IndexSetND')
    if not indexset:
        raise ValueError(f'{indexset.__class__.__name__} is empty')

    lb = _preprocess_attr(indexset, lb, 'lb')
    ub = _preprocess_attr(indexset, ub, 'ub')
    obj = _preprocess_attr(indexset, obj, 'obj')

    gp_var_dict = model.addVars(indexset, lb=lb, ub=ub, obj=obj, vtype=vtype, name=name)  # type: ignore[arg-type]
    # Since gurobipy stubs do not identify IndexSet and ParamDict data structures, we'll add a type
    # ignore comment here
    value_name = name if isinstance(name, str) else None

    if isinstance(indexset, IndexSet1D):
        return VarDict1D._create(
            gp_var_dict, indexset, model=model, vtype=vtype, value_name=value_name
        )
    return VarDictND._create(gp_var_dict, indexset, model=model, vtype=vtype, value_name=value_name)
