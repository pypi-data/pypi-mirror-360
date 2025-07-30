import pytest

quboify = pytest.importorskip("quboify")

import comando
import comando.interfaces
import comando.interfaces.quboify


def test_quboify_problem():
    from comando import Component, DiscretizationParameters, System

    # Define Heater for this trivial test case
    class Heater(Component):
        def __init__(self, label):
            super().__init__(label)

            nom_eff = 0.9
            nom_max = 10

            out = self.make_operational_variable(
                "output",
                bounds=(0, nom_max),
                discretization=DiscretizationParameters(0, nom_max, 1),
                init_val=nom_max,
            )

            inp = self.add_expression("input", out / nom_eff)

            self.add_expression("output", out)

            # set connectors
            self.add_input("IN", inp)
            self.add_output("OUT", out)

    # Set up energy system
    from components.example_components import Consumer, Grid

    PG = Grid("Power", price=160, compensation=100, constrain_flow=True)
    H = Heater("H")
    C = Consumer("Consumer", "heat")
    comp = [PG, H, C]
    conn = {
        "Power_Bus": [PG.CONSUMPTION, H.IN],
        "Heat_Bus": [H.OUT, C.HEAT],
    }
    ES = System("Energy_System", comp, conn)

    # Define discretizations of non-binary variables
    for name, var in ES.operational_variables_dict.items():
        if name == "Power_consumption":
            var.discretization = DiscretizationParameters(0, 12, 1)

    # Define timesteps and scenarios
    ts = ["winter", "spring"]  # ['winter', 'spring', 'summer', 'autumn']
    scenarios = {"best": 0.1, "likely": 0.7}  # {'best': .1, 'likely': .7, 'worst': .2}

    # Define objective function
    from comando.utility import make_tac_objective

    # n is the assumed accounting period and i the interest rate
    d_obj, o_obj = make_tac_objective(ES, n=10, i=0.08)

    # Combine into comando.Problem
    # Operational parameter data is in XXX / h
    # if we consider 8760 timesteps we got one year
    # We scale the objective to million € / year
    P = ES.create_problem(
        d_obj * 1e-6, o_obj * 1e-6, (ts, 2), scenarios, name="Test_Problem"
    )

    # Define missing data
    P["Consumer_heat_demand"] = 2.4

    # Convert to quboify.Problem
    qubo = comando.interfaces.quboify.to_quboify(P)

    # Handle unset parameters
    qubo.get_parameters()
    parameters = {par.name: par.value for par in P.parameters}
    qubo.set_parameters(parameters)

    # Solve qubo
    solver = qubo.solver
    solutions = solver.solve_simulated_annealing(
        lambda_strategy="upper_bound_only_positive", num_reads=1000, annealing_time=100
    )

    # Evaluate solution
    solutions.best_solution
    solutions.best_solution_satisfies_constraints()
    solutions.solution_constraint_violations(solution=solutions.best_solution_object)
