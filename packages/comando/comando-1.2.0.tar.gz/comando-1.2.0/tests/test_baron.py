"""Tests for the BARON interface."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
import os
from shutil import which

import pytest

import comando
from comando.interfaces.baron import solve
from tests import (
    NO_SCENARIOS,
    SCENARIO_LIST,
    TIMESTEP_RANGE,
    SCENARIO_DEPENDENT_TIMESTEPS,
)


@pytest.mark.skipif(which("baron") is None, reason="BARON is not installed")
@pytest.mark.parametrize(
    "scenarios, timesteps",  # for test_problem
    [(None, (["t1"], 1)), (["s1", "s2"], (["t1"], 1)), (["s1", "s2"], None)],
)
def test_baron_solve(test_problem, run_in_tmpdir):
    name = test_problem.name
    with run_in_tmpdir:
        solve(test_problem, reuse=False, MaxTime=1, times=False, epsa=1e-9)
        assert os.path.isfile(f"{name}.res.lst")
        assert os.path.isfile(f"{name}.sum.lst")
        assert not os.path.isfile(f"{name}.tim.lst")  # explicitly turned off!
    assert test_problem["x"].value == pytest.approx(1)
    for yi in test_problem["y"]:
        assert yi.value == pytest.approx(1)
    assert comando.utility.evaluate(test_problem.objective) == pytest.approx(0)


@pytest.mark.skipif(which("baron") is None, reason="BARON is not installed")
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
def test_baron_dynamic(dynamic_test_problem, run_in_tmpdir):
    with run_in_tmpdir:
        solve(dynamic_test_problem, reuse=False, MaxTime=1, times=False, epsa=1e-9)
        tmpdir = os.getcwd()
        logfile = os.path.join(tmpdir, dynamic_test_problem.name + ".baron.log")
        assert os.path.exists(logfile)
        with open(logfile, "r") as lf:
            for line in lf.readlines():
                if "*** Licensing error ***" in line:
                    pytest.skip("Baron uses demo-licence, only!")
        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result
        # if dynamic_test_problem.initial_states['x'].is_Variable:
        #     print(dynamic_test_problem.initial_states['x'].value)
        #     print(f'expected: {expected}')
        #     print(f'result: {result}')
        #     pytest.xfail("The previous assert holds, however this is because the variable initial state is handled like a parameter, i.e., its value is taken as fixed and not optimized. This is an open TODO!")

        # Solve with cyclic initial states (any of the following should work)
        dynamic_test_problem.initial_states["x"] = "nan"
        # dynamic_test_problem.initial_states['x'] = float('nan')
        # dynamic_test_problem.initial_states['x'] = comando.cyclic
        solve(dynamic_test_problem, reuse=False, MaxTime=1, times=False, epsa=1e-9)
        expected, result = dynamic_test_problem.compare()
        assert pytest.approx(expected) == result
