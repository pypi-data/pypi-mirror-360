import os
import platform

import pytest

from tests import missing_module


@pytest.mark.skipif(
    platform.system() != "Windows", reason="DyOS interface is only tested on Windows"
)
@pytest.mark.skipif(
    missing_module("dymola"),
    reason='Dymola python package is not available. If you have Dymola installed ensure that the PYTHONPATH environment variable contains "<Dymola installation directory>\\Modelica\\Library\\python_interface\\dymola.egg"!',
)
def test_car_example(run_in_tmpdir, car_problem):
    P = car_problem
    with run_in_tmpdir:
        pwd = os.getcwd()
        label = P.name
        mo_file = label + ".mo"
        mo_path = os.path.join(pwd, mo_file)
        fmu_file = label
        fmu_path = os.path.join(pwd, fmu_file)
        controls = [P[label + "_accel"]]

        from comando.interfaces.modelica import write_mo_file

        write_mo_file(P, mo_path, controls)
        assert os.path.exists(mo_path)

        from comando.interfaces.dyos import generateFMU

        fmu_name = generateFMU(mo_path, includeSource=False)
        assert os.path.exists(fmu_name)

        fmu_bin = os.path.join(fmu_name, "binaries")
        fmu_doc = os.path.join(fmu_name, "documentation")
        fmu_descr = os.path.join(fmu_name, "modelDescription.xml")
        for content in [fmu_bin, fmu_doc, fmu_descr]:
            assert os.path.exists(content)

        from comando.interfaces.dyos import DyosProblem

        dyosProblem = DyosProblem(
            P,
            controls,  # List of operational variables, taken as controls
            # Since COMANDO only considers path constraints by default, we need to
            # specify any additional point constraints here.
            # In DyOS we can only constrain states or algebraic variables (i.e.,
            # all operational variables that are neither a state nor a control).
            # Furthermore, algebraic variables need to be declared as outputs in
            # the modelica file (all are by default, when using our interface).
            # A point-constraint requires the name of the constrained variable, a
            # lower and/or upper bound.
            # Optionally, the time can be specified via a "timePoint" entry,
            # otherwise the constraint is an end-point constraint.
            # If desired, the dual value can be given via the "lagrangeMultiplier"
            # entry.
            fmu_path,  # The absolute path to the contents of the extracted FMU
            point_constraints=dict(car_velo=dict(lowerBound=0, upperBound=0)),
            # Various options; TODO: names will be converted to snake_case in the future
            plotGridResolution=150,
            adapt_threshold=1e-8,
            maxAdaptSteps=5,
            # Passing adaptation options specific to a particular adaptation strategy
            # activate adaptation, i.e., any of
            # - "minRefinementLevel", "horRefinementDepth", "verRefinementDepth", "etres",
            #   or "epsilon" activate WAVELET adaptation and
            # - "includeTol" activates SWITCHING_FUNCTION adaptation
            # NOTE: If options for both strategies are given no adaptation is done!
            minRefinementLevel=1,
            maxRefinementLevel=20,
            horRefinementDepth=0,
            pcresolution=5,
            # maxStructureSteps=4,  # Passing this activates structure detection
            integrator_options={  # Needs to be Dict[str, str] !
                "absolute tolerance": "1e-7",
                "relative tolerance": "1e-7",
            },
        )

        # Write all problem input in proper json format
        car_in = "car_in.json"
        dyosProblem.dump_input(car_in)
        assert os.path.exists(os.path.join(pwd, car_in))

        car_out = "car_out.json"
        dyosProblem.nameOutputFile = car_out
        output = dyosProblem.solve()

        assert os.path.exists(os.path.join(pwd, car_out))
        # TODO: verify all returned output data matches the internal one.
        #       The below test fails, since the objects are in different memory locations
        # assert output == dyosProblem.Output
        assert hasattr(dyosProblem, "Output")

        velo_func = dyosProblem.result_functions["car_velo"]
        time_vals = {
            -1: float("nan"),
            0: 0.0,
            15: 10.0,
            35: 5.0,
            50: float("nan"),
        }
        for t, v in time_vals.items():
            res = velo_func(t)
            assert res == pytest.approx(v) or (res != res and v != v)
