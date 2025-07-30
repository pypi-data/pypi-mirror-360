"""Tests for the MAiNGO API interface."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
import pytest

import comando
import comando.utility
from tests import (
    NO_SCENARIOS,
    SCENARIO_DEPENDENT_TIMESTEPS,
    SCENARIO_LIST,
    TIMESTEP_RANGE,
    missing_module,
)


@pytest.mark.skipif(missing_module("maingopy"), reason="maingopy is not installed")
@pytest.mark.parametrize(
    "scenarios, timesteps",  # for test_problem
    [(None, (["t1"], 1)), (["s1", "s2"], (["t1"], 1)), (["s1", "s2"], None)],
)
def test_maingo_solve(test_problem):
    from comando.interfaces.maingo_api import MaingoProblem
    from comando.utility import define_function

    tp = test_problem

    # testing the inclusion of user defined functions into Maingo by adding a
    # trivial constraint which includes MAiNGO's lb_func
    lb_func = define_function("lb_func", lambda x, lb: comando.Max(x, lb))
    x = tp["x"]  # getting variable x ∈ [-1.5, 1.5]
    # adding a trivial constraint (always satisfied)
    tp.constraints["c3"] = (2 + x) / lb_func(2 + x, comando.EPS) <= 1

    mp = MaingoProblem(tp)
    solver, ret = mp.solve(epsilonA=1e-5)
    assert ret == comando.interfaces.maingo_api.GLOBALLY_OPTIMAL
    assert solver.get_cpu_solution_time() <= solver.get_wallclock_solution_time()
    assert solver.get_final_abs_gap() < 1e-5
    assert solver.get_final_LBD() == 0
    assert solver.get_final_rel_gap() == 1  # as LBD is 0 this is  UBD / UBD
    assert solver.get_iterations() >= solver.get_LBP_count()
    assert solver.get_iterations() >= solver.get_UBP_count()
    assert solver.get_iterations() >= solver.get_max_nodes_in_memory()
    sp = solver.get_solution_point()
    assert sp[0] == pytest.approx(1, abs=1e-3) == comando.utility.evaluate(tp["x"])
    for yi, spi in zip(tp["y"], sp[1:]):
        assert spi == pytest.approx(1, abs=1e-3) == comando.utility.evaluate(yi)
    exp_vals = iter(solver.evaluate_model_at_solution_point())
    assert (
        next(exp_vals)
        == pytest.approx(0, abs=1e-3)
        == comando.utility.evaluate(tp.objective)
    )
    # First-stage constraint
    assert next(exp_vals) == pytest.approx(
        comando.utility.evaluate(tp.constraints["c3"].lts)
        - comando.utility.evaluate(tp.constraints["c3"].gts),
        abs=1e-6,
    )
    # Second-stage constraints
    for con_val, exp_val in zip(
        comando.utility.evaluate(tp.constraints["c1"].lhs), exp_vals
    ):
        assert con_val == pytest.approx(exp_val, abs=1e-6)
    for con_val, exp_val in zip(
        comando.utility.evaluate(tp.constraints["c2"].lhs), exp_vals
    ):
        assert con_val == pytest.approx(exp_val, abs=1e-6)
    assert len(solver.evaluate_additional_outputs_at_solution_point()) == 0
    assert (
        solver.get_objective_value()
        == pytest.approx(0, abs=1e-5)
        == comando.utility.evaluate(tp.objective)
    )


@pytest.mark.skipif(missing_module("maingopy"), reason="maingopy is not installed")
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
def test_maingo_dynamic(dynamic_test_problem, run_in_tmpdir):
    from comando.interfaces.maingo_api import MaingoProblem

    with run_in_tmpdir:
        mp = MaingoProblem(dynamic_test_problem)
        mp.solve(epsilonA=1e-5)

        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result

        # Solve with cyclic initial states (any of the following should work)
        dynamic_test_problem.initial_states["x"] = "nan"
        # dynamic_test_problem.initial_states['x'] = float('nan')
        # dynamic_test_problem.initial_states['x'] = comando.cyclic

        mp = MaingoProblem(dynamic_test_problem)
        mp.solve(epsilonA=1e-5)
        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result


@pytest.mark.skipif(missing_module("maingopy"), reason="maingopy is not installed")
@pytest.mark.parametrize(
    "scenarios, timesteps",  # for test_problem
    [(["s1", "s2"], (["t1"], 1)), (["s1", "s2"], None)],
)
def test_maingo_two_stage_problem(test_problem, run_in_tmpdir):
    import sys

    import maingopy

    from comando.interfaces.maingo_api import MaingoTwoStageProblem

    print(maingopy, sys.path)
    P = test_problem
    problem = MaingoTwoStageProblem(P)

    # Test the attributes of the problem instance
    assert problem.P == P
    assert {*problem.x} == P.design_variables
    assert {*problem.y} == P.operational_variables
    assert {*problem.p, *problem.c} == P.parameters

    # Test the initialization of the problem instance
    assert problem.Nx == len(P.design_variables)
    assert problem.Ny == len(P.operational_variables)
    assert all(problem.w == P.scenario_weights.values)

    # Test the solve method of the problem instance
    solver, ret = problem.solve(epsilonA=1e-5)
    assert ret == comando.interfaces.maingo_api.GLOBALLY_OPTIMAL
    # assert solver.get_cpu_solution_time() <= solver.get_wallclock_solution_time()
    assert solver.get_final_abs_gap() < 1e-5
    assert solver.get_final_LBD() == 0
    assert solver.get_final_rel_gap() == 1
