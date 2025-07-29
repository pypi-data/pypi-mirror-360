# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""VarDict data structures."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal, TypeVar, cast

from docplex.mp.dvar import Var
from docplex.mp.linear import LinearExpr, ZeroExpr
from docplex.mp.model import Model
from docplex.mp.quad import QuadExpr
from docplex.mp.vartype import VarType

from .._dict_mixins import Dict1DMixin, DictNDMixin
from .._index_sets import Elem1DT, ElemNDT, ElemT, IndexSet1D, IndexSetBase, IndexSetND
from .._param_dicts import ParamDict1D, ParamDictND, ParamT
from .._var_dict_base import VarDictBase, _validate_for_dot_1d, _validate_for_dot_Nd

VarT = TypeVar('VarT', bound=Var)


class VarDictCore(VarDictBase[ElemT, VarT]):
    """Base class for custom subclasses of `dict` to define DOcplex model variables.

    Provides runtime type checks to ensure variables are `gurobipy.Var` objects.

    Parameters
    ----------
    docpx_var_dict : dict
        Dictionary of variable objects associated with the DOcplex model.
    indexset : IndexSetBase
        Keys of dictionary encapsulated in an IndexSet.
    model : docplex.mp.model.Model
        DOcplex model associated with the variable objects.
    vartype : docplex.mp.vartype.VarType
        Type corresponding to the variable objects.
    """

    __slots__ = ('_model', '_vartype')

    def __init__(
        self,
        docpx_var_dict: dict[ElemT, VarT],
        /,
        *,
        indexset: IndexSetBase[ElemT],
        model: Model,
        vartype: VarType,
    ) -> None:
        self._validate_docpx_var_dict(docpx_var_dict)

        self._model = model
        self._vartype = vartype

        super().__init__(docpx_var_dict, indexset)

    @property
    def model(self) -> Model:
        """The DOcplex model associated with the variables.

        Returns
        -------
        docplex.mp.model.Model
        """
        return self._model

    @property
    def vartype(self) -> VarType:
        """The DOcplex VarType corresponding to the variables.

        Returns
        -------
        DOcplex variable type (subclass of docplex.mp.vartype.VarType)
        """
        return self._vartype

    @staticmethod
    def _validate_docpx_var_dict(docpx_var_dict: dict[ElemT, VarT]) -> None:
        """Validate that the input is a populated dict of DOcplex variables.

        Parameters
        ----------
        docpx_var_dict : dict
            Input dictionary for VarDict.
        """
        if not isinstance(docpx_var_dict, dict):
            raise TypeError('input should be a dict')
        if not docpx_var_dict:
            raise ValueError('dict should be populated')
        if any(not isinstance(x, Var) for x in docpx_var_dict.values()):
            raise TypeError('dict values should be docplex.mp.dvar.Var objects')


class VarDict1D(VarDictCore[Elem1DT, VarT], Dict1DMixin[Elem1DT, VarT]):
    """Custom subclasses of `dict` to define DOcplex model variables with 1-dim scalar keys.

    Parameters
    ----------
    docpx_var_dict : dict
        Dictionary of variable objects from docplex.
    indexset : IndexSet1D
        Keys of dictionary encapsulated in IndexSet1D.
    model : docplex.mp.model.Model
        DOcplex model associated with the variable objects.
    vartype : docplex.mp.vartype.VarType
        DOcplex VarType corresponding to the variable objects.
    value_name : str, optional
        Name to refer to variables - not used internally, and solely for user reference.
    """

    # Private attributes
    # ------------------
    # _indexset : IndexSet1D
    #     Index-set of keys.

    __slots__ = ('_key_name', '_value_name')

    def __init__(
        self,
        docpx_var_dict: dict[Elem1DT, VarT],
        indexset: IndexSet1D[Elem1DT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> None:
        self.key_name = indexset.name
        self.value_name = value_name

        super().__init__(docpx_var_dict, indexset=indexset, model=model, vartype=vartype)

    def __new__(
        cls,
        docpx_var_dict: dict[Elem1DT, VarT],
        indexset: IndexSet1D[Elem1DT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> VarDict1D[Elem1DT, VarT]:
        raise TypeError(
            'This class is not meant to be instantiated; VarDict1D is built through the '
            'opti_extensions.docplex.add_variables function'
        )

    @classmethod
    def _create(
        cls,
        docpx_var_dict: dict[Elem1DT, VarT],
        indexset: IndexSet1D[Elem1DT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> VarDict1D[Elem1DT, VarT]:
        # Private method to construct VarDict1D
        instance = super().__new__(cls)
        cls.__init__(
            instance, docpx_var_dict, indexset, model=model, vartype=vartype, value_name=value_name
        )
        return instance

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

    def lookup(self, key: Elem1DT) -> VarT | Literal[0]:
        """Get the variable for the specified key, or zero if it is not found.

        Parameters
        ----------
        key : key

        Returns
        -------
        docplex.mp.dvar.Var or ``0``

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> node_select = add_variables(mdl, nodes, 'B', name='node-select')

        Lookup for keys:

        >>> node_select.lookup('A')
        docplex.mp.Var(type=B,name='node-select_A')

        >>> node_select.lookup('Z')
        0
        """
        return super().get(key, 0)

    def sum(self) -> LinearExpr:
        """Sum all variables in an expression.

        Returns
        -------
        docplex.mp.linear.LinearExpr

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> node_select = add_variables(mdl, nodes, 'B', name='node-select')

        Sum all variables:

        >>> node_select.sum()
        docplex.mp.LinearExpr(node-select_A+node-select_B+node-select_C)
        """
        return self.model.sum_vars_all_different(self.values())

    def sum_squares(self) -> QuadExpr:
        """Sum squares of all variables in an expression.

        Returns
        -------
        docplex.mp.quad.QuadExpr

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> node_select = add_variables(mdl, nodes, 'B', name='node-select')

        Sum squares of all variables:

        >>> node_select.sum_squares()
        docplex.mp.quad.QuadExpr(node-select_A^2+node-select_B^2+node-select_C^2)
        """
        return self.model.sumsq(self.values())

    def dot(self, paramdict: ParamDict1D[Elem1DT, ParamT]) -> LinearExpr | ZeroExpr:
        """Sum the products of variables with corresponding coef from ParamDict1D, in an expression.

        Assumes the coef to be zero if not found in the ParamDict1D.

        Equivalent to::

          model.sum(paramdict.get(k, 0) * v for k, v in vardict.items())

        Parameters
        ----------
        paramdict : ParamDict1D
            ParamDict1D to be used for dot product.

        Returns
        -------
        docplex.mp.linear.LinearExpr or docplex.mp.linear.ZeroExpr

        Raises
        ------
        TypeError
            If the paramdict is not as instance of ParamDict1D.

        Notes
        -----
        This method is equivalent to using the matrix multiplication operator ``@``.

        Both ``ParamDict1D @ VarDict1D`` and ``VarDict1D @ ParamDict1D`` will also produce the same
        result.

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> nodes = IndexSet1D(['A', 'B', 'C'], name='node')

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> node_select = add_variables(mdl, nodes, 'B', name='node-select')

        Define parameter:

        >>> from opti_extensions import ParamDict1D
        >>> fixed_cost = ParamDict1D({'A': 100, 'B': 200})

        Compute dot product (three alternative ways):

        >>> node_select.dot(fixed_cost)
        docplex.mp.LinearExpr(100node-select_A+200node-select_B)

        >>> fixed_cost @ node_select
        docplex.mp.LinearExpr(100node-select_A+200node-select_B)

        >>> node_select @ fixed_cost
        docplex.mp.LinearExpr(100node-select_A+200node-select_B)
        """
        _validate_for_dot_1d(paramdict)
        return self.model.sum(paramdict.get(k, 0) * v for k, v in self.items())

    __matmul__ = dot

    __rmatmul__ = dot


class VarDictND(VarDictCore[ElemNDT, VarT], DictNDMixin[ElemNDT, VarT]):
    """Custom subclasses of `dict` to define DOcplex model variables with N-dim tuple keys.

    Parameters
    ----------
    docpx_var_dict : dict
        Dictionary of variable objects from docplex.
    indexset : IndexSetND
        Keys of dictionary encapsulated in IndexSetND.
    model : docplex.mp.model.Model
        DOcplex model associated with the variable objects.
    vartype : docplex.mp.vartype.VarType
        DOcplex VarType corresponding to the variable objects.
    value_name : str, optional
        Name to refer to variables - not used internally, and solely for user reference.
    """

    # Private attributes
    # ------------------
    # _indexset : IndexSetND
    #     Index-set of keys.

    __slots__ = ('_key_names', '_value_name')

    def __init__(
        self,
        docpx_var_dict: dict[ElemNDT, VarT],
        indexset: IndexSetND[ElemNDT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> None:
        self.key_names = indexset.names
        self.value_name = value_name

        super().__init__(docpx_var_dict, indexset=indexset, model=model, vartype=vartype)

    def __new__(
        cls,
        docpx_var_dict: dict[ElemNDT, VarT],
        indexset: IndexSetND[ElemNDT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> VarDictND[ElemNDT, VarT]:
        raise TypeError(
            'This class is not meant to be instantiated; VarDictND is built through the '
            'opti_extensions.docplex.add_variables function'
        )

    @classmethod
    def _create(
        cls,
        docpx_var_dict: dict[ElemNDT, VarT],
        indexset: IndexSetND[ElemNDT],
        /,
        *,
        model: Model,
        vartype: VarType,
        value_name: str | None = None,
    ) -> VarDictND[ElemNDT, VarT]:
        # Private method to construct VarDictND
        instance = super().__new__(cls)
        cls.__init__(
            instance, docpx_var_dict, indexset, model=model, vartype=vartype, value_name=value_name
        )
        return instance

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

    def lookup(self, *key: Any) -> VarT | Literal[0]:
        """Get the variable for the specified key, or zero if it is not found.

        Parameters
        ----------
        *key : key

        Returns
        -------
        docplex.mp.dvar.Var or ``0``

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> arc_flow = add_variables(mdl, arcs, 'C', ub=10, name='arc-flow')

        Lookup with keys:

        >>> arc_flow.lookup('A', 'B')
        docplex.mp.Var(type=C,name='arc-flow_A_B',ub=10)

        >>> arc_flow.lookup('X', 'Y')
        0
        """
        if any((isinstance(k, Iterable) and not isinstance(k, str)) for k in key):
            raise TypeError('lookup key must be scalars (no iterables except string)')
        if len(key) != self._indexset._tuplelen:
            raise ValueError('lookup key length must be the same as that of N-dim tuple keys')
        return super().get(cast('ElemNDT', key), 0)

    def sum(self, *pattern: Any) -> LinearExpr | ZeroExpr:
        """Sum all variables, or a subset based on wildcard pattern, in an expression.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        docplex.mp.linear.LinearExpr or docplex.mp.linear.ZeroExpr

        Raises
        ------
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> arc_flow = add_variables(mdl, arcs, 'C', ub=10, name='arc-flow')

        Sum all variables:

        >>> arc_flow.sum()
        docplex.mp.LinearExpr(arc-flow_A_B+arc-flow_B_C+arc-flow_C_B)

        Sum subset of variables having ``'B'`` at the second dimension index:

        >>> arc_flow.sum('*', 'B')
        docplex.mp.LinearExpr(arc-flow_A_B+arc-flow_C_B)

        Sum subset of variables having ``'Z'`` at the first dimension index:

        >>> arc_flow.sum('Z', '*')
        docplex.mp.ZeroExpr()
        """
        if pattern:
            return self.model.sum_vars_all_different(self.subset_values(*pattern))
        return self.model.sum_vars_all_different(self.values())

    def sum_squares(self, *pattern: Any) -> QuadExpr | ZeroExpr:
        """Sum squares of all variables, or a subset based on wildcard pattern, in an expression.

        Parameters
        ----------
        *pattern : Any, optional
            For subsets, the pattern requires one value for each dimension of the N-dim tuple key.
            The single-character string ``'*'`` (asterisk) can be used as a wildcard to represent
            all possible values for a dimension.

        Returns
        -------
        docplex.mp.quad.QuadExpr or docplex.mp.linear.ZeroExpr

        Raises
        ------
        TypeError
            If the pattern includes non-scalar(s).
        ValueError
            If the pattern is not the same as the length of N-dim tuple keys.
        ValueError
            If the pattern has no wildcard or all wildcards.

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> arc_flow = add_variables(mdl, arcs, 'C', ub=10, name='arc-flow')

        Sum squares of all variables:

        >>> arc_flow.sum_squares()
        docplex.mp.quad.QuadExpr(arc-flow_A_B^2+arc-flow_B_C^2+arc-flow_C_B^2)

        Sum squares of subset of variables having ``'B'`` at the second dimension index:

        >>> arc_flow.sum_squares('*', 'B')
        docplex.mp.quad.QuadExpr(arc-flow_A_B^2+arc-flow_C_B^2)

        Sum squares of subset of variables having ``'Z'`` at the first dimension index:

        >>> arc_flow.sum_squares('Z', '*')
        docplex.mp.ZeroExpr()
        """
        if pattern:
            return self.model.sumsq(self.subset_values(*pattern))
        return self.model.sumsq(self.values())

    def dot(self, paramdict: ParamDictND[ElemNDT, ParamT]) -> LinearExpr | ZeroExpr:
        """Sum the products of variables with corresponding coef from ParamDictND, in an expression.

        Assumes the coef to be zero if not found in the ParamDictND.

        Equivalent to::

          model.sum(paramdict.get(k, 0) * v for k, v in vardict.items())

        Parameters
        ----------
        paramdict : ParamDictND
            ParamDictND to be used for dot product; should have tuple keys of same length as
            VarDictND.

        Returns
        -------
        docplex.mp.linear.LinearExpr or docplex.mp.linear.ZeroExpr

        Raises
        ------
        TypeError
            If the paramdict is not as instance of ParamDictND.
        ValueError
            If the paramdict does not have tuple keys of same length as VarDictND.

        Notes
        -----
        This method is equivalent to using the matrix multiplication operator ``@``.

        Both ``ParamDictND @ VarDictND`` and ``VarDictND @ ParamDictND`` will also produce the same
        result.

        Examples
        --------
        Create DOcplex model:

        >>> from docplex.mp.model import Model
        >>> mdl = Model()

        Create index-set:

        >>> arcs = IndexSetND([('A', 'B'), ('B', 'C'), ('C', 'B')], names=['ori', 'des'])

        Add variables:

        >>> from opti_extensions.docplex import add_variables
        >>> arc_flow = add_variables(mdl, arcs, 'C', ub=10, name='arc-flow')

        Define parameter:

        >>> from opti_extensions import ParamDictND
        >>> cost = ParamDictND({('A', 'B'): 10, ('B', 'C'): 20})

        Compute dot product (three alternative ways):

        >>> arc_flow.dot(cost)
        docplex.mp.LinearExpr(10arc-flow_A_B+20arc-flow_B_C)

        >>> cost @ arc_flow
        docplex.mp.LinearExpr(10arc-flow_A_B+20arc-flow_B_C)

        >>> arc_flow @ cost
        docplex.mp.LinearExpr(10arc-flow_A_B+20arc-flow_B_C)
        """
        _validate_for_dot_Nd(self._indexset, paramdict)
        return self.model.sum(paramdict.get(k, 0) * v for k, v in self.items())

    __matmul__ = dot

    __rmatmul__ = dot
