import quboify
from sympy import Symbol, sympify

import comando


def to_quboify(problem: comando.Problem) -> quboify.Problem:
    P = problem

    # Variables
    variables = quboify.Symbols()

    for parameter in P.parameters:
        param = variables.add_parameter(name=parameter.name)

    for variable_vector in P.design_variables | P.operational_variables:
        for variable in (
            variable_vector if variable_vector.is_indexed else [variable_vector]
        ):
            variables.add_continuous_variable(
                name=variable.name,
                min_val=variable.lb,
                max_val=variable.ub,
                precision=1.0,
            )

    # Objective Functions
    objectives = quboify.ObjectiveFunctions()
    for objexpr in P.objective.args:
        obj_func = objectives.add_objective_function(sympify(objexpr))
        print("objf", obj_func.expression)

    # Constraints
    from itertools import product

    def indexed(con):
        return any(sym.is_indexed for sym in con.free_symbols)

    constraints = quboify.Constraints()
    for con_id, con in P.constraints.items():
        new_cons = []
        if indexed(con):
            indexed_combo = [
                {sym: [Symbol(el.name) for el in sym.elements]}
                for sym in con.free_symbols
                if sym.is_indexed
            ]
            keys, value_lists = zip(
                *[(k, v) for d in indexed_combo for k, v in d.items()]
            )
            combinations = [dict(zip(keys, combo)) for combo in product(*value_lists)]
            for sub_dict in combinations:
                new_cons.append(con.subs(sub_dict))
        else:
            new_cons = [con]
        for new_con in new_cons:
            new_con_obj = constraints.add_constraint(sympify(new_con))

    # Problem
    qubo_problem = quboify.Problem(variables, constraints, objectives)

    # Add utility functions to make parameters handling easier
    def get_parameters():
        return qubo_problem.symbols.parameters

    qubo_problem.get_parameters = get_parameters

    qubo_problem.solver = quboify.Solver(qubo_problem)

    return qubo_problem
