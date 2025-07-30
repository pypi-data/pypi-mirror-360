"""Tests for the GUROBI interface."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
import os
from contextlib import contextmanager
from shutil import which

import pytest

import comando
import comando.core
from comando.utility import silence
from tests import (
    NO_SCENARIOS,
    SCENARIO_DEPENDENT_TIMESTEPS,
    SCENARIO_LIST,
    TIMESTEP_RANGE,
)


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


@pytest.mark.skipif(which("gurobi") is None, reason="GUROBI is not installed")
@pytest.mark.parametrize(
    "scenarios, timesteps",
    [(None, (["t1"], 1)), (["s1", "s2"], (["t1"], 1)), (["s1", "s2"], None)],
)
def test_gurobi_solve(scenarios, timesteps):
    try:
        from comando.interfaces.gurobi import to_gurobi
    except ModuleNotFoundError as e:
        if "gurobipy" in str(e):
            print(
                "Module gurobipy cannot be found, you may have forgotten to install it!"
            )
            pytest.xfail("Module gurobipy cannot be found")
        raise

    x = comando.core.Variable("x", bounds=(-1.5, 1.5))
    x_squared = comando.core.Variable("x_squared", bounds=(-2.25, 2.25))
    y = comando.core.VariableVector("y", bounds=(-0.5, 2.5))
    # y_squared = comando.VariableVector('y_squared', bounds=(0.25, 6.25))
    p = comando.core.Parameter("p", 2)
    do = 1 - 2 * x + x_squared
    oo = 100 * (y**2 - 2 * y * x_squared + x_squared**2)
    constraints = {
        "c1": x * x_squared - 3 * x_squared + 3 * x - y <= 0,
        "c2": x + y - p <= 0,
        "x_squared": comando.Eq(x_squared, x**2),
    }
    P = comando.Problem(
        do, oo, constraints, timesteps=timesteps, scenarios=scenarios, name="Rosenbrok"
    )
    from gurobipy import GurobiError

    try:
        gm = to_gurobi(P)
    except GurobiError as e:
        pytest.xfail(str(e))
    with silence():
        gm.solve(NonConvex=2)

    assert x.value == pytest.approx(1)
    for yi in y:
        assert yi.value == pytest.approx(1)
    assert comando.utility.evaluate(P.objective) == pytest.approx(0, abs=1e-6)


@pytest.mark.skipif(which("gurobi") is None, reason="GUROBI is not installed")
@pytest.mark.parametrize(
    "scenarios, timesteps, initial_state",  # for dynamic_test_problem
    [
        (NO_SCENARIOS, TIMESTEP_RANGE, "Pnan"),
        (NO_SCENARIOS, TIMESTEP_RANGE, "P1"),
        (NO_SCENARIOS, TIMESTEP_RANGE, "V1,2"),
        (SCENARIO_LIST, TIMESTEP_RANGE, "Pnan"),
        (SCENARIO_LIST, TIMESTEP_RANGE, "P3"),
        (SCENARIO_LIST, TIMESTEP_RANGE, "V4,5"),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, "Pnan"),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, "P6"),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, "V7,8"),
    ],
    indirect=["initial_state"],
)
def test_gurobi_dynamic(dynamic_test_problem, run_in_tmpdir):
    try:
        from comando.interfaces.gurobi import to_gurobi
    except ModuleNotFoundError as e:
        if "gurobipy" in str(e):
            print(
                "Module gurobipy cannot be found, you may have forgotten to install it!"
            )
            pytest.xfail("Module gurobipy cannot be found")
        raise
    with run_in_tmpdir:
        from gurobipy import GurobiError

        try:
            gm = to_gurobi(dynamic_test_problem)
        except GurobiError as e:
            pytest.xfail(str(e))
        with silence():
            gm.solve()

        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result

        # Solve with cyclic initial states (any of the following should work)
        dynamic_test_problem.initial_states["x"] = "nan"
        # dynamic_test_problem.initial_states['x'] = float('nan')
        # dynamic_test_problem.initial_states['x'] = comando.cyclic

        gm = to_gurobi(dynamic_test_problem)
        with silence():
            gm.solve()

        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result
