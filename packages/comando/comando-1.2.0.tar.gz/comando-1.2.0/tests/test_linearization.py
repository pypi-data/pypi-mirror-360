"""Tests for automatic linearization routines."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu, David Shu
import pytest

from comando import System
from comando.core import Variable, VariableVector
from comando.linearization import _is_linear
from components.example_components import Demand, Source
from examples.IES.IES_components import Boiler


def test_is_linear():
    from comando import Domain

    b = Variable("b", domain=Domain.INTEGER, bounds=(0, 1))
    x = Variable("x", domain=Domain.REAL, bounds=(0, 10))
    y = Variable("y", domain=Domain.REAL, bounds=(-5, 5))
    vv = VariableVector("vv")
    assert _is_linear(x + b + y)
    assert not _is_linear(x * b)
    assert not _is_linear(x**y)
    assert not _is_linear(vv * vv)


def test_linearization(clear_components):
    """Check if both convex_combination and multiple_choice result in the same
    expected result.
    """
    G = Source("Gas")
    B = Boiler("Boiler")
    H = Demand("Heat")
    connections = {"gas supply": [G.OUT, B.IN], "demand satisfaction": [B.OUT, H.IN]}
    ES = System("sys", components=[G, B, H], connections=connections)
    for name in ["investment_costs", "fixed_costs", "variable_costs"]:
        ES.add_expression(name, ES.aggregate_component_expressions(name))

    n = 10
    i = 0.08
    af = ((1 + i) ** n * i) / ((1 + i) ** n - 1)  # annuity factor
    ic = ES.get_expression("investment_costs")
    fc = ES.get_expression("fixed_costs")
    vc = ES.get_expression("variable_costs")
    d_obj = af * ic + fc
    o_obj = vc
    P = ES.create_problem(d_obj, o_obj, timesteps=[range(3), 8760], name="P")
    data = {"Gas_price": 0.3, "Heat_demand": (1, 1.5, 2)}
    for param, value in data.items():
        P[param] = value

    # calculate for convex combination method
    lin_opts = dict(method="convex_combination", n_bp=3)
    from comando.linearization import linearize

    P_lin = linearize(P, **lin_opts)
    from comando.interfaces.pyomo import to_pyomo

    m = to_pyomo(P_lin)

    from pyomo.common.errors import ApplicationError

    try:
        m.solve("cplex", keepfiles=False, options={"mipgap": 0})
    except ApplicationError:
        from tests import skip_long

        if skip_long:
            pytest.skip("Skipping long running tests...")
        from pyomo.opt.parallel.manager import ActionManagerError

        try:
            m.solve("cplex", remote=True, options={"mipgap": 0})
        except ActionManagerError as e:
            if "[]" in str(e):
                pytest.xfail("NEOS is unavailable")

    assert m.x["Boiler_Qdot_out_nom"]() == pytest.approx(2)
    assert m.objective() == pytest.approx(4427.527, rel=1e-2)

    # NOTE: Due to the linearization we get an error for the boiler output
    #       at t=1

    # calculate for multiple choice method
    lin_opts["method"] = "multiple_choice"
    P_lin = linearize(P, **lin_opts)
    m = to_pyomo(P_lin)

    from pyomo.common.errors import ApplicationError

    try:
        m.solve("cplex", keepfiles=False, options={"mipgap": 0})
    except ApplicationError:
        from tests import skip_long

        if skip_long:
            pytest.skip("Skipping long running tests...")
        try:
            m.solve("cplex", remote=True, options={"mipgap": 0})
        except ActionManagerError as e:
            if "[]" in str(e):
                pytest.xfail("NEOS is unavailable")

    assert m.x["Boiler_Qdot_out_nom"]() == pytest.approx(2)
    assert m.objective() == pytest.approx(4427.527, rel=1e-2)


def test_piecewise_linear_components(clear_components):
    from comando.utility import make_tac_objective
    from components.example_components import LinearConverter

    # From sass2020model
    investment_costs = {100: 27.6807, 2000: 86.955}
    part_load = {0.22608: 0.2, 1: 1}

    B = LinearConverter("B", investment_costs, part_load, 0.015, 0.8)
    # When running interactively you can check variables and constraints:
    # B.design_variables
    # B.operational_variables
    # B.constraints_dict

    G = Source("Gas")
    H = Demand("Heat")
    connections = {"gas supply": [G.OUT, B.IN], "demand satisfaction": [B.OUT, H.IN]}
    ES = System("Sys2", components=[G, B, H], connections=connections)
    P = ES.create_problem(*make_tac_objective(ES), (range(1, 4), 8760), name="")

    demand = (1000, 1500, 2000)
    data = {"Gas_price": 0.3, "Heat_demand": demand}
    for param, value in data.items():
        P[param] = value
    # When running interactively you can data is set correctly:
    P.data

    from tests import skip_long

    if skip_long:
        pytest.skip("Skipping long running tests...")

    def fallback():
        from pyomo.opt.parallel.manager import ActionManagerError

        from comando.interfaces.pyomo import to_pyomo

        try:
            pm = to_pyomo(P)
            pm.solve("cplex", remote=True, options={"mipgap": 0})
        except ActionManagerError as e:
            if "[]" in str(e):
                pytest.xfail("NEOS is unavailable")

    try:  # If you have gurobi...
        from gurobipy import GurobiError

        from comando.interfaces.gurobi import to_gurobi

        try:
            gm = to_gurobi(P)  # TODO: handle P.name = None
            gm.solve()
        except GurobiError:
            fallback()
    except ModuleNotFoundError:
        fallback()

    # The resulting solution is imported back into COMANDO and can be accessed:
    P.design
    P.operation
