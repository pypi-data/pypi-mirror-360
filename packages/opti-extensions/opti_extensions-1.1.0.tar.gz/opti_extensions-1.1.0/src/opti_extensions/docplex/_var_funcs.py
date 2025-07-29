# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Functions to add variable(s) to a DOcplex model."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Literal, overload

from docplex.mp.dvar import Var
from docplex.mp.model import Model
from docplex.mp.vartype import (
    BinaryVarType,
    ContinuousVarType,
    IntegerVarType,
    SemiContinuousVarType,
    SemiIntegerVarType,
)

from .._index_sets import Elem1DT, ElemNDT, IndexSet1D, IndexSetND
from .._param_dicts import ParamDict1D, ParamDictND, ParamT
from ._var_dicts import VarDict1D, VarDictND


def _get_docpx_vartype(
    vartype: str, model: Model
) -> (
    ContinuousVarType | BinaryVarType | IntegerVarType | SemiContinuousVarType | SemiIntegerVarType
):
    """Get the DOcplex variable type from the corresponding string name.

    Parameters
    ----------
    vartype : str
        Variable type.
    model : docplex.mp.model.Model
        DOcplex model.

    Returns
    -------
    DOcplex variable type (subclass of docplex.mp.vartype.VarType)

    Raises
    ------
    ValueError
        If the variable type name is invalid.
    """
    if not isinstance(vartype, str):
        raise TypeError('`vartype` should be a string')

    match vartype.lower():
        case 'continuous' | 'c':
            return model.continuous_vartype
        case 'binary' | 'b':
            return model.binary_vartype
        case 'integer' | 'i':
            return model.integer_vartype
        case 'semicontinuous' | 'sc':
            return model.semicontinuous_vartype
        case 'semiinteger' | 'si':
            return model.semiinteger_vartype
        case _:
            raise ValueError('`vartype` is invalid')


def _paramdictNd_as_bound(
    indexset: IndexSetND[ElemNDT],
    bound: ParamDictND[ElemNDT, ParamT],
    bound_type: Literal['lb', 'ub'],
) -> Callable[..., int | float | None]:
    """Use ParamDictND as DOcplex variable bound.

    Parameters
    ----------
    indexset : IndexSetND
        Index-set for defining the variables.
    bound : ParamDictND
        ParamDict to be used as variable bound.
    bound_type : str
        Bound type, either ``'lb'`` or ``'ub'``.

    Returns
    -------
    function
        ParamDictND.get method that can be used as DOcplex variable bound for the
        `Model.xyz_var_dict` method.

    Raises
    ------
    ValueError
        ParamDict keys and indexset have tuple elements of different lengths.
    """
    if (not bound) or (bound and bound._indexset._tuplelen == indexset._tuplelen):
        return bound.get
    else:
        raise ValueError(f'{bound_type} keys and indexset have tuple elements of different lengths')


def _preprocess_bound(
    indexset: IndexSet1D[Elem1DT] | IndexSetND[ElemNDT],
    bound: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | None,
    bound_type: Literal['lb', 'ub'],
) -> int | float | Sequence[int | float | None] | Callable[..., int | float | None] | None:
    """Preprocess DOcplex variable bound.

    Parameters
    ----------
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables.
    bound : int or float or Sequence or function or ParamDict or None
        Variable bound.
    bound_type : str
        Bound type, either ``'lb'`` or ``'ub'``.

    Returns
    -------
    int or float or Sequence or function or None
        DOcplex variable bound for the `Model.xyz_var_dict` method.

    Raises
    ------
    ValueError
        ParamDict keys and indexset have tuple elements of different lengths.
    TypeError
        If paramdict is ParamDictND and indexset is IndexSet1D, or vice versa.
    """
    # Validate if ParamDict is used as variable bound
    if isinstance(bound, ParamDict1D):
        if isinstance(indexset, IndexSet1D):
            return bound.get
        else:
            raise TypeError(f'`{bound_type}` should be ParamDictND when indexset is IndexSetND')
    elif isinstance(bound, ParamDictND):
        if isinstance(indexset, IndexSetND):
            return _paramdictNd_as_bound(indexset, bound, bound_type)
        else:
            raise TypeError(f'`{bound_type}` should be ParamDict1D when indexset is IndexSet1D')
    # Let DOcplex handle everything else, so return as is
    else:
        return bound


@overload
def add_variable(  # numpydoc ignore=GL08
    model: Model,
    vartype: Literal[
        'continuous',
        'integer',
        'binary',
        'semicontinuous',
        'semiinteger',
        'C',
        'I',
        'B',
        'SC',
        'SI',
    ],
    lb: int | float,
    ub: int | float | None = ...,
    name: str | None = ...,
) -> Var: ...


@overload
def add_variable(  # numpydoc ignore=GL08
    model: Model,
    vartype: Literal['continuous', 'integer', 'binary', 'C', 'I', 'B'],
    lb: int | float | None = ...,
    ub: int | float | None = ...,
    name: str | None = ...,
) -> Var: ...


def add_variable(
    model: Model,
    vartype: Literal[
        'continuous',
        'integer',
        'binary',
        'semicontinuous',
        'semiinteger',
        'C',
        'I',
        'B',
        'SC',
        'SI',
    ],
    lb: int | float | None = None,
    ub: int | float | None = None,
    name: str | None = None,
) -> Var:
    """Create and add a single variable to the DOcplex model.

    This function is a simple wrapper around DOcplex's `xyz_var` methods and provided for a
    consistent API experience.

    Parameters
    ----------
    model : docplex.mp.model.Model
        DOcplex model.
    vartype : str
        Variable type, in one of the following forms:

        * ``'continuous'`` or ``'C'``
        * ``'binary'`` or ``'B'``
        * ``'integer'`` or ``'I'``
        * ``'semicontinuous'`` or ``'SC'``
        * ``'semiinteger'`` or ``'SI'``

    lb : int or float
        Lower bound. Default ``None`` corresponds to:

        * Continuous: 0
        * Binary: 0
        * Integer: 0
        * Semicontinuous: not applicable... will raise ValueError
        * Semiinteger: not applicable... will raise ValueError

    ub : int or float, optional
        Upper bound. Default ``None`` corresponds to:

        * Continuous: infinity (1e+20)
        * Binary: 1
        * Integer: infinity (1e+20)
        * Semicontinuous: infinity (1e+20)
        * Semiinteger: infinity (1e+20)

    name : str, optional
        Variable name, by default ``None``.

    Returns
    -------
    docplex.mp.dvar.Var

    Raises
    ------
    ValueError
        If the variable type is invalid.
    ValueError
        If no lower bound is specified for Semicontinuous or Semiinteger variable type.

    See Also
    --------
    add_variables : For multiple variables (corresponding to an index-set).

    Examples
    --------
    Create DOcplex model:

    >>> from docplex.mp.model import Model
    >>> mdl = Model()

    Add variables:

    >>> x = add_variable(mdl, 'C', name='x')
    >>> x
    docplex.mp.Var(type=C,name='x')

    >>> y = add_variable(mdl, 'semicontinuous', lb=2, ub=5, name='y')
    >>> y
    docplex.mp.Var(type=S,name='y',lb=2,ub=5)
    """
    if not isinstance(model, Model):
        raise TypeError('`model` should be docplex.mp.model.Model')

    vt = _get_docpx_vartype(vartype, model)
    if vartype.lower() in ('semicontinuous', 'sc') and lb is None:
        raise ValueError('Need to set a lower bound for Semicontinuous variable type')
    if vartype.lower() in ('semiinteger', 'si') and lb is None:
        raise ValueError('Need to set a lower bound for Semiinteger variable type')

    return model.var(vt, lb, ub, name)


@overload
def add_variables(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSet1D[Elem1DT],
    vartype: Literal[
        'continuous',
        'integer',
        'binary',
        'semicontinuous',
        'semiinteger',
        'C',
        'I',
        'B',
        'SC',
        'SI',
    ],
    lb: int
    | float
    | Sequence[int | float]
    | Callable[..., int | float]
    | ParamDict1D[Elem1DT, ParamT],
    ub: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | None = ...,
    name: str | Callable[..., str] | None = ...,
    key_format: str | None = ...,
) -> VarDict1D[Elem1DT, Var]: ...


@overload
def add_variables(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSet1D[Elem1DT],
    vartype: Literal['continuous', 'integer', 'binary', 'C', 'I', 'B'],
    lb: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | None = ...,
    ub: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | None = ...,
    name: str | Callable[..., str] | None = ...,
    key_format: str | None = ...,
) -> VarDict1D[Elem1DT, Var]: ...


@overload
def add_variables(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSetND[ElemNDT],
    vartype: Literal[
        'continuous',
        'integer',
        'binary',
        'semicontinuous',
        'semiinteger',
        'C',
        'I',
        'B',
        'SC',
        'SI',
    ],
    lb: int
    | float
    | Sequence[int | float]
    | Callable[..., int | float]
    | ParamDictND[ElemNDT, ParamT],
    ub: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDictND[ElemNDT, ParamT]
    | None = ...,
    name: str | Callable[..., str] | None = ...,
    key_format: str | None = ...,
) -> VarDictND[ElemNDT, Var]: ...


@overload
def add_variables(  # numpydoc ignore=GL08
    model: Model,
    indexset: IndexSetND[ElemNDT],
    vartype: Literal['continuous', 'integer', 'binary', 'C', 'I', 'B'],
    lb: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDictND[ElemNDT, ParamT]
    | None = ...,
    ub: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDictND[ElemNDT, ParamT]
    | None = ...,
    name: str | Callable[..., str] | None = ...,
    key_format: str | None = ...,
) -> VarDictND[ElemNDT, Var]: ...


def add_variables(
    model: Model,
    indexset: IndexSet1D[Elem1DT] | IndexSetND[ElemNDT],
    vartype: Literal[
        'continuous',
        'integer',
        'binary',
        'semicontinuous',
        'semiinteger',
        'C',
        'I',
        'B',
        'SC',
        'SI',
    ],
    lb: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | None = None,
    ub: int
    | float
    | Sequence[int | float | None]
    | Callable[..., int | float | None]
    | ParamDict1D[Elem1DT, ParamT]
    | ParamDictND[ElemNDT, ParamT]
    | None = None,
    name: str | Callable[..., str] | None = None,
    key_format: str | None = None,
) -> VarDict1D[Elem1DT, Var] | VarDictND[ElemNDT, Var]:
    """Create and add multiple variables (corresponding to an index-set) to the DOcplex model.

    This function extends DOcplex's `Model.xyz_var_dict` methods by wrapping them and returning
    VarDict1D/VarDictND data structures - that can efficiently sum subsets of variables with
    a user-friendly syntax based on wildcard patterns.

    Parameters
    ----------
    model : docplex.mp.model.Model
        DOcplex model.
    indexset : IndexSet1D or IndexSetND
        Index-set for defining the variables. The ``name``/``names`` attribute of
        IndexSet1D/IndexSetND will be set as the ``key_name``/``key_names`` attribute of
        VarDict1D/VarDictND.
    vartype : str
        Variable type, in one of the following forms:

        * ``'continuous'`` or ``'C'``
        * ``'binary'`` or ``'B'``
        * ``'integer'`` or ``'I'``
        * ``'semicontinuous'`` or ``'SC'``
        * ``'semiinteger'`` or ``'SI'``

    lb : int or float or sequence or function or ParamDict, optional
        Lower bound, in one of the following forms:

        * A number - if all variables share the same lower bound.
        * A sequence of numbers - one for each variable.
        * A function - that returns a number when called on each element of index-set.
        * A ParamDict - with keys following the same structute as the index-set elements and values
          representing the lower bound; will fallback to ``None`` for index-set elements not found
          in ParamDict keys.

        Default ``None`` corresponds to:

        * Continuous: 0
        * Binary: 0
        * Integer: 0
        * Semicontinuous: not applicable... will raise ValueError
        * Semiinteger: not applicable... will raise ValueError

    ub : int or float or sequence or function or ParamDict, optional
        Upper bound, in one of the following forms:

        * A number - if all variables share the same lower bound.
        * A sequence of numbers - one for each variable.
        * A function - that returns a number when called on each element of the index-set.
        * A ParamDict - with keys following the same structute as the index-set elements and values
          representing the upper bound; will fallback to ``None`` for index-set elements not found
          in ParamDict keys.

        Default ``None`` corresponds to ``1`` for binary variable type and ``infinity`` for other
        types.
    name : str or function, optional
        For naming variables, in one of the following forms:

        * A string - applied as a prefix to the string representation of each element of the
          index-set.
        * A function - that generates a name when called on each element of the index-set.
        * ``None``.

        Default is None. It will also be used as the ``value_name`` attribute of
        VarDict1D/VarDictND.
    key_format : format str (should include '%s'), optional
        Defines how index-set elements are incorporated into variable names, by default ``'_%s'``.

    Returns
    -------
    VarDict1D or VarDictND

    Raises
    ------
    ValueError
        If the index-set is empty.
    ValueError
        If the variable type is invalid.
    ValueError
        If no lower bound is specified for Semicontinuous or Semiinteger variable type.

    See Also
    --------
    add_variable : For a single variable.

    Examples
    --------
    Create DOcplex model:

    >>> from docplex.mp.model import Model
    >>> mdl = Model()

    Create index-sets:

    >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')
    >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

    Add variables:

    >>> node_select = add_variables(mdl, nodes, 'B', name='select')
    >>> node_select
    VarDict1D: node -> select
    {'A': docplex.mp.Var(type=B,name='select_A'),
     'B': docplex.mp.Var(type=B,name='select_B'),
     'C': docplex.mp.Var(type=B,name='select_C')}

    >>> arc_flow = add_variables(mdl, arcs, 'C', ub=10, name='flow')
    >>> arc_flow
    VarDictND: (ori, des) -> flow
    {('A', 'B'): docplex.mp.Var(type=C,name='flow_A_B',ub=10),
     ('B', 'C'): docplex.mp.Var(type=C,name='flow_B_C',ub=10),
     ('C', 'B'): docplex.mp.Var(type=C,name='flow_C_B',ub=10)}
    """
    if not isinstance(model, Model):
        raise TypeError('`model` should be docplex.mp.model.Model')
    if not isinstance(indexset, IndexSet1D | IndexSetND):
        raise TypeError('`indexset` should be either IndexSet1D or IndexSetND')
    if not indexset:
        raise ValueError(f'{indexset.__class__.__name__} is empty')

    lb = _preprocess_bound(indexset, lb, 'lb')
    ub = _preprocess_bound(indexset, ub, 'ub')

    vt = _get_docpx_vartype(vartype, model)
    if vt.is_semi_type():
        # Provide informative error messages since those from DOcplex are not easy to understand
        if lb is None:
            raise ValueError(f'Need to set a lower bound for {vt.short_name} variable type')
        if (isinstance(lb, Sequence) and None in lb) or (
            callable(lb) and any(lb(elem) is None for elem in indexset)
        ):
            raise ValueError(
                f'Did not get a lower bound for all variables; not allowed for {vt.short_name}'
                'variable type'
            )

    docpx_var_dict = model.var_dict(indexset, vt, lb, ub, name, key_format)
    value_name = name if isinstance(name, str) else None

    if isinstance(indexset, IndexSet1D):
        return VarDict1D._create(
            docpx_var_dict, indexset, model=model, vartype=vt, value_name=value_name
        )
    return VarDictND._create(
        docpx_var_dict, indexset, model=model, vartype=vt, value_name=value_name
    )
