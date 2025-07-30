"""Tests for the Pyomo interface."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
from shutil import which

import pytest

import comando
from comando.interfaces.pyomo import to_pyomo
from tests import (
    NO_SCENARIOS,
    SCENARIO_LIST,
    TIMESTEP_RANGE,
    SCENARIO_DEPENDENT_TIMESTEPS,
)


@pytest.mark.parametrize(
    "scenarios, timesteps",  # for test_problem
    [(None, (["t1"], 1)), (["s1", "s2"], (["t1"], 1)), (["s1", "s2"], None)],
)
def test_pyomo_problem(test_problem, run_in_tmpdir):
    """Test the pyomo interface."""
    m = to_pyomo(test_problem)

    if which("baron") is None:
        pytest.skip("BARON is not installed")
    with run_in_tmpdir:
        m.solve("baron", options={"epsa": 1e-9})
    assert test_problem["x"].value == pytest.approx(1)
    for i in test_problem.index:
        assert test_problem["y"][i].value == pytest.approx(1)
    assert comando.utility.evaluate(test_problem.objective) == pytest.approx(0)


def test_pyomo_voll_problem(det_voll_problem):
    """Test the pyomo interface."""
    m = to_pyomo(det_voll_problem)
    assert len(m.x) + len(m.y) == det_voll_problem.num_vars
    assert len(m.constraints) == det_voll_problem.num_cons
    # TODO: Actually test whether the resulting object works as expected!


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
def test_pyomo_dynamic(dynamic_test_problem, run_in_tmpdir):
    for solver in ["cplex", "gurobi", "clp", "glpk", "ipopt", "baron", "couenne"]:
        if which(solver) is not None:
            break
    else:
        pytest.skip("No solver found!")

    m = to_pyomo(dynamic_test_problem)

    with run_in_tmpdir:
        m.solve(solver)

        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result

        # Solve with cyclic initial states (any of the following should work)
        dynamic_test_problem.initial_states["x"] = "nan"
        # dynamic_test_problem.initial_states['x'] = float('nan')
        # dynamic_test_problem.initial_states['x'] = comando.cyclic

        # NOTE: Updating only works if we don't change between cyclic and non-cyclic
        # m.update()
        m = to_pyomo(dynamic_test_problem)
        m.solve(solver)

        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result
