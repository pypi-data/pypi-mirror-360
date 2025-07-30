import os

import pytest

from comando.core import Parameter, Variable, VariableVector
from tests import missing_module


def check_syntax(mo_file_path, model_name):
    from dymola.dymola_exception import DymolaException
    from dymola.dymola_interface import DymolaInterface

    try:
        dymola = DymolaInterface()
        ret = dymola.openModel(mo_file_path) and dymola.checkModel(model_name)
    except DymolaException as ex:
        print("Error: " + str(ex))
        ret = False
    finally:
        dymola.close()
    return ret


def simulate(mo_file_path, model_name):
    from dymola.dymola_exception import DymolaException
    from dymola.dymola_interface import DymolaInterface

    try:
        dymola = DymolaInterface()
        ret = dymola.openModel(mo_file_path) and dymola.simulateModel(model_name)
    except DymolaException as ex:
        print("Error: " + str(ex))
        ret = False
    finally:
        dymola.close()
    return ret


@pytest.mark.skipif(
    missing_module("dymola"),
    reason='Dymola python package is not available. If you have Dymola installed ensure that the PYTHONPATH environment variable contains "<Dymola installation directory>\\Modelica\\Library\\python_interface\\dymola.egg"!',
)
def test_syntax(run_in_tmpdir):
    from comando import (
        BINARY,
        INTEGER,
        REAL,
        Eq,
        Problem,
    )

    bdv = Variable("bdv", BINARY, init_val=1)
    idv = Variable("idv", INTEGER, bounds=(-1, 1), init_val=1)
    rdv = Variable("rdv", REAL, bounds=(-1, 1), init_val=1)

    bov = VariableVector("bov", BINARY, init_val=1)
    iov = VariableVector("iov", INTEGER, bounds=(-1, 1), init_val=1)
    rov = VariableVector("rov", REAL, bounds=(-1, 1), init_val=1)

    sp = Parameter("sp", 1)
    vp = Parameter("vp")

    # Design expressions are any expression containing only design variables and parameters
    de = bdv + idv + rdv + sp
    # Any expression containing at least one operational variable or parameter is an operational expression
    oe1 = de + bov
    oe2 = de + iov
    oe3 = de + rov
    oe4 = de + vp

    constraints = dict(
        dc=(de >= 1),
        oc1=(oe2 <= 1),
        oc2=(oe3 >= -1),
        # oc3=Eq(oe4, 1),
        oc4=Eq(bov, iov),
        oc5=Eq(bov, rov),
        oc6=Eq(bov, sp),
    )

    timesteps = (range(3), 3)
    P = Problem(de, oe1, constraints, timesteps=timesteps, name="TestProblem")

    from comando.interfaces.modelica import write_mo_file

    mo_file_name = P.name + ".mo"

    with run_in_tmpdir:
        tmpdir = os.getcwd()
        mo_file = os.path.join(tmpdir, mo_file_name)

        write_mo_file(P, mo_file, [])
        assert check_syntax(mo_file, P.name)

        # Adding a constraint containing the time-variable parameter vp
        P.constraints["oc3"] = oe4 <= 1
        write_mo_file(P, mo_file, [])
        # Value of vp was not set, results in nan value
        assert check_syntax(mo_file, P.name) == False

        # Manually registering vp and setting its value fixes this
        P.parameters.add(vp)
        P["vp"] = (3, 2, 0.5)
        # NOTE: By default, time-variable data is not included
        #       in the modelica file, instead, only the first
        #       time value is used.
        write_mo_file(P, mo_file, [])
        assert check_syntax(mo_file, P.name)
        # If data is to be included, this needs to be specified explicitly
        write_mo_file(P, mo_file, [], use_time_variable_data=True)
        assert check_syntax(mo_file, P.name)

        # Changing inequality to equality results in an over constrained system
        P.constraints["oc3"] = Eq(oe4, 1)
        with pytest.raises(RuntimeError) as e:
            write_mo_file(P, mo_file, [], precheck=True)
            assert "overconstrained" in str(e)

        # Removing one constraint results in an underconstrained system
        del P.constraints["oc3"]
        del P.constraints["oc6"]
        with pytest.raises(RuntimeError) as e:
            write_mo_file(P, mo_file, [], precheck=True)
            assert "underconstrained" in str(e)

        # Structural singularity can be detected
        P.constraints["oc6"] = P.constraints["oc5"]
        with pytest.raises(RuntimeError) as e:
            write_mo_file(P, mo_file, [], precheck=True)
            assert "singular" in str(e)

        # Problem with both scenarios and timesteps
        P = Problem(
            de,
            oe1 * vp,
            constraints,
            scenarios=["s1", "s2"],
            timesteps=timesteps,
            name="TestProblem",
        )

        # Operational parameter is only time dependent
        P["vp"] = (3, 2, 0.5)
        write_mo_file(P, mo_file, [])
        assert check_syntax(mo_file, P.name)
        write_mo_file(P, mo_file, [], use_time_variable_data=True)
        assert check_syntax(mo_file, P.name)

        # Operational parameter is only scenario dependent
        P["vp"] = (2, 0.5)
        write_mo_file(P, mo_file, [])
        assert check_syntax(mo_file, P.name)
        write_mo_file(P, mo_file, [], use_time_variable_data=True)
        assert check_syntax(mo_file, P.name)

        # Operational parameter is time and scenario dependent
        P["vp"] = (1, 2, 3, 3, 2, 0.5)
        write_mo_file(P, mo_file, [])
        assert check_syntax(mo_file, P.name)
        write_mo_file(P, mo_file, [], use_time_variable_data=True)
        assert check_syntax(mo_file, P.name)

        # We can simulate the most general case
        assert simulate(mo_file, P.name)

        # NOTE: If you want to continue working with the results you can do
        # import scipy.io
        # mat = scipy.io.loadmat('dsres.mat')
