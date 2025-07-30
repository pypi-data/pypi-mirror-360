"""Routines for interfacing with DyOS."""

import os

import dyospy as dp

import comando.core

# ParameterInput namespace
# paramType_type
# NOTE: Top-level members PROFILE, TIME_INVARIANT, INITIAL, and DURATION are of OutputparamType_type
PROFILE_PARAM = dp.paramType_type.PROFILE
TIME_INVARIANT_PARAM = dp.paramType_type.TIME_INVARIANT
INITIAL_PARAM = dp.paramType_type.INITIAL
DURATION_PARAM = dp.paramType_type.DURATION
# sensType_type namespace
# NOTE: Top-level members FULL, FRACTIONAL, and NO are of OutputsensType_type
FULL_SENS = dp.sensType_type.FULL
FRACTIONAL_SENS = dp.sensType_type.FRACTIONAL
NO_SENS = dp.sensType_type.NO

# AdaptationInput namespace
# adaptType_type
from dyospy import SWITCHING_FUNCTION, WAVELET

# ParamGridInput namespace
# ApproximationType_type
# NOTE: Top-level members PIECEWISE_CONSTANT and PIECEWISE_LINEAR are of OutputApproximationType_type
PIECEWISE_CONSTANT = dp.ApproximationType_type.PIECEWISE_CONSTANT
PIECEWISE_LINEAR = dp.ApproximationType_type.PIECEWISE_LINEAR

# ConstraintInput namespace
# ConstraintType_type
# NOTE: Top-level members POINT, ENDPOINT, and PATH are of OutputConstraintType_type, and
#                         MULTIPLE_SHOOTING is of OutputrunningMode_type
POINT = dp.ConstraintType_type.POINT
ENDPOINT = dp.ConstraintType_type.ENDPOINT
PATH = dp.ConstraintType_type.PATH
MULTIPLE_SHOOTING = dp.ConstraintType_type.MULTIPLE_SHOOTING

# NonLinearSolverInput namespace
# SolverType_type
from dyospy import CMINPACK

# DaeInitializationType_type namespace
# NOTE: The top level members NO and FULL correspond to those of the OutputsensType_type namespace!
#       We therefore disambiguate using the suffix "_INIT"
NO_INIT = dp.DaeInitializationType_type.NO
FULL_INIT = dp.DaeInitializationType_type.FULL
BLOCK_INIT = dp.DaeInitializationType_type.BLOCK
# For BLOCK there are no ambiguities, so we could also do the following
# from dyospy import BLOCK as BLOCK_INIT

# IntegratorInput namespace
# IntegratorType_type
# NOTE: Top-level members NIXE, LIMEX, and IDAS are of OutputIntegratorType_type
NIXE = dp.IntegratorType_type.NIXE
LIMEX = dp.IntegratorType_type.LIMEX
IDAS = dp.IntegratorType_type.IDAS
# order_type
# NOTE: Top-level members ZEROTH, FIRST_FORWARD, FIRST_REVERSE, and SECOND_REVERSE are of Outputorder_type
ZEROTH = dp.order_type.ZEROTH
FIRST_FORWARD = dp.order_type.FIRST_FORWARD
FIRST_REVERSE = dp.order_type.FIRST_REVERSE
SECOND_REVERSE = dp.order_type.SECOND_REVERSE

# AdaptationOptions namespace
# adaptStrategy_type
# NOTE: NOADAPTION is not exposed as a top-level member
NOADAPTION = dp.adaptStrategy_type.NOADAPTATION
from dyospy import ADAPT_STRUCTURE, ADAPTATION, STRUCTURE_DETECTION

# OptimizerInput namespace
# NOTE: Top-level members SNOPT, NPSOL, IPOPT, FILTER_SQP, and SENSITIVITY_INTEGRATION are of OutputOptimizerType_type
SNOPT = dp.OptimizerType_type.SNOPT
NPSOL = dp.OptimizerType_type.NPSOL
IPOPT = dp.OptimizerType_type.IPOPT
FILTER_SQP = dp.OptimizerType_type.FILTER_SQP
SENSITIVITY_INTEGRATION = dp.OptimizerType_type.SENSITIVITY_INTEGRATION

# OptimizerInput namespace
# optimizationMode_type
from dyospy import MINIMIZE

# Input namespace
# runningMode_type
# NOTE: Top-level members SIMULATION, SINGLE_SHOOTING, and MULTIPLE_SHOOTING are of OutputrunningMode_type
SIMULATION = dp.runningMode_type.SIMULATION
SINGLE_SHOOTING = dp.runningMode_type.SINGLE_SHOOTING
MULTIPLE_SHOOTING = dp.runningMode_type.MULTIPLE_SHOOTING


class EsoInput(dp.EsoInput):
    """Struct containing information for the ESO.

    NOTE
    ----
    The current interface only implements ESO with FMI type

    Arguments
    ---------
    relativeFmuTolerance : float
        relative tolerance for the FMU (default 0)

    model : str
        path to the fmu file or directory containing the contents of extracting the fmu
    """

    def __init__(self, relativeFmuTolerance=0, model="."):
        super().__init__()
        self.type = dp.EsoType_type.FMI
        self.relativeFmuTolerance = relativeFmuTolerance
        self.model = model


class ParameterInput(dp.ParameterInput):
    """A single DyOS Parameter.

    Arguments
    ---------
    name : str
        Name of the parameter (must have an exact match in the ESO)

    lowerBound, upperBound : float
        lower and upper bound of the parameter (default -1e+300, +1e+300)

    value : float
        value of the parameter (default 0.0)

    grids : list[dp.ParameterGridInput]
        grids on which the parameter is defined (default [])

    paramType : dp.paramType_type
        type of the parameter, options are:
        - dp.paramType_type.PROFILE (default)
        - dp.paramType_type.TIME_INVARIANT
        - dp.paramType_type.INITIAL
        - dp.paramType_type.DURATION

        For paramType PROFILE the value is ignored (initial values are defined in grids).
        For all other paramType options, grids is ignored and can be left empty.

    sensType : dp.sensType_type
        sensitivity type of the parameter, options are:
        - dp.sensType_type.FULL (default)
        - dp.sensType_type.FRACTIONAL
        - dp.sensType_type.NO

        For sensType is FULL, the parameter (or all control parameters on the grid) is declared as a decision variable, so the full Hessian matrix is calculated for 2nd order integration.
        If lowerbound = upperbound, sensType FULL is changed to sensType FRACTIONAL.
        If sensType is FRACTIONAL, the parameter is no decision variable and only mixed Lagrange derivatives and constraint derivatives are calculated.
        For senstype NO the bounds are ignored.
    """

    def __init__(
        self,
        name,
        lowerBound=-1e300,
        upperBound=1e300,
        value=0.0,
        grids=[],
        paramType=PROFILE_PARAM,
        sensType=FULL_SENS,
    ):
        super().__init__()
        self.name = name
        self.lowerBound = max(lowerBound, -1e300)
        self.upperBound = min(upperBound, +1e300)
        self.value = value
        self.grids = grids
        self.paramType = paramType
        self.sensType = sensType


class WaveletAdaptationInput(dp.WaveletAdaptationInput):
    """Struct for Wavelet Adaptation.

    Arguments
    ---------
    maxRefinementLevel : int
        Maximum level of refinement (default 10)

    minRefinementLevel : int
        Minimum level of refinement (default 3)

    horRefinementDepth : int
        Depth of wavelets considered for refinement in horizontal direction. (default 1)

    verRefinementDepth : int
        Depth of wavelets considered for refinement in vertical direction. (default 1)

    etres : float
        Constant that marks wavelets for elimination (default 1e-8)

    epsilon : float
        Constant that marks wavelets for insertion (default 0.9)
    """

    def __init__(
        self,
        maxRefinementLevel=10,
        minRefinementLevel=3,
        horRefinementDepth=1,
        verRefinementDepth=1,
        etres=1e-8,
        epsilon=0.9,
    ):
        super().__init__()
        self.maxRefinementLevel = maxRefinementLevel
        self.minRefinementLevel = minRefinementLevel
        self.horRefinementDepth = horRefinementDepth
        self.verRefinementDepth = verRefinementDepth
        self.etres = etres
        self.epsilon = epsilon


class SWAdaptationInput(dp.SWAdaptationInput):
    """Struct for Switching Function Adaptation.

    Arguments
    ---------
    maxRefinementLevel : int
        Maximum level of refinement (default 10)

    includeTol : float
        If SW is large than the tolerance, a grid point is included in the control grid. (default 1e-3)
    """

    def __init__(self, maxRefinementLevel=10, includeTol=1e-3):
        super().__init__()
        self.maxRefinementLevel = maxRefinementLevel
        self.includeTol = includeTol


class AdaptationInput(dp.AdaptationInput):
    """Struct for Adaptation Input.

    Arguments
    ---------
    input : WaveletAdaptationInput | SWAdaptationInput
        Object specifying grid adaptation

    maxAdaptSteps : int
        maximum number of adaptation steps (default 1)
    """

    def __init__(self, input, maxAdaptSteps=1):
        super().__init__()
        if isinstance(input, dp.WaveletAdaptationInput):
            self.adaptType = WAVELET
            self.adaptWave = input
        elif isinstance(input, dp.SWAdaptationInput):
            self.adaptType = SWITCHING_FUNCTION
            self.swAdapt = input
        else:
            raise ValueError(
                "input must be either a WaveletAdaptationInput or a SWAdaptationInput!"
            )
        self.maxAdaptSteps = maxAdaptSteps


class ParameterGridInput(dp.ParameterGridInput):
    """A DyOS Parameter Grid.

    Arguments
    ---------
    numIntervals : int
        number of intervals on the profile grid.
        Ignored if timePoints is specified.

    timePoints : list[float]
        explicit time points for the grid.
        The values of timePoints must be in ascending order and within the range [0.0,1.0].
        If left empty, an equidistant grid (with numIntervals intervals) is used

    values : list[float]
        initial values of all parameters of this control.
        May be left empty (then all control parameters are initialized with 0.0).
        For type PIECEWISE_CONSTANT numIntervals values need to be specified.
        For type PIECEWISE_LINEAR numIntervals+1 values need to be specified.

    duration : float
        value of the grid duration (default 0.0).
        Need not be set on the last grid

    hasFreeDuration : bool
        specify whether the grid duration is an optimization variable (default false)

    type : dp.ApproximationType_type
        approximation type, options are:
        - dp.ApproximationType_type.PIECEWISE_CONSTANT (default)
        - dp.ApproximationType_type.PIECEWISE_LINEAR

    adapt : dp.AdaptationInput
        Object specifying grid adaptation

    pcresolution : int
        density of constraint grid points for path constraints (and states for output).
        splits the intervals of the plotgrid (e.g. pcresolution = 3 splits each interval into 3 intervals by adding 2 additional gridpoints on each interval).
    """

    def __init__(
        self,
        numIntervals=0,
        timePoints=None,
        values=None,
        duration=0.0,
        hasFreeDuration=False,
        type=PIECEWISE_CONSTANT,
        adapt=None,
        pcresolution=1,
    ):
        super().__init__()
        if timePoints:
            assert (0.0 <= min(timePoints)) and (max(timePoints) <= 1.0), (
                "Time points must be in the range [0.0,1.0]"
            )
            assert list(timePoints) == sorted(timePoints), (
                "Time points must be in ascending order"
            )
            self.numIntervals = len(timePoints) - 1
            self.timePoints = timePoints
        else:
            self.numIntervals = numIntervals
        if values is not None:
            if isinstance(values, (int, float)):
                numVals = (
                    numIntervals if type == PIECEWISE_CONSTANT else numIntervals + 1
                )
                values = [values] * numVals
            else:
                if type == PIECEWISE_CONSTANT:
                    assert len(values) == numIntervals, (
                        "Number of values must match number of intervals"
                    )
                else:  # type == PIECEWISE_LINEAR
                    assert len(values) == numIntervals + 1, (
                        "Number of values must match number of intervals + 1"
                    )
                import pandas as pd

                if isinstance(values, pd.Series):
                    # Extract raw data
                    values = values.values
            self.values = values
        self.duration = duration
        self.hasFreeDuration = hasFreeDuration
        self.type = type
        if adapt:
            self.adapt = adapt
        self.pcresolution = pcresolution


class IntegratorStageInput(dp.IntegratorStageInput):
    """Struct containing integration-related information for a single stage.

    Arguments
    ---------
    duration : float | ParameterInput
        duration of the stage or ParameterInput with type DURATION and a value ≥ 1e-1.
    parameters : list[ParameterInput]
        vector of ParameterInput containing information of control, initial and time invariant parameters
    plotGridResolution : int
        If the user wants to get output for trajectories on an equidistant grid in addition to the control grid, they can specify the number of grid points with this parameter. (default 1)
    """

    def __init__(self, duration=1, parameters=None, plotGridResolution=1):
        super().__init__()
        if isinstance(duration, (int, float)):
            self.duration = ParameterInput(
                "stageDuration",
                value=duration,
                sensType=NO_SENS,
                paramType=dp.paramType_type.DURATION,
            )
        else:
            self.duration = duration
        if parameters:
            self.parameters = parameters
        self.plotGridResolution = plotGridResolution


class ConstraintInput(dp.ConstraintInput):
    """Struct for point or path constraints.

    Path constraints are later transformed into a vector of point constraints.
    It is possible to define a path constraint and a point constraint for the same state.
    When more than one constraint is defined for the same state at the same time point, they are merged to a single point constraint using the strictest bounds of the constraints.

    Arguments
    ---------
    name : str
        Name of the state to which the constraint applies

    lowerBound, upperBound : float
        lower and upper bound of the constraint (default -1e+300, +1e+300)

    timePoint : float
        point within [0.0, 1.0] at which the constraint is defined (only for type=POINT).

    lagrangeMultiplier : float | list[float]
        Lagrange multipliers of the constraint.
        Single value for type=POINT and ENDPOINT, vector for type=PATH.

    type : dp.ConstraintType_type
        type of the constraint, options are:
        - dp.ConstraintType_type.POINT (default)
        - dp.ConstraintType_type.ENDPOINT
        - dp.ConstraintType_type.PATH
        - dp.ConstraintType_type.MULTIPLE_SHOOTING

    excludeZero : bool
        If set true, the path constraint is not defined at point 0.0 (default false)
    """

    def __init__(
        self,
        name,
        lowerBound=-1e300,
        upperBound=1e300,
        timePoint=0.0,
        lagrangeMultiplier=0.0,
        type=POINT,
        excludeZero=False,
    ):
        super().__init__()
        self.name = name
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        if type == POINT:
            assert 0.0 <= timePoint <= 1.0, "Time point must be in the range [0.0,1.0]"
            self.timePoint = timePoint
            assert isinstance(lagrangeMultiplier, (int, float)), (
                "Lagrange multiplier must be a single value for type POINT"
            )
            self.lagrangeMultiplier = lagrangeMultiplier
        elif type == ENDPOINT:
            assert isinstance(lagrangeMultiplier, (int, float)), (
                "Lagrange multiplier must be a single value for type ENDPOINT"
            )
            self.lagrangeMultiplier = lagrangeMultiplier
        elif type == PATH:
            assert isinstance(lagrangeMultiplier, list), (
                "Lagrange multiplier must be a list of values for type PATH"
            )
            self.lagrangeMultiplierVector = lagrangeMultiplier
        self.type = type
        self.excludeZero = excludeZero


class StructureDetectionInput(dp.StructureDetectionInput):
    """Struct for structure detection options for a given stage.

    Arguments
    ---------
    maxStructureSteps : int
        maximum number of refinement steps (default 0)

    createContinuousGrids : bool
        if set to true, the stages inserted by structure detection will be continuous.
        Otherwise there might be a jump discontinuity at the stage boundaries. (default false)
    """

    def __init__(self, maxStructureSteps=0, createContinuousGrids=False):
        super().__init__()
        self.maxStructureSteps = maxStructureSteps
        self.createContinuousGrids = createContinuousGrids


class OptimizerStageInput(dp.OptimizerStageInput):
    """Struct containing optimization-related information for a single stage.

    In DyOS the objective is handled internally like an endpoint constraint, but only the name and bounds need to be specified.
    In a multistage problem, there might be no objective function available on some stages.
    In this case you need to define a dummy objective (choose any state of the model) and set treatObjective to false.
    Also some optimizers need at least one constraint, so if the problem is unconstrained, define a dummy constraint without bounds on any stage.

    Arguments
    ---------
    objective : dp.ConstraintInput
        objective function of the stage
    constraints : list[dp.ConstraintInput]
        vector of constraints
    structureDetection : dp.StructureDetectionInput
        structure detection options
    """

    def __init__(self, objective, constraints=None, structureDetection=None):
        super().__init__()
        self.objective = objective
        if constraints:
            self.constraints = constraints
        if structureDetection:
            self.structureDetection = structureDetection


class StageInput(dp.StageInput):
    """Struct containing all information of one single stage.

    Arguments
    ---------
    treatObjective : bool
        If set true, the objective value of this stage is added to the total objective value of the multistage problem.
        Otherwise the objective value of the stage will be ignored.
        At least one stage must set treatObjective to true.
        Default is true.
    mapping : dp.StageMapping
        mapping of states from this stage to the following stage
    eso : dp.EsoInput
        ESO input data
    integrator : dp.IntegratorStageInput
        integrator for the stage
    optimizer : dp.OptimizerStageInput
        optimizer for the stage
    """

    def __init__(
        self,
        treatObjective=True,
        mapping=None,
        eso=None,
        integrator=None,
        optimizer=None,
    ):
        super().__init__()
        self.treatObjective = treatObjective
        if mapping:
            self.mapping = mapping
        if eso:
            self.eso = eso
        if integrator:
            self.integrator = integrator
        if optimizer:
            self.optimizer = optimizer


class NonLinearSolverInput(dp.NonLinearSolverInput):
    """Struct containing information for the nonlinear solver that initializes the algebraic variables.

    Arguments
    ---------
    type : dp.SolverType_type
        specify the solver type:
        - dp.SolverType_type.NLEQ1S
        - dp.SolverType_type.CMINPACK (default)

    tolerance : float
        tolerance for the nonlinear solver (default 1e-10)
    """

    def __init__(self, type=None, tolerance=1e-10):
        super().__init__()
        if type is not None:
            self.type = type
        self.tolerance = tolerance


class DaeInitializationInput(dp.DaeInitializationInput):
    """Struct containing information for DAE initialization.

    Usually this input does not need to be specified at all.
    Specify only if tolerances need to be reset or if no solver (Linsol, NLEQ1S) is available.

    Note
    ----
    The linsolver option is not exposed by this class, as the only available option is currently linsol-MA28.

    Arguments
    ---------
    type : dp.DaeInitializationType_type
        specify initialization type:
        - dp.DaeInitializationType_type.NO
        - dp.DaeInitializationType_type.FULL
        - dp.DaeInitializationType_type.BLOCK (default)

        Nixe has a built in DAE initialization, so if either no linear or nonlinear solver is available and if using Nixe, select type NO.
        Type BLOCK uses a block decomposition and solves many small matrix blocks (often 1x1) which will speed up the initialization.
        Type FULL uses the entire Jacobian (as a full matrix) to solve the initialization problem.

    nonLinSolver : dp.NonLinearSolverInput
        struct containing information for the nonlinear solver

    maximumErrorTolerance : float
        After initialization the residuals of all equations are summed up to a total error.
        If the error is greater than the set tolerance, the initialization is considered as failed. (default 1e-10)
    """

    def __init__(self, type=BLOCK_INIT, nonLinSolver=None, maximumErrorTolerance=1e-10):
        super().__init__()
        self.type = type
        if nonLinSolver:
            self.nonLinSolver = nonLinSolver
        self.maximumErrorTolerance = maximumErrorTolerance


class IntegratorInput(dp.IntegratorInput):
    """Struct containing information for the integrator.

    Arguments
    ---------
    type : dp.IntegratorType_type
        specify the integrator:
        - dp.IntegratorType_type.NIXE (default)
        - dp.IntegratorType_type.LIMEX
        - dp.IntegratorType_type.IDAS

        In the open source version the integrators LIMEX and IDAS are not available.
        The integrator NIXE has a built in DAE-initialization, so if the solver LINSOL and NLEQ1s are missing, NIXE is the only integrator that can be used.

    integratorOptions : dict
        specify individual configuration for the chosen integrator.
        Up to now only tolerances may be set (for NIXE and LIMEX),
        e.g: {"absolute tolerance"=..., "relative tolerance"=...}

    order : dp.order_type
        specify integration order:
        - dp.order_type.ZEROTH
        - dp.order_type.FIRST_FORWARD (default)
        - dp.order_type.FIRST_REVERSE
        - dp.order_type.SECOND_REVERSE

        Since all optimizers at least need first order sensitivities, ZEROTH order may only be used with simulation.
        For optimization the default order is switched to FIRST_FORWARD.
        SECOND_REVERSE may only be used with the 2nd order integrator NIXE and a 2nd order optimizer (filter_sqp, IPOPT).

    daeInit : dp.DaeInitializationInput
        struct containing information for DAE initialization
    """

    def __init__(
        self, type=NIXE, integratorOptions=None, order=FIRST_FORWARD, daeInit=None
    ):
        super().__init__()
        self.type = type
        if integratorOptions:
            self.integratorOptions = integratorOptions
        self.order = order
        if daeInit:
            self.daeInit = daeInit


class AdaptationOptions(dp.AdaptationOptions):
    """Struct containing options for grid adaptation.

    Arguments
    ---------
    adaptationThreshold : float
        threshold that checks the change in the objective as a stopping criterion (default 1e-2)

    intermConstraintViolationTolerance : float
        adaptation stops when the intermediate constraint violation is below this tolerance (default 0.1)

    numOfIntermPoints : int
        Number of intermediate points between the points of the path constraints.
        These points are required to determine the intermediate constraint violation (default 4)

    adaptStrategy : dp.adaptStrategy_type
        specify the adaptive strategy (only for optimization)
        - dp.adaptStrategy_type.NOADAPTION (default)
        - dp.adaptStrategy_type.ADAPTATION
        - dp.adaptStrategy_type.STRUCTURE_DETECTION
        - dp.adaptStrategy_type.ADAPT_STRUCTURE

        If ADAPTATION is selected, then after an optimization the discretization grid is refined and another optimization is started.
        These steps are repeated until the improvement of the objective value gets too small.
        In STRUCTURE_DETECTION mode the trajectories are analyzed and a multistage problem is created (e.g. additional stages where profiles are on the bounds).
        ADAPT_STRUCTURE does adaptation and structure detection.
    """

    def __init__(
        self,
        adaptationThreshold=1e-2,
        intermConstraintViolationTolerance=0.1,
        numOfIntermPoints=4,
        adaptStrategy=NOADAPTION,
    ):
        super().__init__()
        self.adaptationThreshold = adaptationThreshold
        self.intermConstraintViolationTolerance = intermConstraintViolationTolerance
        self.numOfIntermPoints = numOfIntermPoints
        self.adaptStrategy = adaptStrategy


class OptimizerInput(dp.OptimizerInput):
    """Struct containing information for the optimizer.

    Arguments
    ---------
    type : dp.OptimizerType_type
        specify the optimizer:
        - dp.OptimizerType_type.SNOPT (default)
        - dp.OptimizerType_type.NPSOL
        - dp.OptimizerType_type.IPOPT
        - dp.OptimizerType_type.FILTER_SQP
        - dp.OptimizerType_type.SENSITIVITY_INTEGRATION

    globalConstraints : list[dp.ConstraintInput]
        vector of ConstraintInput structs.
        Up to now, global constraints are only generated in multiple shooting mode, so this vector should always be left empty

    optimizationMode : dp.optimizationMode_type
        specify whether to minimize or to maximize
        - dp.optimizationMode_type.MINIMIZE (default)
        - dp.optimizationMode_type.MAXIMIZE

    adaptationOptions : dp.AdaptationOptions
        options for grid adaptation

    optimizerOptions : dict
        specify options for the chosen optimizer.
    """

    def __init__(
        self,
        type=SNOPT,
        globalConstraints=None,
        optimizationMode=MINIMIZE,
        adaptationOptions=None,
        optimizerOptions=None,
    ):
        super().__init__()
        self.type = type
        if globalConstraints:
            self.globalConstraints = globalConstraints
        self.optimizationMode = optimizationMode
        if adaptationOptions:
            self.adaptationOptions = adaptationOptions
        if optimizerOptions:
            self.optimizerOptions = optimizerOptions


class Input(dp.Input):
    """Top level input structure containing all data.

    Arguments
    ---------
    stages : dp.stageInput | list[dp.StageInput]
        vector of StageInput structs

    runningMode : dp.runningMode_type
        Specify whether DyOS should optimize (and in which optimization mode) or just simulate (in that case no optimizer input needs to be provided).
        Options are:
        - dp.runningMode_type.SIMULATION
        - dp.runningMode_type.SINGLE_SHOOTING (default)
        - dp.runningMode_type.MULTIPLE_SHOOTING

    integratorInput : dp.IntegratorInput
        integrator input struct

    optimizerInput : dp.OptimizerInput
        optimizer input struct

    totalEndTimeLowerBound, totalEndTimeUpperBound : float
        lower and upper bound of multi stage end time (default -1e+300, +1e+300).
        In multi stage scenarios the duration of the single stages might be set as degrees of freedom.
        However, if the total time of the problem is bounded or fixed, specify the bounds in totalEndTimeLowerBound and totalEndTimeUpperBound.
        Otherwise these fields need not be set at all.
    """

    def __init__(
        self,
        stages,
        runningMode=SINGLE_SHOOTING,
        integratorInput=None,
        optimizerInput=None,
        totalEndTimeLowerBound=-1e300,
        totalEndTimeUpperBound=1e300,
    ):
        super().__init__()
        if isinstance(stages, dp.StageInput):
            stages = [stages]
        self.stages = stages
        self.runningMode = runningMode
        if integratorInput:
            self.integratorInput = integratorInput
        if optimizerInput:
            self.optimizerInput = optimizerInput
        self.totalEndTimeLowerBound = totalEndTimeLowerBound
        self.totalEndTimeUpperBound = totalEndTimeUpperBound


MOD_NOT_FOUND = """Could not import MOD. Ensure that you installed it and that

MODPATH
              
is in your PYTHONPATH."""


def generateFMU(mo_path, **options):
    from importlib.util import find_spec

    generator = None
    if find_spec("dymola"):
        generator = "DYMOLA"
    else:
        msg = MOD_NOT_FOUND.replace(
            "MODPATH",
            "<DYMOLA_INSTALL_PATH>\Modelica\Library\python_interface\dymola.egg",
        )
        msg = msg.replace("MOD", "dymola")
        print(msg)
        print("I will now attempt to fall back to OMPython...")
        if find_spec("OMPython"):
            generator = "OMPYTHON"
        else:
            msg = MOD_NOT_FOUND.replace("MODPATH", "<openmodelica_path>/bin/omc")
            msg = msg.replace("MOD", "OMPython")
            raise ModuleNotFoundError(msg)

    wd = os.path.dirname(mo_path)
    mo_model_name = options.pop(
        "modelToOpen", os.path.splitext(os.path.basename(mo_path))[0]
    )
    fmu_name = options.pop("modelName", mo_model_name)

    if generator == "DYMOLA":
        from dymola.dymola_exception import DymolaException
        from dymola.dymola_interface import DymolaInterface

        try:
            # Instantiate the Dymola interface and start Dymola
            # Gather DymolaInterface options

            # Older dymola versions:
            # use64bit = options.pop("use64bit", True)

            # Gather translateModelFMU options

            storeResult = options.pop("storeResut", False)
            fmiVersion = str(options.pop("fmiVersion", "2"))
            fmiType = options.pop("fmiType", "me")
            includeSource = options.pop("includeSource", True)

            dymola = DymolaInterface(
                dymolapath=options.pop("dymolapath", ""),
                port=options.pop("port", -1),
                showwindow=options.pop("showwindow", False),
                debug=options.pop("debug", False),
                allowremote=options.pop("allowremote", False),
                nolibraryscripts=options.pop("nolibraryscripts", False),
                startDymola=True,
                dsls=False,
                closeDymola=True,
            )

            if options:
                raise TypeError(f"invalid options {[*options]}!")

            # Call a function in Dymola and check its return value
            dymola.openModel(mo_path)
            # dymola.AddModelicaPath(pwd)
            dymola.ExecuteCommand("Advanced.GenerateAnalyticJacobian = true;")
            fmu_name = dymola.translateModelFMU(
                mo_model_name, storeResult, fmu_name, fmiVersion, fmiType, includeSource
            )

            messages, n_error, n_warn, n_info = dymola.getLastError()
            print(messages)
            if not fmu_name:
                return ""
            fmu_file = fmu_name + ".fmu"
        except DymolaException as ex:
            print("Error: " + str(ex))
            generator = None

        if generator is not None:
            dymola.close()

        fmu_dir_path = os.path.join(wd, fmu_name)
        if os.path.exists(fmu_dir_path):
            import shutil

            shutil.rmtree(fmu_dir_path)
        os.rename(os.path.join(wd, "~FMUOutput"), fmu_dir_path)

    else:  # Fallback to open modelica
        from OMPython import OMCSessionZMQ

        omc = OMCSessionZMQ()

        # TODO: Is this necessary?
        if omc.loadFile(mo_path).startswith("false"):
            raise Exception(
                "Modelica compilation failed: {}".format(
                    omc.sendExpression("getErrorString()")
                )
            )

        # omc.sendExpression('setDebugFlags("-disableDirectionalDerivatives")')
        omc.sendExpression('setCommandLineOptions("-d=initialization")')
        # omc.sendExpression(f'translateModelFMU({mo_model_name})')  # DEPRECATED
        fmu_file = omc.sendExpression(f"buildModelFMU({mo_model_name})")
        flag = omc.sendExpression("getErrorString()")
        if flag:
            print("warnings:\n{}".format(flag))
        if not fmu_file.endswith(".fmu"):
            raise Exception("FMU generation failed: {}".format(flag))

        # DyOS requires the FMU (which is just a renamed zip file) to be extracted
        import zipfile

        fmu_path = os.path.join(wd, fmu_file)
        fmu_dir_path = os.path.join(wd, fmu_name)
        with zipfile.ZipFile(fmu_path, "r") as zip_ref:
            zip_ref.extractall(fmu_dir_path)

    return fmu_dir_path


def dump(obj, indent=0, nest=True):
    """Serialize an object to JSON format.

    Arguments
    ---------
    obj : obj
        The object to be serialized
    indent : int
        The current level of indentation
    nest : bool
        Wheather nested
    """
    lev = "  " * indent
    if isinstance(obj, bool):
        return lev * nest + repr(obj).lower()
    if isinstance(obj, (int, float)):
        return lev * nest + repr(obj)
    if isinstance(obj, str):
        return lev * nest + repr(obj).replace("'", '"')
    if isinstance(obj, list):
        return (
            lev * nest
            + (
                "[\n"
                + ",\n".join(dump(elem, indent + 1) for elem in obj)
                + "\n"
                + lev
                + "]"
            )
            if obj
            else "[]"
        )
    if isinstance(obj, dict):
        return (
            lev * nest
            + (
                "{\n"
                + ",\n".join(dump._kv(k, v, indent + 1) for (k, v) in obj.items())
                + "\n"
                + lev
                + "}"
            )
            if obj
            else "{}"
        )
    members = [m for m in dir(obj) if not m.startswith("_")]
    if members:
        member_dict = {
            m: str(getattr(obj, m)) if m in dump.enums else getattr(obj, m)
            for m in members
            if m not in dump.ignore
        }
        return dump(member_dict, indent, nest)

    return lev + str(obj)


def __kv(k, v, indent):
    return "  " * indent + repr(k).replace("'", '"') + ": " + dump(v, indent, False)


dump._kv = __kv

# Exclude (attributes that contain duplicate information or are not informative)
dump.ignore = {
    "ADAPTATION",
    "ADAPT_STRUCTURE",
    "DURATION",
    "FIRST_FORWARD",
    "FIRST_REVERSE",
    "FRACTIONAL",
    "FULL",
    "IDAS",
    "INITIAL",
    "KLU",
    "LIMEX",
    "MA28",
    "MAXIMIZE",
    "MINIMIZE",
    "MULTIPLE_SHOOTING",
    "NIXE",
    "NO",
    "NOADAPTATION",
    "PROFILE",
    "SECOND_REVERSE",
    "SENSITIVITY_INTEGRATION",
    "SIMULATION",
    "SINGLE_SHOOTING",
    "STRUCTURE_DETECTION",
    "SolverType",
    "TIME_INVARIANT",
    "ZEROTH",
}

# ENUMS (contain references to their type and thus need to be handled separately to avoid infinite recursion)
dump.enums = {
    "adaptType",
    "adaptStrategy",
    "optimizationMode",
    "order",
    "paramType",
    "runningMode",
    "sensType",
    "type",
    "adaptStrategy",
}


# TODO: Make option casing consistent
DEFAULT_OPTIONS = dict(
    # ESO
    fmu_tol=1e-12,
    # IntegratorStageInput
    plotGridResolution=1,
    # StructureDetection
    maxStructureSteps=0,
    createContinuousGrids=False,
    # NonLinearSolverInput
    nl_solver=CMINPACK,
    nl_solver_tol=1e-10,
    # DaeInitializationInput
    init_type=NO_INIT,
    init_tol=1e-10,
    # IntegratorInput
    integrator=NIXE,
    integrator_options=None,
    integrator_order=FIRST_FORWARD,
    # AdaptationOptions
    adapt_threshold=1e-2,
    adapt_tol=0.1,
    adapt_points=4,
    adapt_strategy=NOADAPTION,
    adapt_type=WAVELET,
    maxAdaptSteps=1,
    pcresolution=1,
    maxRefinementLevel=10,
    # Wavelet Adaptation
    minRefinementLevel=3,
    horRefinementDepth=1,
    verRefinementDepth=1,
    etres=1e-8,
    epsilon=0.9,
    # Switching-Function Adaptation
    includeTol=0.001,
    # OptimizerInput
    optimizer=SNOPT,
    optimizer_mode=MINIMIZE,
    optimizer_options=None,
    # Input
    runningMode=SINGLE_SHOOTING,
    totalEndTimeLowerBound=-1e300,
    totalEndTimeUpperBound=1e300,
    nameOutputFile="output.json",
)


class DyosProblem(dp.DyosPy):
    """Initialize a DyOS Problem from a COMANDO Problem.

    Arguments
    ---------
    P : comando.Problem
        A COMANDO problem that is to be translated to MAiNGO data structures.
    controls : List[comando.VariableVector]
        List of operational variables that are to be treated as controls.
        Note that all design variables are automatically treated as controls.
    fmu_path : str | None
        If given, must be the path to an fmu file or the directory containing
        the extracted contents.
        If not, writes a modelica file and attempts to generates an FMU.
    point_constraints : Dict[str->Dict(str->float)]
        Dictionary mapping variable names to a dictionary, specifying bounds.
        The inner dictionary may contain a numeric entry for each of the
        following:
        - "lowerBound"
        - "upperBound"
        - "lagrangeMultiplier"
        - "timePoint"
        If the latter is not given, the end time is used.
    kwargs : Dict[str->(str | float)]
        Dictionary specifying further DyOS options.
    """

    def __init__(self, P, controls, fmu_path=None, point_constraints=None, **kwargs):
        super().__init__()

        self.P = P
        self.controls = controls

        options = DEFAULT_OPTIONS.copy()
        options.update(kwargs)

        fmu_tol = options.pop("fmu_tol")
        plotGridResolution = options.pop("plotGridResolution")
        maxStructureSteps = options.pop("maxStructureSteps")
        createContinuousGrids = options.pop("createContinuousGrids")
        nl_solver = options.pop("nl_solver")
        nl_solver_tol = options.pop("nl_solver_tol")
        init_type = options.pop("init_type")
        init_tol = options.pop("init_tol")
        integrator = options.pop("integrator")
        integrator_options = options.pop("integrator_options")
        integrator_order = options.pop("integrator_order")
        adapt_threshold = options.pop("adapt_threshold")
        adapt_tol = options.pop("adapt_tol")
        adapt_points = options.pop("adapt_points")
        adapt_strategy = options.pop("adapt_strategy")
        adapt_type = options.pop("adapt_type")
        maxAdaptSteps = options.pop("maxAdaptSteps")
        pcresolution = options.pop("pcresolution")
        maxRefinementLevel = options.pop("maxRefinementLevel")
        minRefinementLevel = options.pop("minRefinementLevel")
        horRefinementDepth = options.pop("horRefinementDepth")
        verRefinementDepth = options.pop("verRefinementDepth")
        etres = options.pop("etres")
        epsilon = options.pop("epsilon")
        includeTol = options.pop("includeTol")
        optimizer = options.pop("optimizer")
        optimizer_mode = options.pop("optimizer_mode")
        optimizer_options = options.pop("optimizer_options")
        runningMode = options.pop("runningMode")
        totalEndTimeLowerBound = options.pop("totalEndTimeLowerBound")
        totalEndTimeUpperBound = options.pop("totalEndTimeUpperBound")
        nameOutputFile = options.pop("nameOutputFile")

        if options:
            import warnings

            warnings.warn(f"Unused options: {[*options]}")

        if fmu_path is None:
            # Create a modelica file and Attempt to generate an fmu
            # in a temporary directory then return where we've been.
            import tempfile

            tmp_dir_obj = tempfile.TemporaryDirectory()
            tmp_dir = tmp_dir_obj.name
            old_pwd = os.getcwd()  # we start in old_pwd
            os.chdir(tmp_dir)  # then we go to tmpdir
            print("RUNNING IN:", os.getcwd())
            label = P.name if P.name else "MyModel"
            mo_file = label + ".mo"
            mo_path = os.path.join(tmp_dir, mo_file)
            try:
                from comando.interfaces.modelica import write_mo_file

                write_mo_file(P, mo_path, controls)
                fmu_path = generateFMU(mo_path, includeSource=False)
                assert fmu_path == os.path.join(tmp_dir, label)
                # Unfortunately, DyOS appears to require an fmu in the same
                # directory as it is called, so we need to copy if we want
                # to return to the original directory.
                import shutil

                shutil.copytree(
                    fmu_path, os.path.join(old_pwd, label), dirs_exist_ok=True
                )
                shutil.copyfile(mo_path, os.path.join(old_pwd, mo_file))

                fmu_path = os.path.join(old_pwd, label)
            finally:
                os.chdir(old_pwd)  # and return to old_pwd
        elif (
            os.path.exists(fmu_path)
            and not os.path.isdir(fmu_path)
            and fmu_path.endswith(".fmu")
        ):
            import zipfile

            fmu_dir_path = (fmu_path + ".fmu")[:-4]
            with zipfile.ZipFile(fmu_path, "r") as zip_ref:
                zip_ref.extractall(fmu_dir_path)

        # ESO
        esoInput = EsoInput(fmu_tol, fmu_path)

        # PARAMETERS
        if P.scenarios:
            ts = (P.timesteps.groupby(level="s").cumsum() / P.T).groupby(level="s")
            time_points = {s: [0, *(d.values)] for s, d in ts}
            n_t = {
                s: len(time_points_s) - 1 for s, time_points_s in time_points.items()
            }
        else:
            time_points = [0, *(P.timesteps.cumsum().values / P.T)]
            n_t = len(time_points) - 1

        # Grid adaptation, for now the same for all parameters

        # If adapt_strategy is not explicitly set, try to determine the strategy from the passed options
        if "adapt_strategy" not in kwargs:
            adaptation = False
            structure = False
            if "maxStructureSteps" in kwargs:
                structure = True
            wavelet_options = [
                "minRefinementLevel",
                "horRefinementDepth",
                "verRefinementDepth",
                "etres",
                "epsilon",
            ]
            if "includeTol" in kwargs:
                if not any(
                    wavelet_option in kwargs for wavelet_option in wavelet_options
                ):
                    if "adapt_type" not in kwargs:
                        adapt_type = SWITCHING_FUNCTION
                adaptation = True
            else:
                if any(wavelet_option in kwargs for wavelet_option in wavelet_options):
                    if "adapt_type" not in kwargs:
                        adapt_type = WAVELET
                    adaptation = True
            if adaptation:
                if structure:
                    adapt_strategy = ADAPT_STRUCTURE
                else:
                    adapt_strategy = ADAPTATION
            elif structure:
                adapt_strategy = STRUCTURE_DETECTION
            else:
                adapt_strategy = NOADAPTION

            # Otherwise use the default (WAVELET)

        if adapt_strategy != NOADAPTION:
            if adapt_type is WAVELET:
                adapt = AdaptationInput(
                    WaveletAdaptationInput(
                        maxRefinementLevel,
                        minRefinementLevel,
                        horRefinementDepth,
                        verRefinementDepth,
                        etres,
                        epsilon,
                    ),
                    maxAdaptSteps,
                )
            else:  # adapt_type is SWITCHING_FUNCTION
                adapt = AdaptationInput(
                    SWAdaptationInput(maxRefinementLevel, includeTol), maxAdaptSteps
                )
        else:
            adapt = None

        parameters = []
        for p in P.parameters:
            if p.is_indexed:
                if P.scenarios:
                    for s in P.scenarios:
                        grid = ParameterGridInput(
                            n_t[s],
                            time_points[s],
                            p.value[s],
                            adapt=adapt,
                            pcresolution=pcresolution,
                        )
                        parameters.append(
                            ParameterInput(
                                p.name + f"_{s}",
                                grids=[grid],
                                paramType=PROFILE_PARAM,
                                sensType=NO_SENS,
                            )
                        )
                else:
                    grid = ParameterGridInput(
                        n_t,
                        time_points,
                        p.value,
                        adapt=adapt,
                        pcresolution=pcresolution,
                    )
                    parameters.append(
                        ParameterInput(
                            p.name,
                            grids=[grid],
                            paramType=PROFILE_PARAM,
                            sensType=NO_SENS,
                        )
                    )
            else:
                parameters.append(
                    ParameterInput(
                        p.name,
                        value=p.value,
                        paramType=TIME_INVARIANT_PARAM,
                        sensType=NO_SENS,
                    )
                )

        for dv in P.design_variables:
            parameters.append(
                ParameterInput(
                    dv.name,
                    *dv.bounds,
                    value=dv.value,
                    paramType=TIME_INVARIANT_PARAM,
                    sensType=FULL_SENS,
                )
            )

        for c in controls:
            if P.scenarios:
                lbds, ubds = c.bounds  # TODO
                for s in P.scenarios:
                    grid = ParameterGridInput(
                        n_t[s],
                        time_points[s],
                        c.value[s],
                        adapt=adapt,
                        pcresolution=pcresolution,
                    )
                    parameters.append(
                        ParameterInput(
                            c.name + f"_{s}",
                            min(lbds[s]),
                            max(ubds[s]),
                            grids=[grid],
                            paramType=PROFILE_PARAM,
                            sensType=FULL_SENS,
                        )
                    )
            else:
                grid = ParameterGridInput(
                    n_t, time_points, c.value, adapt=adapt, pcresolution=pcresolution
                )
                lbds, ubds = c.bounds  # TODO
                parameters.append(
                    ParameterInput(
                        c.name,
                        min(lbds),
                        max(ubds),
                        grids=[grid],
                        paramType=PROFILE_PARAM,
                        sensType=FULL_SENS,
                    )
                )

        # STAGE-RELATED INTEGRATOR OPTIONS
        if not P._uniform_timesteps:
            raise NotImplementedError(
                "Currently the duration for all scenarios must be equal!"
            )
        integratorStageInput = IntegratorStageInput(
            next(iter(P.T)) if P.scenarios else P.T, parameters, plotGridResolution
        )

        # OBJECTIVE AND CONSTRAINTS
        obj = ConstraintInput("obj")

        n_ineqs = 0
        for c in P.constraints.values():
            if not c.is_Equality:
                n_ineqs += 1
        lamb = []  # [0] * n_t
        inf = float("inf")
        if P.scenarios:
            state_bound_constraints = []
            for state in P.states:
                if state._bounds != (-inf, inf):
                    lbds, ubds = state.bounds
                    for s in P.scenarios:
                        lb = lbds[s].min()
                        ub = ubds[s].max()
                        state_bound_constraints.append(
                            ConstraintInput(
                                state.name + f"_{s}",
                                lowerBound=-1e300 if lb == -inf else lb,
                                upperBound=1e300 if ub == inf else ub,
                                type=PATH,
                                lagrangeMultiplier=lamb,
                            )
                        )
            path_cons = [
                ConstraintInput(
                    f"inequality_{i}_{s}",
                    upperBound=0,
                    type=PATH,
                    lagrangeMultiplier=lamb,
                )
                for i in range(n_ineqs)
                for s in P.scenarios
            ]
        else:
            state_bound_constraints = [
                ConstraintInput(
                    s.name,
                    lowerBound=-1e300 if s._bounds[0] == -inf else s._bounds[0],
                    upperBound=1e300 if s._bounds[1] == inf else s._bounds[1],
                    type=PATH,
                    lagrangeMultiplier=lamb,
                )
                for s in P.states
                if s._bounds != (-inf, inf)
            ]
            path_cons = [
                ConstraintInput(
                    f"inequality_{i}", upperBound=0, type=PATH, lagrangeMultiplier=lamb
                )
                for i in range(n_ineqs)
            ]

        # NOTE: Specifying scenario-specific constraints is the user's responsibility
        point_cons = []
        if not point_constraints:
            point_constraints = {}
        for name, vals in point_constraints.items():
            # TODO: Check that name refers to a control(?), state or an algebraic variable declared as output
            timePoint = vals.pop("timePoint", None)
            point_cons.append(
                ConstraintInput(
                    name,
                    lowerBound=vals.pop("lowerBound", -1e300),
                    upperBound=vals.pop("upperBound", 1e300),
                    timePoint=0 if timePoint is None else timePoint,
                    lagrangeMultiplier=vals.pop("lagrangeMultiplier", 0),
                    type=ENDPOINT if timePoint is None else POINT,
                )
            )

        constraints = [*state_bound_constraints, *path_cons, *point_cons]

        # STRUCTURE DETECTION
        structureDetectionInput = StructureDetectionInput(
            maxStructureSteps, createContinuousGrids
        )

        # STAGE-RELATED OPTIMIZER OPTIONS
        optimizerStageInput = OptimizerStageInput(
            obj, constraints, structureDetectionInput
        )

        # STAGE
        stageInput = StageInput(
            eso=esoInput, integrator=integratorStageInput, optimizer=optimizerStageInput
        )

        nonLinearSolverInput = NonLinearSolverInput(
            type=nl_solver, tolerance=nl_solver_tol
        )
        daeInitializationInput = DaeInitializationInput(
            type=init_type,
            nonLinSolver=nonLinearSolverInput,
            maximumErrorTolerance=init_tol,
        )
        integratorInput = IntegratorInput(
            type=integrator,
            integratorOptions=integrator_options,
            order=integrator_order,
            daeInit=daeInitializationInput,
        )

        global_cons = None  # TODO

        adaptationOptions = AdaptationOptions(
            adaptationThreshold=adapt_threshold,
            intermConstraintViolationTolerance=adapt_tol,
            numOfIntermPoints=adapt_points,
            adaptStrategy=adapt_strategy,
        )
        optimizerInput = OptimizerInput(
            type=optimizer,
            globalConstraints=global_cons,
            optimizationMode=optimizer_mode,
            adaptationOptions=adaptationOptions,
            optimizerOptions=optimizer_options,
        )

        # INPUT
        self.Input = Input(
            stageInput,
            runningMode=runningMode,
            integratorInput=integratorInput,
            optimizerInput=optimizerInput,
            totalEndTimeLowerBound=totalEndTimeLowerBound,
            totalEndTimeUpperBound=totalEndTimeUpperBound,
        )

        self.nameOutputFile = nameOutputFile

    def dump_input(self, file_name):
        """ "Dump the input struct to JSON."""
        with open(file_name, "w") as f:
            try:
                print(dump(self.Input), file=f)
            except Exception as e:
                print(e)

    def solve(self):
        # solving problem
        self.runDyosPy()

        # NOTE: We only consider single stage problems here
        stage = self.Output.stages[0]

        # Collect data on the union of all time grids
        import numpy as np
        import pandas as pd

        t = comando.core.Symbol("t")
        total_time_grid = set()
        self.time_grids = {}
        self.result_functions = {}
        dvs = {v.name: v.value for v in self.P.design_variables}

        def _consistent_lambdify(t, f):
            if comando.BACKEND.__name__ == "sympy":
                return comando.lambdify(t, f)
            else:
                _f = comando.lambdify(t, (f,))

                def lambdified(arg):
                    val = _f(arg)
                    if isinstance(arg, (int, float)):
                        return float(val)
                    else:
                        return val

                return lambdified

        for parameter in stage.integrator.parameters:
            if parameter.name in dvs:  # Design variables only have one value
                dvs[parameter.name] = parameter.grids[0].values[0]
                continue

            definitions = []
            time = 0
            tp = set()
            for grid in parameter.grids:
                times = time + np.array(grid.timePoints) * grid.duration
                values = grid.values
                tp.update(times)
                if grid.type == grid.type.PIECEWISE_CONSTANT:
                    definitions.extend(
                        ((vi, t <= te) for te, vi in zip(times[1:], values))
                    )
                else:  # grid.type == grid.type.PIECEWISE_LINEAR:
                    definitions.extend(
                        (
                            (vs + (ve - vs) * (t - ts) / (te - ts), t < te)
                            for ts, te, vs, ve in zip(
                                times[:-1], times[1:], values[:-1], values[1:]
                            )
                        )
                    )
                time += grid.duration
            total_time_grid.update(tp)
            times = sorted(tp)
            self.time_grids[parameter.name] = times

            definitions[-1] = definitions[-1][0], t <= times[-1]

            # Define function
            f = comando.Piecewise(
                (float("nan"), t < times[0]),
                *definitions,
                (values[-1], t > times[-1]),
                (float("nan"), True),
            )
            self.result_functions[parameter.name] = _consistent_lambdify(t, f)

        for state in stage.integrator.states:
            times = state.grid.timePoints
            values = state.grid.values

            total_time_grid.update(times)
            self.time_grids[state.name] = times

            # NOTE: While states should be computed from the integral over
            #       their associated differential equation, this is difficult
            #       to achieve here. We therefore use a piecewise-linear
            #       approximation based on the values returned by dyos.
            definitions = [
                (vs + (ve - vs) * (t - ts) / (te - ts), t < te)
                for ts, te, vs, ve in zip(
                    times[:-1], times[1:], values[:-1], values[1:]
                )
            ]
            definitions[-1] = definitions[-1][0], t <= times[-1]

            # Define function
            f = comando.Piecewise(
                (float("nan"), t < times[0]),
                *definitions,
                (values[-1], t == times[-1]),
                (float("nan"), True),
            )
            self.result_functions[state.name] = _consistent_lambdify(t, f)

        # Store results
        total_time_grid = np.array(sorted(total_time_grid))
        self.results = pd.DataFrame(
            {n: func(total_time_grid) for n, func in self.result_functions.items()},
            total_time_grid,
        )

        # Update design values
        self.P.design = dvs
        # Update Problem time discretization, parameter and operational variable values
        self.P.timesteps = total_time_grid[1:], total_time_grid[-1]
        opars = [p.name for p in self.P.parameters if p.is_indexed]
        if self.P.scenarios:
            for parname in opars:
                self.P.data[parname] = pd.concat(
                    {
                        s: self.results[f"{parname}_{s}"].iloc[1:]
                        for s in self.P.scenarios
                    },
                    names=["s", "t"],
                )
            for ov in self.P.operational_variables:
                self.P[ov.name] = pd.concat(
                    {
                        s: self.results[f"{ov.name}_{s}"].iloc[1:]
                        for s in self.P.scenarios
                    },
                    names=["s", "t"],
                )
        else:
            opar_values = self.results[opars]
            for parname in opars:
                self.P.data[parname] = opar_values[parname].iloc[1:]
            for ov in self.P.operational_variables:
                self.P[ov.name] = self.results[ov.name].iloc[1:]

        return self.Output

    def plot(self, *subplots, **plot_args):
        """Plot results for given variables.

        Arguments
        ---------
        subplots : Tuple[List[str]]
            names of variables to be included in subplots. The number of lists
            specifies the total number of subplots.
        plot_args : dict
            additional plotting options, passed to plt.subplots
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd

        plotting_time = np.linspace(
            0, next(iter(self.P.T)), self.Input.stages[0].integrator.plotGridResolution
        )
        if not subplots:
            subplots = (
                [control.name for control in self.controls],
                [state.name for state in self.P.states],
            )
            if self.P.scenarios:
                subplots = tuple(
                    subplot
                    for s in self.P.scenarios
                    for subplot in (
                        [f"{control.name}_{s}" for control in self.controls],
                        [f"{state.name}_{s}" for state in self.P.states],
                    )
                )
        elems = [e for subplot in subplots for e in subplot]
        plot_data = pd.DataFrame(
            {k: self.result_functions[k](plotting_time) for k in elems}, plotting_time
        )
        N = len(subplots)
        fig, axs = plt.subplots(N, **plot_args)
        if N == 1:
            axs = [axs]
        for ax, subplot in zip(axs, subplots):
            plot_data[subplot].plot(ax=ax)
        plt.show()
