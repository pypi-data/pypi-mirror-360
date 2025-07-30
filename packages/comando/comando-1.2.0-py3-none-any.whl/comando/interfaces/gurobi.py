"""COMANDO-GUROBI interface."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Alexander Holtwerth, Marco Langiu
from gurobipy import GRB, Model

import comando
import comando.core
from comando.utility import handle_state_equations, is_indexed, parse

gurobi_op_map = comando.base_op_map.copy()


def gurobipow(base, exp):
    """Compute valid powers for GUROBI."""
    try:  # both numeric or base is linear and exp is 2
        return base**exp
    except TypeError:
        if exp == 1:  # base ** 1 is not accepted, so we handle it manually
            return base
    raise ValueError(
        "Invalid power in GUROBI model. GUROBI only accepts "
        f"linear or quadratic expressions, but <{type(base)}> "
        f"{base} is being raised to the power of <{type(exp)}> "
        f"{exp}!"
    )


gurobi_op_map["Pow"] = gurobipow


def _translate(comando_var, gurobi_var, index=None):
    if comando_var.is_binary:
        gurobi_var.vtype = GRB.BINARY
    elif comando_var.is_integer:
        gurobi_var.vtype = GRB.INTEGER
    else:
        gurobi_var.vtype = GRB.CONTINUOUS
    gurobi_var.lb = comando_var.lb
    gurobi_var.ub = comando_var.ub
    value = comando_var.value if index is None else comando_var.value[index]
    gurobi_var.varName = comando_var.name
    # NOTE obj attribute is for objective coefficients!
    try:
        gurobi_var.start = value
    except ValueError as err:
        if "is not in domain" in str(err):
            gurobi_var.start = round(value)


class GurobiModel(Model):
    """An extension of the GUROBI model for COMANDO."""

    def __init__(self, P):
        super().__init__(P.name)
        self.P = P
        self.variable_initial_states = {}

    def __setattr__(self, attr, value):
        """Let GUROBI handle its own Model attributes but allow new ones."""
        if hasattr(Model, attr):
            super().__setattr__(attr, value)
        else:
            object.__setattr__(self, attr, value)

    def solve(self, **options):
        """Solve the GUROBI model."""
        for option, value in options.items():
            self.setParam(option, value)
        self.optimize()
        self.write_back()

    def write_back(self, P=None):
        """Write back results from gurobi model to a COMANDO problem."""
        if P is None:
            P = self.P
        index = list(P.index)
        for v in P.design_variables:
            v.value = self.getVarByName(v.name).x
        for v in P.operational_variables:
            v.value = {i: self.getVarByName(f"{v.name}[{i}]").x for i in index}
        for v, gv in self.variable_initial_states.items():
            v.value = gv.x


def _create_symmap(P, gm):
    index = P.index
    dvs = P.design_variables
    dv_names = sorted(dv.name for dv in dvs)
    pars = P.parameters
    ovs = P.operational_variables
    ov_names = sorted(ov.name for ov in ovs)

    x = gm.addVars(dv_names, name="dv")
    y = gm.addVars(ov_names, index, name="ov")
    sym_map = {}
    for p in pars:
        sym_map[p] = p.value
    for iv, *_ in P.states.values():
        if isinstance(iv, comando.core.Parameter):
            if iv.is_indexed:
                for iv_j in iv:
                    sym_map[iv_j] = iv_j.value
            else:
                sym_map[iv] = iv.value
        elif isinstance(iv, (comando.core.Variable, comando.core.VariableVector)):
            if iv.is_indexed:
                for iv_j in iv:
                    gvar = gm.addVar(name=iv_j.name)
                    _translate(iv_j, gvar)
                    sym_map[iv_j] = gvar
                    gm.variable_initial_states[iv_j] = gvar
            else:
                gvar = gm.addVar(name=iv.name)
                _translate(iv, gvar)
                sym_map[iv] = gvar
                gm.variable_initial_states[iv] = gvar
        else:
            msg = "Expected Variable or Parameter as initial state!"
            raise NotImplementedError(msg)
    for v in dvs:
        gvar = x[v.name]
        _translate(v, gvar)
        sym_map[v] = gvar
    for vv in ovs:
        gvars = {}
        if index.nlevels > 1:
            for i in index:
                gvar = y[(vv.name, *i)]
                _translate(vv[i], gvar)
                sym_map[vv[i]] = gvars[i] = gvar
        else:
            for i in index:
                gvar = y[vv.name, i]
                _translate(vv[i], gvar)
                sym_map[vv[i]] = gvars[i] = gvar
        sym_map[vv] = gvars

    # Raise an error if any of the parameters has no value
    miss = "\n\t".join(p.name for p in P.parameters if sym_map[p] is None)
    if miss:
        raise ValueError(f"Lacking data for parameter(s):\n\t{miss}")

    return sym_map


def to_gurobi(P):
    """Create a Gurobi model from the optimization problem P."""
    gm = GurobiModel(P)

    sym_map = _create_symmap(P, gm)

    def parse2gurobi(expr, idx=None):
        """Parse expressions from COMANDO to GUROBI."""
        return parse(expr, sym_map, gurobi_op_map, idx=idx)

    # Adding objective
    do = parse2gurobi(P.design_objective)
    ts = P.timesteps
    if ts is None:
        oo = sum(
            p * parse2gurobi(P.operational_objective, s)
            for s, p in P.scenario_weights.items()
        )
    elif P.scenarios is None:
        oo = sum(dt * parse2gurobi(P.operational_objective, t) for t, dt in ts.items())
    else:
        oo = sum(
            p
            * sum(
                dt * parse2gurobi(P.operational_objective, (s, t))
                for t, dt in ts[s].items()
            )
            for s, p in P.scenario_weights.items()
        )

    gm.setObjective(do + oo, GRB.MINIMIZE)

    # Add constraints defined by components and their connections
    from operator import itemgetter

    constraints = dict(sorted(P.constraints.items(), key=itemgetter(0)))

    for con_id, con in constraints.items():
        if comando.utility.get_vars(con):
            if is_indexed(con):
                for idx in P.index:
                    gm.addConstr(parse2gurobi(con, idx), con_id + "_" + str(idx))
            else:
                gm.addConstr(parse2gurobi(con), con_id)
        else:  # Only numerical parameters, constraint can be checked here
            if is_indexed(con):
                vals = parse2gurobi(con)
                if all(vals):  # all values True
                    pass
                else:  # Some violations
                    raise comando.ImpossibleConstraintException(
                        f"Constraint '{con_id}' is violated "
                        f"at indices {[*vals[vals == False].keys()]}!"
                    )
            else:
                if parse2gurobi(con):
                    pass
                else:
                    raise comando.ImpossibleConstraintException(
                        f"Constraint '{con_id}' is violated!"
                    )

    handle_state_equations(P, lambda c_id, c: gm.addConstr(parse2gurobi(c), c_id))

    gm.update()

    return gm
