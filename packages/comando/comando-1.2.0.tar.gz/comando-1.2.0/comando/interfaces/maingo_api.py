"""API interface for MAiNGO."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
from collections import OrderedDict, defaultdict
from functools import reduce
from itertools import islice
from operator import attrgetter

namegetter = attrgetter("name")
is_Eq = attrgetter("is_Equality")

import maingopy

import comando.core

FEASIBLE_POINT = maingopy.FEASIBLE_POINT
GLOBALLY_OPTIMAL = maingopy.GLOBALLY_OPTIMAL
LANG_ALE = maingopy.LANG_ALE
LANG_GAMS = maingopy.LANG_GAMS
LANG_NONE = maingopy.LANG_NONE

import comando
from comando import BINARY, INTEGER, REAL
from comando.utility import get_index, handle_state_equations, is_indexed, split

d_map = {
    REAL: maingopy.VT_CONTINUOUS,
    INTEGER: maingopy.VT_BINARY,
    BINARY: maingopy.VT_INTEGER,
}

maingo_API_op_map = {
    "Abs": maingopy.fabs,
    "Pow": maingopy.pow,
    "acos": maingopy.acos,
    "acquisition_function": maingopy.acquisition_function,
    "arh": maingopy.arh,
    "asin": maingopy.asin,
    "atan": maingopy.atan,
    "bounding_func": maingopy.bounding_func,
    "bstep": maingopy.bstep,
    "cheb": maingopy.cheb,
    "cos": maingopy.cos,
    "cosh": maingopy.cosh,
    "cost_function": maingopy.cost_function,
    "cost_turton": maingopy.cost_turton,
    "coth": maingopy.coth,
    "covariance_function": maingopy.covariance_function,
    "enthalpy_of_vaporization": maingopy.enthalpy_of_vaporization,
    "erf": maingopy.erf,
    "erfc": maingopy.erfc,
    "euclidean_norm_2d": maingopy.euclidean_norm_2d,
    "exp": maingopy.exp,
    "expx_times_y": maingopy.expx_times_y,
    "fabs": maingopy.fabs,
    "fabsx_times_x": maingopy.fabsx_times_x,
    "fstep": maingopy.fstep,
    "gaussian_probability_density_function": maingopy.gaussian_probability_density_function,
    "iapws": maingopy.iapws,
    "ideal_gas_enthalpy": maingopy.ideal_gas_enthalpy,
    "inv": maingopy.inv,
    "lb_func": maingopy.lb_func,
    "lmtd": maingopy.lmtd,
    "log": maingopy.log,
    "Max": lambda *args: reduce(maingopy.max, args),
    "Min": lambda *args: reduce(maingopy.min, args),
    "neg": maingopy.neg,
    "norm2": maingopy.norm2,
    "nrtl_G": maingopy.nrtl_G,
    "nrtl_Gdtau": maingopy.nrtl_Gdtau,
    "nrtl_Gtau": maingopy.nrtl_Gtau,
    "nrtl_dGtau": maingopy.nrtl_dGtau,
    "nrtl_dtau": maingopy.nrtl_dtau,
    "nrtl_tau": maingopy.nrtl_tau,
    "p_sat_ethanol_schroeder": maingopy.p_sat_ethanol_schroeder,
    "pos": maingopy.pos,
    "pow": maingopy.pow,
    "regnormal": maingopy.regnormal,
    "rho_liq_sat_ethanol_schroeder": maingopy.rho_liq_sat_ethanol_schroeder,
    "rho_vap_sat_ethanol_schroeder": maingopy.rho_vap_sat_ethanol_schroeder,
    "rlmtd": maingopy.rlmtd,
    "saturation_temperature": maingopy.saturation_temperature,
    "sin": maingopy.sin,
    "sinh": maingopy.sinh,
    "sqr": maingopy.sqr,
    "sqrt": maingopy.sqrt,
    "squash_node": maingopy.squash_node,
    "sum_div": maingopy.sum_div,
    "tan": maingopy.tan,
    "tanh": maingopy.tanh,
    "ub_func": maingopy.ub_func,
    "vapor_pressure": maingopy.vapor_pressure,
    "xexpax": maingopy.xexpax,
    "xlog": maingopy.xlog,
    "xlog_sum": maingopy.xlog_sum,
}


def floor_substitute(x, LB, UB):
    from numpy import floor

    lb = int(floor(LB))
    ub = int(floor(UB))
    return maingopy.max(
        x - 1, lb + sum(maingopy.fstep(x - i) for i in range(lb + 1, ub + 1))
    )


maingo_API_op_map["floor_substitute"] = floor_substitute


def const_fun(expr):
    """Convert a COMANDO backend constant to a MAiNGO constant."""
    return float(expr)
    # return maingopy.FFVar(float(expr))


def MAiNGO_var(v, branching_priorities):
    """Create a MAiNGO variable from a COMANDO variable."""
    try:  # if v is an element of an indexed variable, default to parent prio
        prio = branching_priorities.get(v.parent, 1)
        # prio = branching_priorities.get(v, prio))  # own or parent
        prio = max(branching_priorities.get(v, 1), prio)  # use max
        # prio = branching_priorities.get(v, 0) + prio  # use sum
    except AttributeError:
        prio = branching_priorities.get(v, 1)  # get own priority
    return maingopy.OptimizationVariable(
        maingopy.Bounds(*v.bounds), d_map[v.domain], prio, v.name
    )


def _pop_cons(con_dict, subset):
    return {con_id: con_dict.pop(con_id) for con_id in con_dict if con_id in subset}


def sorted_cons(cons):
    """Sort constraints alphabetically by name."""
    return {con_id: cons[con_id] for con_id in sorted(cons)}


def _order(cons, relaxation_only, squash):
    cons_ineq, cons_eq = split(cons, is_Eq)
    cons_ineqRelOnly = _pop_cons(cons_ineq, relaxation_only)
    cons_squash = _pop_cons(cons_ineq, squash)
    cons_eqRelOnly = _pop_cons(cons_eq, relaxation_only)

    # Sort constraints to get identical order in logs on repeated runs
    cons_ineq = sorted_cons(cons_ineq)
    cons_squash = sorted_cons(cons_squash)
    cons_eq = sorted_cons(cons_eq)
    cons_ineqRelOnly = sorted_cons(cons_ineqRelOnly)
    cons_eqRelOnly = sorted_cons(cons_eqRelOnly)

    return dict(
        ineq=cons_ineq,
        squash=cons_squash,
        eq=cons_eq,
        ineqRelOnly=cons_ineqRelOnly,
        eqRelOnly=cons_eqRelOnly,
    )


def _split_des_op_cons(mp):
    """Split design operational constraints into separate dictionaries."""
    return map(
        lambda cons: _order(cons, mp.relaxation_only, mp.squash),
        split(mp.P.constraints, is_indexed),
    )


def solve(problem, **options):
    """Solve the problem with the given options.

    Options
    -------
    epsilonA : double
        Absolute optimality tolerance, i.e., termination when (UBD-LBD) <
        BAB_epsilon_a.

    epsilonR : double
        Relative optimality tolerance, i.e., termination when (UBD-LBD) <
        BAB_epsilon_r * UBD.

    deltaIneq : double
        Absolute feasibility tolerance for inequality constraints (i.e.,
        constraint is considered satisfied if gi_(x)<=UBP_delta_ineq.

    deltaEq : double
        Absolute feasibility tolerance for equality constraints (i.e.,
        constraint is considered satisfied if abs(hi_(x))<=UBP_delta_eq.

    relNodeTol : double
        Relative tolerance for minimum node size.

    BAB_maxNodes : unsigned
        Maximum number of nodes (i.e., solver terminates when more than
        BAB_maxnodes are held in memory; used to avoid excessive branching)

    BAB_maxIterations : unsigned
        Maximum number of iterations (i.e., maximum number of nodes visited
        in the Branch-and-Bound tree)

    maxTime : unsigned
        CPU time limit in seconds.

    confirmTermination : bool
        Whether to ask the user before terminating when reaching time,
        node, or iteration limits.

    terminateOnFeasiblePoint : bool
        Whether to terminate as soon as the first feasible point was found
        (no guarantee of global or local optimality!)

    targetLowerBound : double
        Target value for the lower bound on the optimal objective. MAiNGO
        terminates once LBD>=targetLowerBound (no guarantee of global or
        local optimality!)

    targetUpperBound : double
        Target value for the upper bound on the optimal objective. MAiNGO
        terminates once UBD<=targetUpperBound (no guarantee of global or
        local optimality!)

    infinity : double
        User definition of infinity (used to initialize UBD and LBD)
        [currently cannot be set by the user via set_option].

    PRE_maxLocalSearches : unsigned
        Number of local searches in the multistart heuristic during
        preprocessing at the root node.

    PRE_obbtMaxRounds : unsigned
        Maximum number of rounds of optimization-based range reduction
        (OBBT; cf., e.g., Gleixner et al., J. Glob. Optim. 67 (2017) 731;
        maximizing and minimizing each variable subject to relaxed
        constraints) at the root node. If >=1 and a feasible point is
        found during multistart, one round of OBBT using an objective cut
        (f_cv<=UBD) is conducted as well.

    PRE_pureMultistart : bool
        Whether to perform a multistart only. A B&B tree will not be
        constructed and no lower bounding problems will be solved.

    BAB_nodeSelection : babBase::enums::NS
        How to select the next node to process. See documentation of
        babBase::enums::NS for possible values.

    BAB_branchVariable : babBase::enums::BV
        Which dimension to branch in for the current node. See
        documentation of babBase::enums::BV for possible values.

    BAB_alwaysSolveObbt : bool
        Whether to solve OBBT (feasibility- and, once a feasible point has
        been found, also optimality-based) at every BaB node.

    BAB_dbbt : bool
        Whether to do a single round of duality based bound tightening
        (DBBT, cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19 (1995) 551). If
        false, no DBBT is used. If true, multipliers from CPLEX are used to
        tighten bounds (essentially for free). we tried additional rounds
        but without reasonable improvement.

    BAB_probing : bool
        Whether to do probing (cf. Ryoo&Sahinidis, Comput. Chem. Eng. 19
        (1995) 551) at every node (can only be done if BAB_DBBT_maxrounds
        >= 1)

    BAB_constraintPropagation : bool
        Whether to do constraint propagation. If false, no constraint
        propagation is executed.

    LBP_solver : lbp::LBP_SOLVER
        Solver for solution of lower bounding problems.

    LBP_linPoints : lbp::LINP
        At which points to linearize for affine relaxation. See
        documentation of lbp::LINP for possible values.

    LBP_subgradientIntervals : bool
        Whether to use the heuristic to improve McCormick relaxations by
        tightening the range of each factor with the use of subgradients
        (cf. Najman & Mitsos, JOGO 2019)

    LBP_obbtMinImprovement : double
        How much improvement needs to be achievable (relative to initial
        diameter) to conduct OBBT for a variable.

    LBP_activateMoreScaling : unsigned
        Number of consecutive iterations without LBD improvement needed to
        activate more aggressive scaling in LP solver (e.g., CPLEX)

    LBP_addAuxiliaryVars : bool
        Whether to add auxiliary variables for common factors in the lower
        bounding DAG/problem.

    LBP_minFactorsForAux : unsigned
        Minimum number of common factors to add an auxiliary variable.

    LBP_maxNumberOfAddedFactors : unsigned
        Maximum number of added factor as auxiliaries.

    MC_mvcompUse : bool
        Whether to use multivariate composition theorem for computing
        McCormick relaxations (see MC++ documentation for details)

    MC_mvcompTol : double
        (see MC++ documentation for details)

    MC_envelTol : double
        (see MC++ documentation for details)

    UBP_solverPreprocessing : ubp::UBP_SOLVER
        Solver to be used during pre-processing (i.e., multistart). See
        documentation of ubp::UBP_SOLVER for possible values.

    UBP_maxStepsPreprocessing : unsigned
        Maximum number of steps the local solver is allowed to take in each
        local run during multistart in pre-processing.

    UBP_maxTimePreprocessing : double
        Maximum CPU time the local solver is allowed to take in each local
        run during multistart in pre-processing. Usually, this should only
        be a fall-back option to prevent truly getting stuck in local
        solution.

    UBP_solverBab : ubp::UBP_SOLVER
        Solver to be used during Branch-and-Bound. See documentation of
        ubp::UBP_SOLVER for possible values.

    UBP_maxStepsBab : unsigned
        Maximum number of steps the local solver is allowed to take at each
        BaB node.

    UBP_maxTimeBab : double
        Maximum CPU time the local solver is allowed to take at each BaB
        node. Usually, this should only be a fall-back option to prevent
        truly getting stuck in local solution.

    UBP_ignoreNodeBounds : bool
        Flag indicating whether the UBP solvers should ignore the box
        constraints of the current node during the B&B (and consider only
        the ones of the root node instead).

    EC_nPoints : unsigned
        Number of points on the Pareto front to be computed in
        epsilon-constraint method (only available via the C++ API)

    BAB_verbosity : VERB
        How much output to print from Branch & Bound solver. Possible
        values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

    LBP_verbosity : VERB
        How much output to print from Lower Bounding Solver. Possible
        values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

    UBP_verbosity : VERB
        How much output to print from Upper Bounding Solver. Possible
        values are VERB_NONE (=0), VERB_NORMAL (=1), VERB_ALL (=2)

    BAB_printFreq : unsigned
        After how many iterations to print progress on screen
        (additionally, a line is printed when a new incumbent is found)

    BAB_logFreq : unsigned
        Like BAB_printFreq, but for log.

    writeLog : bool
        Whether to write a log file (named bab.log)

    writeToLogSec : unsigned
        Write to log file after a given ammount of CPU seconds.

    writeResFile : bool
        Whether to write an additional file containing non-standard
        information about the solved model.

    writeCsv : bool
        Whether to write a csv-log file (named bab.csv). Currently, this
        only include time, LBD, UBD, and final output.

    PRE_printEveryLocalSearch : bool
        Whether to print every run during multistart at the root node.

    writeToOtherLanguage : PARSING_LANGUAGE
        Write to a file in a different modeling language.

    File name options added for convenience
    ---------------------------------------

    iterations_csv_file_name, json_file_name, log_file_name,
    result_file_name, solution_and_statistics_csv_file_name : str
        names for the respective files generated by MAiNGO, paths are
        interpreted as relative to the current working directory.

    Returns
    -------
    solver : MAiNGO solver object
        A solver object that can be queried for solve related information
        and adjust different settings:

        * solver.evaluate_additional_outputs_at_point(point)
        * solver.evaluate_additional_outputs_at_solution_point()
        * solver.evaluate_model_at_point(point)
        * solver.evaluate_model_at_solution_point()
        * solver.get_LBP_count()
        * solver.get_UBP_count()
        * solver.get_cpu_solution_time()
        * solver.get_final_LBD()
        * solver.get_final_abs_gap()
        * solver.get_final_rel_gap()
        * solver.get_iterations()
        * solver.get_max_nodes_in_memory()
        * solver.get_objective_value()
        * solver.get_solution_point()
        * solver.get_status()
        * solver.get_wallclock_solution_time()
        * solver.read_settings('settings.txt')
        * solver.set_iterations_csv_file_name('iterations.csv')
        * solver.set_json_file_name('results.json')
        * solver.set_log_file_name('results.log')
        * solver.set_model(myMAiNGOmodel)
        * solver.set_option(option, value)
        * solver.set_result_file_name('res.txt')
        * solver.set_solution_and_statistics_csv_file_name('sol.csv')
        * solver.solve()
        * solver.write_model_to_file_in_other_language('ALE', 'prob.ale')

    status : MAiNGO RETCODE
        Return code for the solution, possible values are:

        * GLOBALLY_OPTIMAL
        * INFEASIBLE
        * FEASIBLE_POINT
        * NO_FEASIBLE_POINT_FOUND
        * BOUND_TARGETS
        * NOT_SOLVED_YET
        * JUST_A_WORKER_DONT_ASK_ME
    """
    problem.branching_priorities = problem._check_prios(
        options.pop("branching_priorities", {})
    )
    solver = maingopy.MAiNGO(problem)
    lang = options.pop("writeToOtherLanguage", LANG_NONE)
    if lang is None:
        lang = LANG_NONE
    if lang not in {LANG_ALE, LANG_GAMS, LANG_NONE}:
        try:  # whether a string was given
            lang = globals().get(f"LANG_{lang.upper()}")
        except KeyError:
            raise ValueError(
                f"Language {lang} is not implemented! "
                "Possible values for writeToOtherLanguage are"
                " ALE, GAMS or NONE!"
            )
    if lang != LANG_NONE:
        ending = {LANG_ALE: ".ale", LANG_GAMS: ".gms"}[lang]
        solver.write_model_to_file_in_other_language(lang, problem.P.name + ending)

    # Handle special options for adjusting default file names
    for file_name_option in [
        "iterations_csv_file_name",
        "json_file_name",
        "log_file_name",
        "result_file_name",
        "solution_and_statistics_csv_file_name",
    ]:
        file_name = options.pop(file_name_option, "")
        if file_name:
            getattr(solver, "set_" + file_name_option)(file_name)

    for option, value in options.items():
        if not solver.set_option(option, value):
            raise ValueError(f'Option "{option}" is not recognized!')
        print(option, value)

    status = solver.solve()
    if status in {FEASIBLE_POINT, GLOBALLY_OPTIMAL}:
        for var, val in zip(problem.yield_vars(), solver.get_solution_point()):
            var.value = val
    return solver, status


class MaingoProblem(maingopy.MAiNGOmodel):
    """Initialize a MAiNGO Model from a COMANDO Problem.

    Arguments
    ---------
    P : comando.Problem
        A COMANDO problem that is to be translated to MAiNGO data structures.
    relaxation_only : set
        constraint ids that are to be treated as relaxation only
    squash : set
        constraint ids that are to be treated as relaxation only
    outputs : Mapping
        Mapping from textual description to expressions of interest for output
    use_cse : bool (default: True)
        Whether to use common subexpression elimination to represent
        reoccurring expressions with intermediate variables
    """

    def __init__(self, P, relaxation_only=None, squash=None, output=None, use_cse=True):
        super().__init__()
        # NOTE: it would make sense if the OptimizationVariable objects and the
        #       vars passed to the evaluate function were the same objects!
        #       This would allow to build a symbol mapping once and just store
        #       the MAiNGO equivalent of objective and constraints.
        # self.sym_map = {}
        # for p in P.parameters:  # translate parameters (scalars and vectors)
        #     try:  # treating the parameter as a vector
        #         mpars = {}
        #         for i, pi in p.expansion.items():
        #             mpars[pi] = self.sym_map[pi] = pi.value
        #         self.sym_map[p] = mpars
        #     except AttributeError:  # Parameter is scalar
        #         self.sym_map[p] = p.value
        # for v in P.design_variables:  # translate scalar variables
        #     sym_map[v] = MAiNGO_var(v)
        # for vv in P.operational_variables:
        #     mvars = {}
        #     for i, v in vv.expansion.items():  # translate vector variables
        #         mvars[v] = self.sym_map[v] = MAiNGO_var(v)
        #     self.sym_map[vv] = mvars

        # Then we could just do all parsing once at this point and be done...:
        # self.obj = parse(P.objective, sym_map)
        # self.cons = {c_id: parse(c, sym_map) for c_id, c in P.constraints}
        # self.states = ...  # TODO: Differential state discretization

        # ... But that's not the case, so we define an order via generators...
        self.P = P

        # def yield_pars():
        #     for p in P.parameters:
        #         if p.is_indexed:
        #             yield from p
        #         else:
        #             yield p
        # self.yield_pars = yield_pars

        from operator import attrgetter

        name_attr = attrgetter("name")
        self.dvs = sorted(self.P.design_variables, key=name_attr)
        self.ovs = sorted(self.P.operational_variables, key=name_attr)

        def yield_vars():
            yield from self.dvs
            for st in P.index:
                for y_i in self.ovs:
                    yield y_i[st]
            for x0, *_ in P.states.values():
                if isinstance(x0, (comando.core.Variable, comando.core.VariableVector)):
                    if x0.is_indexed:
                        yield from x0.expansion
                    else:
                        yield x0

        self.yield_vars = yield_vars
        # ... and delay sym map and parser creation to _make_sym_map!

        self._initial_point = [v.value for v in self.yield_vars()]

        self.relaxation_only = set() if relaxation_only is None else relaxation_only
        self.squash = set() if squash is None else squash
        self.output = dict() if output is None else output

        self.use_cse = use_cse

    def _make_sym_map(self, vars):
        self.sym_map = {}
        for p in self.P.parameters:  # translate parameters (scalars & vectors)
            try:  # treating the parameter as a vector
                mpars = {}
                for i, pi in p.expansion.items():
                    mpars[i] = self.sym_map[pi] = maingopy.FFVar(pi.value)
                self.sym_map[p] = mpars
            except AttributeError:  # Parameter is scalar
                self.sym_map[p] = maingopy.FFVar(p.value)

        var_iter = iter(vars)
        for v in self.dvs:  # translate scalar variables
            self.sym_map[v] = next(var_iter)
        # A bit more complicated since we want the order given by yield_vars:
        # first we prepare empty dicts for each variable...
        for vv in self.ovs:
            self.sym_map[vv] = {}
        # ...then we fill in the dicts and definitions for individual variables
        for st in self.P.index:
            for vv in self.ovs:
                self.sym_map[vv][st] = self.sym_map[vv[st]] = next(var_iter)

        for iv, *_ in self.P.states.values():
            if isinstance(iv, comando.core.Parameter):
                if iv.is_indexed:
                    for iv_j in iv:
                        self.sym_map[iv_j] = maingopy.FFVar(iv_j.value)
                else:
                    self.sym_map[iv] = maingopy.FFVar(iv.value)
            elif isinstance(iv, (comando.core.Variable, comando.core.VariableVector)):
                if iv.is_indexed:
                    for iv_j in iv:
                        self.sym_map[iv_j] = next(var_iter)
                else:
                    self.sym_map[iv] = next(var_iter)
            else:
                msg = "Expected Variable or Parameter as initial state!"
                raise NotImplementedError(msg)

        def parse(expr, i=None):
            """Parse from COMANDO to MAiNGO."""
            try:
                return comando.utility.parse(
                    expr, self.sym_map, maingo_API_op_map, i, const_fun
                )
            except Exception as e:
                print("\nParsing to MAiNGO raised ", e)

                print("\nindex was ", i)

                print("\nexpression was: ")
                print(expr)

                print("\nSymbols were mapping to:\n")
                for sym in expr.free_symbols:
                    print(
                        sym,
                        "->",
                        comando.utility.parse(
                            sym, self.sym_map, maingo_API_op_map, i, const_fun
                        ),
                    )
                raise

        self.parse = parse

    def get_variables(self):
        """Get the MAiNGO equivalent of COMANDO variables."""
        return [MAiNGO_var(v, self.branching_priorities) for v in self.yield_vars()]

    def get_initial_point(self):
        """Get the current initial point."""
        return self._initial_point

    def set_initial_point(self, point):
        """Set the initial point with values corresponding to `yield_vars`."""
        lp = len(point)
        lip = len(self._initial_point)
        if lp == lip:
            self._initial_point = point
        else:
            raise ValueError(
                f"Length of given point is {lp}, however number of variables is {lip}!"
            )

    def evaluate(self, vars):
        """Get an evaluation container representing objective and constraints.

        The evaluation container contains entries for the following
        expressions:

        * obj: objective
        * ineq: inequality constraints
        * eq: equality constraints
        * ineqSquash: squash inequality constraints (vegans only!?)
        * ineqRO: relaxation-only inequality constraints
        * ineqRO: relaxation-only inequality constraints
        * eqRO: relaxation-only equality constraints
        * out: output

        All of these expressions contain FFVar Objects for the variables (NOT
        OptimizationVariable objects!).
        The `out` entry is a list of OutputVariable Objects for display.
        OutputVariables combine an expression in the form of an FFVar object
        with a textual description.
        """
        self._make_sym_map(vars)

        P = self.P
        if self.use_cse is True:
            # Using Common Subexpression Elimination to determine intermediate
            # variables for reoccurring subexpressions within the problem
            reps, exprs = comando.cse(
                (P.design_objective, P.operational_objective, *P.constraints.values())
            )

            defs = {}
            # self = mp; sym, rep = next(iter(reps)); i = 'nominal'
            for sym, rep in reps:
                e = rep.subs(defs)
                index = get_index(e)
                if index is None:
                    x = comando.core.Variable(sym.name)
                    self.sym_map[x] = self.parse(e)
                else:
                    x = comando.core.VariableVector(sym.name)
                    x.instantiate(index)
                    mreps = {}
                    for i, xi in x.expansion.items():
                        mreps[i] = self.sym_map[xi] = self.parse(e, i)
                    self.sym_map[x] = mreps
                defs[sym] = x

            obj = exprs[0].subs(defs) + P.weighted_sum(exprs[1].subs(defs))
            cons = {
                con_id: expr.subs(defs)
                for con_id, expr in zip(P.constraints, exprs[2:])
            }
        else:
            obj, cons = P.objective, P.constraints

        result = maingopy.EvaluationContainer()
        result.obj = self.parse(obj)

        def con_order():
            con_types = ["ineq", "squash", "eq", "ineqRelOnly", "eqRelOnly"]
            for con_group in _split_des_op_cons(self):
                for con_type in con_types:
                    yield from con_group[con_type]

        def handle_con(c_id, con):
            try:  # whether con is ≤ or ≥
                norm_con = con.lts - con.gts
                if c_id in self.relaxation_only:
                    entry = result.ineqRO
                elif c_id in self.squash:
                    entry = result.ineqSquash
                else:
                    entry = result.ineq
            except AttributeError:  # Eq constraint
                norm_con = con.lhs - con.rhs
                if c_id in self.relaxation_only:
                    entry = result.ineqRO
                else:
                    entry = result.eq
            index = get_index(norm_con)
            if index is None:
                entry.push_back(self.parse(norm_con), c_id)
            else:
                for i in index:
                    entry.push_back(self.parse(norm_con, i), f"{c_id}_{i}")

        for c_id in con_order():
            con = cons[c_id]
            handle_con(c_id, con)

        handle_state_equations(P, handle_con)

        # NOTE: Using the append and extend methods on result.output directly
        #       will neither work nor raise any error! That's why we populate
        #       a separate list object here.
        output = []
        for descr, expr in self.output.items():
            index = get_index(expr)
            if index is None:
                output.append(maingopy.OutputVariable(descr, self.parse(expr)))
            else:
                output.extend(
                    [
                        maingopy.OutputVariable(f"{descr}[{i}]", self.parse(expr, i))
                        for i in index
                    ]
                )
        result.output = output

        return result

    def _check_prios(self, branching_priorities):
        vars = {*self.yield_vars(), *self.P.operational_variables}
        for var, val in branching_priorities.items():
            if var not in vars:
                raise ValueError(
                    f'Entry "{var}" is neither a design, nor an '
                    f'operational variable of "{self.P.name}"'
                )
        return branching_priorities


MaingoProblem.solve = solve


class MaingoTwoStageProblem(maingopy.TwoStageModel):
    def __setattr__(self, attr, value):
        if attr not in self._protected:
            super().__setattr__(attr, value)
        else:
            raise AttributeError(
                f"Cannot overwrite attribute '{attr}' of MaingoTwoStageProblem!"
            )

    def _g1_exprs(self):
        """Yield from all g1 constraints."""
        for g1_type in self.g1_expr:
            yield from g1_type

    def _g2_exprs(self):
        """Yield from all g2 constraints."""
        for g2_type in self.g2_expr:
            yield from g2_type

    def __init__(self, P, relaxation_only=None, squash=None, output=None, use_cse=True):
        """Initialize the TwoStageModel."""
        assert P.scenarios, (
            "MaingoTwoStageProblem can only be used with "
            "Problems that have scenarios! For Problems that only have a "
            "time domain use the MaingoProblem class instead."
        )

        if P.states:
            raise NotImplementedError(
                "MaingoTwoStageProblem does not yet support state equations!"
            )

        Nx = len(P.design_variables)
        Ny = len(P.operational_variables)
        w = P.scenario_weights.values
        constants, parameters = split(P.parameters, is_indexed)
        parameters = sorted(parameters, key=namegetter)
        data = P.data.get(map(namegetter, parameters)).values

        super().__init__(Nx, Ny, data, w)
        # store protected attributes to prevent overwriting them
        super().__setattr__("_protected", dir(self))

        self.P = P

        self.x = sorted(P.design_variables, key=namegetter)
        _y = sorted(P.operational_variables, key=namegetter)
        # NOTE: Properly formulated TwoStage problems will never have
        #       references to individual second-stage variables!
        # self.y = [[y_i.elements[s] for y_i in _y] for s in range(self.Ns)]
        self.y = _y
        self.p = parameters
        self.c = constants

        # Variable order: first-stage then for all scenarios second-stage
        def yield_vars():
            yield from self.x
            for st in P.index:
                for y_i in self.y:
                    yield y_i[st]

        self.yield_vars = yield_vars

        self._initial_point = [v.value for v in self.yield_vars()]

        # constants do not change on calls to <f/g><1/2>_func
        self._sym_map = {c: c.value for c in constants}

        self.relaxation_only = set() if relaxation_only is None else relaxation_only
        self.squash = set() if squash is None else squash
        self.output = dict() if output is None else output

        self.f1_expr = P.design_objective
        self._f1_func_cache = {}
        self.f2_expr = P.operational_objective
        self._f2_func_cache = {}

        g1, g2 = _split_des_op_cons(self)

        self.constraints = dict(g1=g1, g2=g2)

        self.g1_expr = [
            [con.lts - con.gts for con in g1["ineq"].values()],
            [con.lts - con.gts for con in g1["squash"].values()],
            [con.lhs - con.rhs for con in g1["eq"].values()],
            [con.lts - con.gts for con in g1["ineqRelOnly"].values()],
            [con.lhs - con.rhs for con in g1["eqRelOnly"].values()],
        ]
        self._g1_func_cache = {}

        self.g2_expr = [
            [con.lts - con.gts for con in g2["ineq"].values()],
            [con.lts - con.gts for con in g2["squash"].values()],
            [con.lhs - con.rhs for con in g2["eq"].values()],
            [con.lts - con.gts for con in g2["ineqRelOnly"].values()],
            [con.lhs - con.rhs for con in g2["eqRelOnly"].values()],
        ]
        self._g2_func_cache = {}

        if use_cse is True:
            # Using Common Subexpression Elimination to determine intermediate
            # variables for reoccurring subexpressions within the problem
            reps, exprs = comando.cse(
                (
                    P.design_objective,
                    P.operational_objective,
                    *self._g1_exprs(),
                    *self._g2_exprs(),
                )
            )

            # mapping backend symbols to COMANDO symbols
            intermediates = {}
            # mapping COMANDO symbols to FFVars representing intermediate expressions
            self._intermediate_expressions = OrderedDict()

            self._base_symbols = set.union(
                P.design_variables, P.operational_variables, P.parameters
            )
            self._deps_level = {}

            for sym, rep in reps:
                var = comando.core.Variable(sym.name)
                intermediates[sym] = var
                i_expr = rep.subs(intermediates)
                self._intermediate_expressions[var] = i_expr

                deps = i_expr.free_symbols - self._base_symbols
                level = max((self._deps_level[var][1] for var in deps), default=-1) + 1
                self._deps_level[var] = deps, level

            self.f1_expr = exprs[0].subs(intermediates)
            self.f2_expr = exprs[1].subs(intermediates)

            con_iter = iter(exprs[2:])
            self.g1_expr = [
                [con.subs(intermediates) for con in islice(con_iter, len(g1["ineq"]))],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g1["squash"]))
                ],
                [con.subs(intermediates) for con in islice(con_iter, len(g1["eq"]))],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g1["ineqRelOnly"]))
                ],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g1["eqRelOnly"]))
                ],
            ]
            self.g2_expr = [
                [con.subs(intermediates) for con in islice(con_iter, len(g2["ineq"]))],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g2["squash"]))
                ],
                [con.subs(intermediates) for con in islice(con_iter, len(g2["eq"]))],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g2["ineqRelOnly"]))
                ],
                [
                    con.subs(intermediates)
                    for con in islice(con_iter, len(g2["eqRelOnly"]))
                ],
            ]

        else:
            self._intermediate_expressions = {}

        def _get_intermediates_for(*exprs):
            if not exprs:
                return OrderedDict()
            deps = (
                set.union(*(expr.free_symbols for expr in exprs)) - self._base_symbols
            )

            expr_deps = defaultdict(set)
            # iterative determination of dependencies
            # obtained from recursive version via tail-call elimination
            while deps:
                deps_deps = set()
                for dep in deps:
                    dep_deps, dep_level = self._deps_level[dep]
                    expr_deps[dep_level].add(dep)
                    deps_deps.update(dep_deps)
                deps = deps_deps.difference(expr_deps)

            # now create a dict with the appropriate order
            maxlevel = max(expr_deps, default=0)
            return OrderedDict(
                (dep, self._intermediate_expressions[dep])
                for i in range(maxlevel + 1)
                for dep in expr_deps[i]
            )

        self.f1_intermediates = _get_intermediates_for(self.f1_expr)
        self.f2_intermediates = _get_intermediates_for(self.f2_expr)
        self.g1_intermediates = _get_intermediates_for(*self._g1_exprs())
        self.g2_intermediates = _get_intermediates_for(*self._g2_exprs())

        super().__setattr__("_protected", dir(self))

    def _update(self, vars):
        """Update the _sym_map with values for intermediate expressions."""
        pass

    def _update_symbols(self, x, ys=None, ps=None, i_exprs=None):
        """Update definitions of symbols and functions."""
        # Update defitions of symbols
        self._sym_map.update(zip(self.x, x))
        if ys:
            self._sym_map.update(zip(self.y, ys))
            self._sym_map.update(zip(self.p, ps))

        # Update definitions of intermediate expressions
        for var, expr in i_exprs.items():
            self._sym_map[var] = self.parse(expr)

    def _check_prios(self, branching_priorities):
        vars = {*self.yield_vars(), *self.P.operational_variables}
        for var, val in branching_priorities.items():
            if var not in vars:
                raise ValueError(
                    f'Entry "{var}" is neither a design, nor an '
                    f'operational variable of "{self.P.name}"'
                )
        return branching_priorities

    def parse(self, expr):
        """Parse from COMANDO to MAiNGO."""
        try:
            return comando.utility.parse(
                expr, self._sym_map, maingo_API_op_map, const_fun=const_fun
            )
        except Exception as e:
            msg = (
                "\nParsing to MAiNGO raised "
                + str(e)
                + "\nexpression was: "
                + str(expr)
                + "\nSymbols were mapping to:\n\t"
                + "\n\t".join(
                    f"{sym} -> "
                    + str(
                        comando.utility.parse(
                            sym, self._sym_map, maingo_API_op_map, const_fun=const_fun
                        )
                    )
                    for sym in expr.free_symbols
                )
            )
            print(msg)
            raise

    def print_sym_map(self):
        """Print the current sym map.

        For a MaingoTwoStageProblem the sym_map is updated on each call to
        f1_func, f2_func, g1_func or g2_func, i.e., it is a mapping
        corresponding to a particular scenario (typically the last one).
        """
        for v, var in self._sym_map.items():
            try:
                print(f"{v} -> {var.name()} ({var})")
            except AttributeError:  # parameters and constants
                print(f"{v} -> {var}")

    def get_variables(self):
        """Get the MAiNGO equivalent of COMANDO variables."""
        return [MAiNGO_var(v, self.branching_priorities) for v in self.yield_vars()]

    def get_initial_point(self):
        """Get the current variable values as the initial point."""
        return [v.value for v in self.yield_vars()]

    def f1_func(self, x):
        """First-stage part of the objective."""
        _x = tuple(id(xi) for xi in x)
        if _x in self._f1_func_cache:
            print("USING CACHED RESULT FOR f1_func(x)!")
            return self._f1_func_cache[_x]
        self._update_symbols(x, i_exprs=self.f1_intermediates)
        self._f1_func_cache[_x] = res = self.parse(self.f1_expr)
        return res

    def f2_func(self, x, ys, ps):
        """Second-stage part of the objective."""
        _args = (
            tuple(id(xi) for xi in x),
            tuple(id(yi) for yi in ys),
            tuple(id(pi) for pi in ps),
        )
        if _args in self._f2_func_cache:
            print("USING CACHED RESULT FOR f2_func(x, ys, ps)!")
            return self._f2_func_cache[_args]
        self._update_symbols(x, ys, ps, i_exprs=self.f2_intermediates)
        self._f2_func_cache[_args] = res = self.parse(self.f2_expr)
        return res

    def g1_func(self, x):
        """First-stage constraints."""
        _x = tuple(id(xi) for xi in x)
        if _x in self._g1_func_cache:
            print("USING CACHED RESULT FOR f1_func(x)!")
            return self._g1_func_cache[_x]
        self._update_symbols(x, i_exprs=self.g1_intermediates)
        self._g1_func_cache[_x] = res = [
            [(self.parse(expr), name) for expr, name in zip(*g1_type)]
            for g1_type in zip(self.g1_expr, self.constraints["g1"].values())
        ]
        return res

    def g2_func(self, x, ys, ps):
        """Second-stage constraints."""
        _args = (
            tuple(id(xi) for xi in x),
            tuple(id(yi) for yi in ys),
            tuple(id(pi) for pi in ps),
        )
        if _args in self._g2_func_cache:
            print("USING CACHED RESULT FOR g2_func(x, ys, ps)!")
            return self._f2_func_cache[_args]
        self._update_symbols(x, ys, ps, i_exprs=self.g2_intermediates)
        self._g2_func_cache[_args] = res = [
            [(self.parse(expr), name) for expr, name in zip(*g2_type)]
            for g2_type in zip(self.g2_expr, self.constraints["g2"].values())
        ]

        return res


MaingoTwoStageProblem.solve = solve
