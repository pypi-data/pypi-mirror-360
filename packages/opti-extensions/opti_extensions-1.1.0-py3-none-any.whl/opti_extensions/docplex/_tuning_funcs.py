# Copyright 2025 Samarth Mistry
# This file is part of the `opti-extensions` package, which is released under
# the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0).

"""Tuning tool functionality."""

from io import TextIOBase
from operator import attrgetter
from pathlib import Path
from typing import Any, TextIO

from docplex.mp.model import Model
from docplex.mp.params.parameters import Parameter
from docplex.mp.utils import DOcplexException


def get_name(parameter: Any) -> str:
    """Get name of the parameter in the form a string.

    Parameters
    ----------
    parameter : DOcplex parameter or CPLEX legacy parameter object

    Returns
    -------
    str
        Parameter name.
    """
    # Cannot typecheck function arg since CPLEX legacy parameter class is not exposed to the public
    # API
    if isinstance(parameter, Parameter):
        name: str = parameter.qualified_name
        return name.split('.', maxsplit=1)[1]
    else:
        return str(parameter).split('.', maxsplit=1)[1]


def _tune(
    input: Model | list[str],
    /,
    *,
    log_output: bool | str | TextIO | None = True,
    overall_timelimit_sec: int | float | str | None = None,
    tuning_timelimit_sec: int | float | str | None = None,
    overall_timelimit_det: int | float | str | None = None,
    tuning_timelimit_det: int | float | str | None = None,
    display_level: int | None = None,
    measure: int | None = None,
    repeat: int | None = None,
    fixed_params_and_values: dict[str, int | float | bool | str] | None = None,
) -> dict[str, int | float]:
    """Run the CPLEX tuning tool for a DOcplex model or a batch of models (stored as files).

    Parameters
    ----------
    input : docplex.mp.model.Model or list[str]
        Either the DOcplex model or list of filepaths of the models to be tuned.
    log_output : bool or str or stream object, optional
        Log output switch, in one of the following forms:

        * ``True`` or ``'1'`` or ``'stdout'`` or ``'sys.stdout'``: Log is output to stdout.
        * ``'stderr'`` or ``'sys.stderr'``: Log is output to stderr.
        * ``False`` or ``'0'`` or ``None``: No log output.
        * File path (in form of str): Log is output to the file.
        * Stream object (a file-like object with a write method and a flush method): Log is output
          to the stream object.

        Default is ``True``.
    overall_timelimit_sec : int or float or str, optional
        Time limit for the tuning tool, in terms of seconds. Corresponds to the CPLEX parameter
        `timelimit`.
    tuning_timelimit_sec : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of seconds. Corresponds to the CPLEX
        parameter `tune.timelimit`.
    overall_timelimit_det : int or float or str, optional
        Time limit for the tuning tool, in terms of deterministic ticks. Corresponds to the CPLEX
        parameter `dettimelimit`.
    tuning_timelimit_det : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of deterministic ticks. Corresponds to
        the CPLEX parameter `tune.dettimelimit`.
    display_level : int, optional
        Level of information reported by the tuning tool as it works. Corresponds to the CPLEX
        parameter `tune.display`.
    measure : int, optional
        Measure for evaluating progress when a batch of models is being tuned. Only applicable when
        tuning a batch of models. Corresponds to the CPLEX parameter `tune.measure`.
    repeat : int, optional
        Number of times tuning is to be repeated on reordered versions of a given model. Only
        applicable when tuning a single model. Corresponds to the CPLEX parameter `tune.repeat`.
    fixed_params_and_values : dict, optional
        Set of parameters and their values that should be respected by the tuning tool, in form of a
        dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.) as
        keys and parameter values as values. Default is ``None``.

    Returns
    -------
    dict
        Set of performance-improving parameters and their values identified by tuning tool, in form
        of a dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.)
        as keys and parameter values as values.

    Raises
    ------
    ValueError
        If both overall_timelimit_sec and overall_timelimit_det are specified.
    ValueError
        If both tuning_timelimit_sec and tuning_timelimit_det are specified.
    ValueError
        If an invalid value is specified for any tuning parameter in function arguments:
        overall_timelimit_sec, tuning_timelimit_sec, overall_timelimit_det, tuning_timelimit_det,
        display_level, measure, repeat.
    ValueError
        If an invalid parameter or value is specified is fixed_params_and_values.
    """
    # Validation checks
    if isinstance(log_output, str) and log_output in ('1', '0'):
        log_output = bool(int(log_output))
    if not (
        log_output is None
        or isinstance(log_output, bool | str | TextIOBase)
        or (hasattr(log_output, 'write') and hasattr(log_output, 'flush'))
    ):
        raise TypeError('`log_output` should be a bool or str or stream object')
    if overall_timelimit_sec and overall_timelimit_det:
        raise ValueError(
            'Only one of `overall_timelimit_sec` and `overall_timelimit_det` can be set at a time'
        )
    if tuning_timelimit_sec and tuning_timelimit_det:
        raise ValueError(
            'Only one of `tuning_timelimit_sec` and `tuning_timelimit_det` can be set at a time'
        )
    if fixed_params_and_values is None:
        fixed_params_and_values = {}
    if not isinstance(fixed_params_and_values, dict):
        raise TypeError('`fixed_params_and_values` should be a dict')

    # Process input
    match input:
        case Model():
            batch_mode = False
            model = input
            # Register prior state so it can be restored post-tuning
            prior_log_output = model.log_output
            prior_params = {
                get_name(param): param.get()
                for param in model.parameters.generate_nondefault_params()
            }
            model.parameters.reset_all()
        case list():
            batch_mode = True
            model = Model()  # Dummy model to be used as proxy for accessing CPLEX env

    # Set params in the DOcplex model for the tuning tool
    tuning_args = {
        'overall_timelimit_sec': (overall_timelimit_sec, model.parameters.timelimit),
        'tuning_timelimit_sec': (tuning_timelimit_sec, model.parameters.tune.timelimit),
        'overall_timelimit_det': (overall_timelimit_det, model.parameters.dettimelimit),
        'tuning_timelimit_det': (tuning_timelimit_det, model.parameters.tune.dettimelimit),
        'display_level': (display_level, model.parameters.tune.display),
        'measure': (measure, model.parameters.tune.measure),
        'repeat': (repeat, model.parameters.tune.repeat),
    }
    tuning_params = {}
    for arg_name, (arg_val, param) in tuning_args.items():
        if arg_val is not None:
            try:
                param.set(arg_val)
            except (ValueError, DOcplexException):
                raise ValueError(f'Value {arg_val} for `{arg_name}` is invalid') from None
        tuning_params[get_name(param)] = param.get()

    # Sync DOcplex model params with the underlying CPLEX engine
    model.apply_parameters()

    # Access the underlying CPLEX engine through legacy API
    cplex = model.get_cplex()

    # Fixed params to be set directly in the CPLEX engine
    if fixed_params_and_values:
        param_set = cplex.create_parameter_set()
        for fixed_name, fixed_val in fixed_params_and_values.items():
            try:
                param = attrgetter(fixed_name)(model.parameters)
            except AttributeError:
                raise ValueError(
                    f'`{fixed_name}` in `fixed_parameters_and_values` is not a valid parameter'
                ) from None
            else:
                if param.accept_value(fixed_val):
                    param_set.add(attrgetter(fixed_name)(cplex.parameters), fixed_val)
                else:
                    # Provide a more informative error message since the one from CPLEX engine
                    # is ambiguous
                    raise ValueError(
                        f'Value {fixed_val} for `{fixed_name}` in `fixed_parameters_and_values` is '
                        'invalid'
                    )
    else:
        param_set = None

    if log_output:
        model.log_output = log_output
        stream = model.context.solver.log_output_as_stream

        if cplex.get_problem_name() != model.name:
            cplex.set_problem_name(model.name)

        # Log tuning tool params
        log_header = 'Tuning tool parameters:\n'
        for tuning_name, tuning_val in tuning_params.items():
            if not (tuning_name == 'tune.repeat' and batch_mode) and not (
                tuning_name == 'tune.measure' and not batch_mode
            ):
                log_header += f'   {tuning_name:<40} {tuning_val}\n'

        # Log fixed params
        log_header += '\nFixed parameters:\n'
        if fixed_params_and_values:
            for fixed_name, fixed_val in fixed_params_and_values.items():
                log_header += f'   {fixed_name:<40} {fixed_val}\n'
        else:
            log_header += '   None\n'

        stream.write(log_header)
        stream.flush()

    # Run the tuning tool
    if batch_mode:
        status = cplex.parameters.tune_problem_set(input, fixed_parameters_and_values=param_set)
    else:
        status = cplex.parameters.tune_problem(param_set)

    improving_params_and_values = {}
    # Exclude from coverage since there's no clear way to deterministically test the tuning tool
    # across multiple CPLEX versions. Also, it's not critical as it's only populating a dict.
    for param, param_value in cplex.parameters.get_changed():  # pragma: no cover
        param_name = get_name(param)
        if param_name not in fixed_params_and_values and param_name not in tuning_params:
            improving_params_and_values[param_name] = param_value

    if log_output:
        # Log status
        log_footer = f'Tuning tool status: {cplex.parameters.tuning_status[status]}\n\n'

        # Log improving params
        if improving_params_and_values:  # pragma: no cover
            log_footer += 'Tuned parameters:\n'
            for tuned_name, tuned_val in improving_params_and_values.items():
                log_footer += f'   {tuned_name:<40} {tuned_val}\n'
        else:
            log_footer += 'The tuning tool could not find a better set of parameters\n'

        stream.write(log_footer)
        stream.flush()
        try:
            stream.custom_close()
        except AttributeError:
            pass

    # Post-tuning cleanup
    if batch_mode:
        # Terminate the dummy model
        model.end()
    else:
        # Restore prior state
        model.log_output = prior_log_output
        for tuning_param_name in tuning_params:
            attrgetter(tuning_param_name)(model.parameters).reset()
        for prior_name, prior_val in prior_params.items():
            attrgetter(prior_name)(model.parameters).set(prior_val)
        model.apply_parameters()

    return improving_params_and_values


def tune(
    model: Model,
    *,
    log_output: bool | str | TextIO | None = True,
    overall_timelimit_sec: int | float | str | None = None,
    tuning_timelimit_sec: int | float | str | None = None,
    overall_timelimit_det: int | float | str | None = None,
    tuning_timelimit_det: int | float | str | None = None,
    display_level: int | None = None,
    repeat: int | None = None,
    fixed_params_and_values: dict[str, int | float | bool | str] | None = None,
) -> dict[str, int | float]:
    """Run tuning tests on a DOcplex model to search for performance-improving parameter settings.

    This function is a wrapper around CPLEX's tuning tool. Refer to the CPLEX user manual for more
    details about this functionality.

    Parameters
    ----------
    model : docplex.mp.model.Model
        DOcplex model.
    log_output : bool or str or stream object, optional
        Log output switch, in one of the following forms:

        * ``True`` or ``'1'`` or ``'stdout'`` or ``'sys.stdout'``: Log is output to stdout.
        * ``'stderr'`` or ``'sys.stderr'``: Log is output to stderr.
        * ``False`` or ``'0'`` or ``None``: No log output.
        * File path (in form of str): Log is output to the file.
        * Stream object (a file-like object with a write method and a flush method): Log is output
          to the stream object.

        Default is ``True``.
    overall_timelimit_sec : int or float or str, optional
        Time limit for the tuning tool, in terms of seconds. Corresponds to the CPLEX parameter
        `timelimit`.
    tuning_timelimit_sec : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of seconds. Corresponds to the CPLEX
        parameter `tune.timelimit`.
    overall_timelimit_det : int or float or str, optional
        Time limit for the tuning tool, in terms of deterministic ticks. Corresponds to the CPLEX
        parameter `dettimelimit`.
    tuning_timelimit_det : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of deterministic ticks. Corresponds to
        the CPLEX parameter `tune.dettimelimit`.
    display_level : int, optional
        Level of information reported by the tuning tool as it works. Corresponds to the CPLEX
        parameter `tune.display`.
    repeat : int, optional
        Number of times tuning is to be repeated on reordered versions of a given model. Corresponds
        to the CPLEX parameter `tune.repeat`.
    fixed_params_and_values : dict, optional
        Set of parameters and their values that should be respected by the tuning tool, in form of a
        dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.) as
        keys and parameter values as values. Default is ``None``.

    Returns
    -------
    dict
        Set of performance-improving parameters and their values identified by tuning tool, in form
        of a dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.)
        as keys and parameter values as values.

    Raises
    ------
    ValueError
        If both overall_timelimit_sec and overall_timelimit_det are specified.
    ValueError
        If both tuning_timelimit_sec and tuning_timelimit_det are specified.
    ValueError
        If an invalid value is specified for any tuning parameter in function arguments:
        overall_timelimit_sec, tuning_timelimit_sec, overall_timelimit_det, tuning_timelimit_det,
        display_level, repeat.
    ValueError
        If an invalid parameter or value is specified is fixed_params_and_values.

    See Also
    --------
    batch_tune : For tuning a batch of models (stored as files).

    Notes
    -----
    Any CPLEX parameters set for the model before passing it to this function will be disregarded.
    """
    if not isinstance(model, Model):
        raise TypeError('`model` should be docplex.mp.model.Model')

    return _tune(
        model,
        log_output=log_output,
        overall_timelimit_sec=overall_timelimit_sec,
        tuning_timelimit_sec=tuning_timelimit_sec,
        overall_timelimit_det=overall_timelimit_det,
        tuning_timelimit_det=tuning_timelimit_det,
        display_level=display_level,
        repeat=repeat,
        fixed_params_and_values=fixed_params_and_values,
    )


def batch_tune(
    *model_files: str,
    log_output: bool | str | TextIO | None = True,
    overall_timelimit_sec: int | float | str | None = None,
    tuning_timelimit_sec: int | float | str | None = None,
    overall_timelimit_det: int | float | str | None = None,
    tuning_timelimit_det: int | float | str | None = None,
    display_level: int | None = None,
    measure: int | None = None,
    fixed_params_and_values: dict[str, int | float | bool | str] | None = None,
) -> dict[str, int | float]:
    """Run tuning tests on a batch of models to search for performance-improving parameter settings.

    This function is a wrapper around CPLEX's tuning tool. Refer to the CPLEX user manual for more
    details about this functionality.

    Parameters
    ----------
    *model_files : str
        Path of file containing the model. Supported formats are ``.mps``, ``.lp``, and ``.sav``
        (compressed files with extensions ``.gz`` and ``.bz2`` are also supported).
    log_output : bool or str or stream object, optional
        Log output switch, in one of the following forms:

        * ``True`` or ``'1'`` or ``'stdout'`` or ``'sys.stdout'``: Log is output to stdout.
        * ``'stderr'`` or ``'sys.stderr'``: Log is output to stderr.
        * ``False`` or ``'0'`` or ``None``: No log output.
        * File path (in form of str): Log is output to the file.
        * Stream object (a file-like object with a write method and a flush method): Log is output
          to the stream object.

        Default is ``True``.
    overall_timelimit_sec : int or float or str, optional
        Time limit for the tuning tool, in terms of seconds. Corresponds to the CPLEX parameter
        `timelimit`.
    tuning_timelimit_sec : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of seconds. Corresponds to the CPLEX
        parameter `tune.timelimit`.
    overall_timelimit_det : int or float or str, optional
        Time limit for the tuning tool, in terms of deterministic ticks. Corresponds to the CPLEX
        parameter `dettimelimit`.
    tuning_timelimit_det : int or float or str, optional
        Time limit for each test of the tuning tool, in terms of deterministic ticks. Corresponds to
        the CPLEX parameter `tune.dettimelimit`.
    display_level : int, optional
        Level of information reported by the tuning tool as it works. Corresponds to the CPLEX
        parameter `tune.display`.
    measure : int, optional
        Measure for evaluating progress. Corresponds to the CPLEX parameter `tune.measure`.
    fixed_params_and_values : dict, optional
        Set of parameters and their values that should be respected by the tuning tool, in form of a
        dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.) as
        keys and parameter values as values. Default is ``None``.

    Returns
    -------
    dict
        Set of performance-improving parameters and their values identified by tuning tool, in form
        of a dict having parameter names (as str such as 'lpmethod', 'mip.limits.cutpasses', etc.)
        as keys and parameter values as values.

    Raises
    ------
    FileNotFoundError
        If model file is not found.
    ValueError
        If both overall_timelimit_sec and overall_timelimit_det are specified.
    ValueError
        If both tuning_timelimit_sec and tuning_timelimit_det are specified.
    ValueError
        If an invalid value is specified for any tuning parameter in function arguments:
        overall_timelimit_sec, tuning_timelimit_sec, overall_timelimit_det, tuning_timelimit_det,
        display_level, measure.
    ValueError
        If an invalid parameter or value is specified is fixed_params_and_values.

    See Also
    --------
    tune : For tuning a DOcplex model.

    Notes
    -----
    Although the tuning tool can tune a single model through this function, it cannot access the
    CPLEX parameter `tune.repeat`. Use the ``opti_extensions.docplex.tune`` function instead to use
    this parameter.
    """
    for file in model_files:
        if isinstance(file, Model):
            raise TypeError(
                'batch_tune does not work with DOcplex models - use model files such as .mps, .lp, '
                'or .sav (compressed files with extensions .gz and .bz2 are also supported)'
            )
        if not isinstance(file, str):
            raise TypeError(f'File path `{file}` should be a string')
        if not Path(file).is_file():
            raise FileNotFoundError(f'File `{file}` not found')

    return _tune(
        list(model_files),
        log_output=log_output,
        overall_timelimit_sec=overall_timelimit_sec,
        tuning_timelimit_sec=tuning_timelimit_sec,
        overall_timelimit_det=overall_timelimit_det,
        tuning_timelimit_det=tuning_timelimit_det,
        display_level=display_level,
        measure=measure,
        fixed_params_and_values=fixed_params_and_values,
    )
