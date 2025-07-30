import pytest

import comando
import comando.core
from tests import (
    NO_SCENARIOS,
    NO_TIMESTEPS,
    SCENARIO_DEPENDENT_TIMESTEPS,
    SCENARIO_LIST,
    TIMESTEP_RANGE,
)

CYCLIC = float("nan")
PARAMETER = comando.core.Parameter("x_init_par")
VARIABLE = comando.core.Variable("x_init_var")


@pytest.mark.parametrize(
    "scenarios, timesteps, initial_state",  # for dynamic_test_problem
    [
        (NO_SCENARIOS, NO_TIMESTEPS, CYCLIC),
        (NO_SCENARIOS, NO_TIMESTEPS, PARAMETER),
        (NO_SCENARIOS, NO_TIMESTEPS, VARIABLE),
        (NO_SCENARIOS, TIMESTEP_RANGE, CYCLIC),
        (NO_SCENARIOS, TIMESTEP_RANGE, PARAMETER),
        (NO_SCENARIOS, TIMESTEP_RANGE, VARIABLE),
        (SCENARIO_LIST, NO_TIMESTEPS, CYCLIC),
        (SCENARIO_LIST, NO_TIMESTEPS, PARAMETER),
        (SCENARIO_LIST, NO_TIMESTEPS, VARIABLE),
        (SCENARIO_LIST, TIMESTEP_RANGE, CYCLIC),
        (SCENARIO_LIST, TIMESTEP_RANGE, PARAMETER),
        (SCENARIO_LIST, TIMESTEP_RANGE, VARIABLE),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, CYCLIC),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, PARAMETER),
        (SCENARIO_LIST, SCENARIO_DEPENDENT_TIMESTEPS, VARIABLE),
    ],
)
def test_initial_states_setter_getter(dynamic_test_problem):
    P = dynamic_test_problem
    x_0 = P.initial_states["x"]

    # set all initial states to 1
    P.initial_states["x"] = 1
    if P.scenarios:
        # Since the initial state is a scalar, x_0 has a scalar value
        x_0.value = 1

        # now change one of the initial states to be cyclic (represented by a nan value)
        P.initial_states["x"] = ["nan", 2]
        assert x_0[SCENARIO_LIST[0]].value != x_0[SCENARIO_LIST[0]].value
        assert x_0[SCENARIO_LIST[1]].value == 2

        # Alternative way of setting initial state
        x_0.value = {SCENARIO_LIST[0]: 1, SCENARIO_LIST[1]: "nan"}
        assert x_0[SCENARIO_LIST[0]].value == 1
        assert x_0[SCENARIO_LIST[1]].value != x_0[SCENARIO_LIST[1]].value
    else:
        assert x_0.value == 1
