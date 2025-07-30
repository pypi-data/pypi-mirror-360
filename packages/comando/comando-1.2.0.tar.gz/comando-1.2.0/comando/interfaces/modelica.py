"""Routines for translation to Modelica syntax."""

import comando.core
import comando.utility
from comando.utility import StrParser, _str_map, is_indexed, split


def raise_(ex):
    raise ex


modelica_str_map = {
    "LessThan": lambda lhs, rhs: raise_(
        NotImplemented("Modelica does not support inequality constraints!")
    ),
    "GreaterThan": lambda lhs, rhs: raise_(
        NotImplemented("Modelica does not support inequality constraints!")
    ),
    "Equality": lambda lhs, rhs: f"{lhs} = {rhs}",
    "exp": lambda arg: f"exp({arg})",
    "log": lambda arg: f"log({arg})",
    "Pow": lambda base, exponent: f"{base}^({exponent})",
}
for key in "()", "Add", "Neg", "Sub", "Mul", "Div", "Inv":
    modelica_str_map[key] = _str_map[key]


class ModelicaParser(StrParser):  # pylint: disable=too-few-public-methods
    """A class for parsing comando expressions to Modelica Syntax."""

    def __init__(self, sym_map):
        super().__init__(sym_map, modelica_str_map)


from enum import Enum

Modifier = Enum("modifier", ["parameter", "input", "output"])


def _entry(name, value=None, modifier=None, kind="Real"):
    """Create a string representation of a modelica symbol.

    For <kind="Real" or "Integer">, states are represented as
      <kind> state(start=<initial_value>, fixed=true)
    controls as
      input <kind> control(start=<initial_value_guess_if_available>)
    all algebraic variables as
      output <kind> var(start=<initial_value_guess_if_available>)

    NOTE: The `output` modifier may cause issues when using fmus
          generated from the resulting Modelica model in certain
          Programs, e.g., DyOS, if var is constant through some
          combination of equations!
    """
    if modifier:  # in {'parameter', 'input', 'output'}:
        entry = f"  {modifier.name} {kind} {name}"
    else:
        entry = f"  {kind} {name}"
    if value is not None:
        if kind == "Integer":
            value = int(value)  # Ensure appropriate value type
        # For states modifier == None, otherwise value is a guess
        entry += f"(start={value}{'' if modifier else ', fixed=true'})"
    return entry + ";\n"


def _data_entry(parameter, timesteps):
    """Helper function to include time-variable data."""
    import pandas as pd

    if isinstance(parameter.value.index, pd.MultiIndex):
        res = "  "
        for s, data in parameter.value.groupby(level=0):
            t = timesteps[s].cumsum()
            v = data.values
            table_entries = ";\n      ".join(f"{ti}, {vi}" for ti, vi in zip(t, v))
            res += f"""CombiTimeTable {parameter.name}_{s}(
    table=[ // Time (s), Value;
      {table_entries}
    ],
    tableOnFile=false,
    extrapolation=Extrapolation.HoldLastPoint,
    smoothness=Smoothness.ConstantSegments
  ) "data for parameter {parameter.name} in scenario {s}";\n\n  """
    else:
        t = timesteps.cumsum()
        v = parameter.value
        table_entries = ";\n      ".join(f"{ti}, {vi}" for ti, vi in zip(t, v))
        res = f"""  CombiTimeTable {parameter.name}(
    table=[ // Time (s), Value;
      {table_entries}
    ],
    tableOnFile=false,
    extrapolation=Extrapolation.HoldLastPoint,
    smoothness=Smoothness.ConstantSegments
  ) "data for parameter {parameter.name}";\n\n  """
    return res


Modelica_HEADER = """// This file was automatically generated via the COMANDO-modelica interface.
"""


def _imports_section(*modules, **options):
    modules = set(modules)
    if options.pop("use_time_variable_data", False):
        modules.add("Modelica.Blocks.Sources.CombiTimeTable")
        modules.add("Modelica.Blocks.Types.Extrapolation")
        modules.add("Modelica.Blocks.Types.Smoothness")

    if modules:
        return (
            "  "
            + "  ".join(f"import {module};\n" for module in sorted(modules))
            + "\n\n"
        )
    else:
        return ""


def _parameters_section(P, use_time_variable_data):
    """Generate the parameters section."""
    if P.scenarios:
        # one entry per scenario for each indexed parameter
        def _get_param_entries():
            for p in sorted(P.parameters, key=lambda p: p.name):
                if p.is_indexed:
                    if use_time_variable_data:
                        yield _data_entry(p, P.timesteps)
                    else:
                        for s in P.scenarios:
                            s_val = p.value[s]
                            yield _entry(
                                p.name + f"_{s}",
                                (
                                    s_val
                                    if isinstance(s_val, (int, float))
                                    else s_val[P.timesteps[s].index[0]]
                                ),
                                Modifier.input,
                            )
                else:
                    yield _entry(p.name, p.value, Modifier.input)

    else:

        def _get_param_entries():
            for p in sorted(P.parameters, key=lambda p: p.name):
                if p.is_indexed:
                    if use_time_variable_data:
                        yield _data_entry(p, P.timesteps)
                    else:
                        yield _entry(
                            p.name, p.value[P.timesteps.index[0]], Modifier.input
                        )
                    # raise NotImplementedError(err_msg)
                else:
                    yield _entry(p.name, p.value, Modifier.input)

    if P.parameters:
        return f"  // parameters\n{''.join(_get_param_entries())}\n"
    return ""


def _variables_section(P, controls):
    """Write the different 'VARIABLES' sections and variable bounds."""

    _bd = "binary design variables"
    _id = "integer design variables"
    _cd = "continuous design variables"
    _bo = "binary operational variables"
    _io = "integer operational variables"
    _co = "continuous operational variables"
    from comando.utility import evaluate

    var_types = {_bd: [], _id: [], _cd: [], _bo: [], _io: [], _co: []}

    for v in P.design_variables:  # Sort the variabes according to their domain
        if v.is_binary:
            var_types[_bd].append(v)
        elif v.is_integer:
            var_types[_id].append(v)
        else:
            var_types[_cd].append(v)

    for v in P.operational_variables:
        if v.is_binary:
            var_types[_bo].append(v)
        elif v.is_integer:
            var_types[_io].append(v)
        else:
            var_types[_co].append(v)

    if not controls:
        # Ensure there is at least one input
        dummy_input = comando.core.VariableVector("dummy_input")
        dummy_input.instantiate(P.index)
        controls = {dummy_input}
        var_types[_co].append(dummy_input)

    variables = ""
    # Design
    for v_type, kind in zip([_bd, _id, _cd], ["Integer", "Integer", "Real"]):
        vars = var_types[v_type]
        if vars:  # Only print this section if there are variables of this type
            var_entries = []
            for v in sorted(vars, key=lambda v: v.name):
                var_entries.append(_entry(v.name, v.value, Modifier.input, kind))
            variables += f"  // {v_type}\n{''.join(var_entries)}\n"

    # Operation
    for v_type, kind in zip([_bo, _io, _co], ["Integer", "Integer", "Real"]):
        vars = var_types[v_type]
        if vars:  # Only print this section if there are variables of this type
            var_entries = []
            for v in sorted(vars, key=lambda v: v.name):
                if v in P.states:
                    mod = None
                    init_state, *_ = P.states[v]
                    init_value = init_state.value
                else:
                    # Use first time value as initial value
                    init_value = (
                        v.value.groupby(level=0).head(1).droplevel(1)
                        if P.scenarios
                        else v.value.iloc[0]
                    )
                    # all controls are inputs, all algebraic variables are outputs
                    mod = Modifier.input if v in controls else Modifier.output

                if P.scenarios:
                    for s in P.scenarios:
                        try:
                            init_val = init_value[s]
                        except TypeError:
                            init_val = init_value
                        var_entries.append(
                            _entry(v.name + f"_{s}", init_val, mod, kind)
                        )
                else:
                    var_entries.append(_entry(v.name, init_value, mod, kind))
            variables += f"  // {v_type}\n{''.join(var_entries)}\n"

    dobj_init = evaluate(P.design_objective)
    t0 = (
        {s: P.timesteps[s].index[0] for s in P.scenarios}
        if P.scenarios
        else P.timesteps.index[0]
    )
    # objective definitions
    variables += (
        "  // objective\n"
        f"  Real d_obj(start={dobj_init});\n"
        + (
            "".join(
                f"  Real o_obj_{s}(start={evaluate(P.operational_objective, (s, t0[s]))});\n"
                for s in P.scenarios
            )
            if P.scenarios
            else f"  Real o_obj(start={evaluate(P.operational_objective, t0)});\n"
        )
        + (
            "".join(
                f"  Real o_obj_int_{s}(start=0, fixed=true);\n" for s in P.scenarios
            )
            if P.scenarios
            else "  Real o_obj_int(start=0, fixed=true);\n"
        )
        + f"  output Real obj(start={dobj_init});\n"
    )
    return variables


def _equations_section(P, ineqs, parse):
    """Generate a string representation of all equations."""
    from comando.utility import evaluate

    if not (P.states or P.constraints):
        return "\n\nequation\n\n  "  # for mandatory objective definitions

    t0 = (
        {s: P.timesteps[s].index[0] for s in P.scenarios}
        if P.scenarios
        else P.timesteps.index[0]
    )
    inequalities = (
        (
            "\n  // inequalities\n  "
            + "  ".join(
                (
                    "  ".join(
                        f"output Real {name}_{s}(start={evaluate(ineq, (s, t0[s]))});  "
                        f"// {c_id} for scenario {s}\n"
                        for s in P.scenarios
                    )
                    if P.scenarios and comando.utility.is_indexed(ineq)
                    else f"output Real {name}(start={evaluate(ineq, t0)});  // {c_id}\n"
                )
                for c_id, (ineq, name) in ineqs.items()
            )
        )
        if ineqs
        else ""
    )

    def eq(id):
        """Normalize the equation id if it doesn't fit Modelica syntax."""
        import re

        if re.match(r"^\w+$", id):
            eq_id = id
        else:
            eq_id = f"constraint_{eq.n}"
            eq.n += 1
        eq.map[eq_id] = id
        return eq_id

    eq.n = 0
    eq.map = {}

    equations = f"{inequalities}\nequation\n"
    if P.states:
        equations += "\n  // differential equations\n"
    for state, (_, der_state_var, _) in P.states.items():
        if P.scenarios:
            for s in P.scenarios:
                equations += f"  der({state.name}_{s}) = {der_state_var.name}_{s};\n"
        else:
            equations += f"  der({state.name}) = {der_state_var.name};\n"

    if P.constraints:
        equations += "\n  // constraints\n"
    for c_id, c in P.constraints.items():
        if not c.is_Equality:  # Define auxiliary variables for inequalities
            ineq, name = ineqs[c_id]
            if P.scenarios and comando.utility.is_indexed(ineq):
                for s in P.scenarios:
                    equations += f"  {name}_{s} = {parse(ineq, s)};  // {c_id} for scenario {s}\n"
            else:
                equations += f"  {name} = {parse(ineq)};  // {c_id}\n"
            continue

        if P.scenarios and comando.utility.is_indexed(c):
            for s in P.scenarios:
                equations += f"  {parse(c, s)};  // {c_id} for scenario {s}\n"
        else:
            equations += f"  {parse(c)};  // {c_id}\n"

    return equations


def _objective_section(P, parse):
    return (
        "\n  // objective definitions\n"
        f"  d_obj = {parse(P.design_objective)};  // design objective\n  "
        + (
            (
                "  ".join(
                    f"o_obj_{s} = {parse(P.operational_objective, s)};  "
                    f"// operational objective for scenario {s}\n"
                    for s in P.scenarios
                )
                + "  obj = d_obj + "
                + " + ".join(
                    f"{ws} * o_obj_int_{s}" for s, ws in P.scenario_weights.items()
                )
                + ";  // overall objective\n  "
                + "  ".join(f"der(o_obj_int_{s}) = o_obj_{s};\n" for s in P.scenarios)
            )
            if P.scenarios
            else (
                f"o_obj = {parse(P.operational_objective)};  // operational objective\n"
                "  der(o_obj_int) = o_obj;\n"
                "  obj = d_obj + o_obj_int;  // overall objective\n"
            )
        )
    )


def _create_sym_map(
    dvars=(),
    ovars=(),
    pars=(),
    scenarios=None,
    use_time_variable_data=False,
    sym_map=None,
):
    """Create a Modelica symbol map or populate an existing one with new symbols.

    Arguments
    ---------
    dvars : iterable
        design variables
    ovars : iterable
        operational variables
    pars : iterable
        parameters

    Returns
    -------
    sym_map : dict
        Symbol map with Modelica representation for each passed symbol.
    """
    import re
    from itertools import chain

    p = re.compile(r"(\w+)\[\(?'?(\w+)'?(?:, '?(\w+)'?)*\)?\]")

    if sym_map is None:
        sym_map = {}
    dpars, opars = split(pars, is_indexed)
    for sym in chain(dpars, dvars):
        sym_map[sym] = sym.name

    for sym in chain(opars, ovars):
        if scenarios and sym.is_indexed:
            sym_map[sym] = {s: f"{sym.name}_{s}" for s in scenarios}
        else:
            sym_map[sym] = f"{sym.name}"
    if use_time_variable_data:
        for p in opars:
            if scenarios:
                sym_map[p] = {s: n + ".y[1]" for s, n in sym_map[p].items()}
            else:
                sym_map[p] = sym_map[p] + ".y[1]"
    return sym_map


def write_mo_file(
    P, mo_file_path, controls, *modules, use_time_variable_data=False, precheck=False
):
    """Write a Modelica file based on the COMANDO Problem.

    Arguments
    ---------
    P : comando.Problem
        the problem to translate
    mo_file_path : str
        the path to the Modelica file to be created, i.e., <optional_path>\<class_name>.mo
    controls : list[comando.VariableVector]
        the operational variables to be treated as controls (i.e., inputs in Modelica terms)
    modules : tuple[str]
        additional module to be imported
    options : dict[str -> Any]
        additional options
    """
    import os

    if P.timesteps is None:
        raise RuntimeError(
            "Trying to generate a modelica file for a Problem without time-steps."
        )

    eqs = {}
    ineqs = {}
    n_ineqs = 0
    for c_id, c in P.constraints.items():
        if c.is_Equality:
            eqs[c_id] = c
        else:
            ineqs[c_id] = (c.lts - c.gts, f"inequality_{n_ineqs}")
            n_ineqs += 1

    _states = set(P.states)
    _controls = set()
    if isinstance(controls, (str, comando.core.Symbol)):  # single control
        controls = [controls]
    for control in controls:
        if isinstance(control, str):
            try:
                control = P[control]
            except KeyError:
                raise KeyError(f'"{control}" is not a valid symbol name.')
        if control not in P.operational_variables:
            raise RuntimeError(f'"{control}" is not an operational variable.')
        _controls.add(control)
    alg_vars = P.operational_variables - _states - _controls

    nEqs = len(eqs)
    nVars = len(alg_vars)

    if precheck:
        if nEqs > nVars:
            raise RuntimeError(
                f"System is overconstrained: nEqs ({nEqs}) > nVars ({nVars})!"
            )
        elif nEqs < nVars:
            raise RuntimeError(
                f"System is underconstrained: nEqs ({nEqs}) < nVars ({nVars})!"
            )
        else:
            import pandas as pd

            incidence = pd.DataFrame(
                [[int(v in eq.free_symbols) for v in alg_vars] for eq in eqs.values()],
                eqs,
                (v.name for v in alg_vars),
                int,
            )
            from numpy.linalg import matrix_rank

            rank = matrix_rank(incidence)
            if rank < nEqs:
                raise RuntimeError(
                    "System is structurally singular, incidence matrix:\n\n"
                    + str(incidence)
                )

    # Parsing setup
    sym_map = _create_sym_map(
        P.design_variables,
        P.operational_variables,
        P.parameters,
        P.scenarios,
        use_time_variable_data,
    )

    parse = ModelicaParser(sym_map)

    class_name = os.path.basename(mo_file_path).split(".")[0]
    with open(mo_file_path, "w") as f:
        f.write(Modelica_HEADER)
        f.write(f"\nmodel {class_name}\n\n")
        f.write(
            _imports_section(*modules, use_time_variable_data=use_time_variable_data)
        )
        f.write(_parameters_section(P, use_time_variable_data))
        f.write(_variables_section(P, _controls))
        f.write(_equations_section(P, ineqs, parse))
        f.write(_objective_section(P, parse))
        f.write(f"\nend {class_name};\n")
