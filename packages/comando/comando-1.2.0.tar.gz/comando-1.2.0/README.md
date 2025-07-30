<!-- This file is part of the COMANDO project which is released under the MIT
license. See file LICENSE for full license details.

AUTHOR: Marco Langiu -->
# COMANDO
COMANDO is a next generation modeling framework for **Component-Oriented Modeling and optimizAtion for Nonlinear Design and Operation of integrated energy systems**.
An energy system is considered to be a collection of different interconnected components whose purpose is to satisfy demands of various commodities such as, e.g., electric power, heat and cooling in a variety of different operating conditions.

When such a system is built (or extended), there are many design and operational decisions that need to be made.
In this context, optimizing the design and operation means finding a set of decisions that results in a minimal value for some generalized costs, taking into account restrictions imposed by individual components, their connections or by other safety-related, social, political, or economic considerations.

COMANDO provides means to...
- model existing energy systems and possible extension in a flexible,
  component-oriented fashion.
- use the resulting system models to create mathematical optimization problems
- solve these problems directly or use tools to automatically approximate/
  reformulate them to a form, more amenable to solution

## Referencing

When using COMANDO in an academic context please cite
[our associated publication](https://doi.org/10.1016/j.compchemeng.2021.107366).
```bibtex
@Article{langiu2021comando,
  title   = {COMANDO: A Next-Generation Open-Source Framework for Energy Systems Optimization},
  journal = {Computers & Chemical Engineering},
  volume  = {152},
  pages   = {107366},
  year    = {2021},
  issn    = {0098-1354},
  doi     = {https://doi.org/10.1016/j.compchemeng.2021.107366},
  author  = {Marco Langiu and David Yang Shu and Florian Joseph Baader and Dominik Hering and
             Uwe Bau and André Xhonneux and Dirk Müller and André Bardow and Alexander Mitsos
             and Manuel Dahmen}
}
```

## License

This project is licensed under the MIT License, for more information please refer to the [LICENSE](LICENSE) file.

## Documentation and support [![Documentation Status](https://readthedocs.org/projects/comando/badge/?version=latest)](https://comando.readthedocs.io/en/latest/?badge=latest)
The documentation for COMANDO is hosted on [readthedocs](https://comando.readthedocs.io/en/latest).
You can also build it locally, following the [instructions in the docs directory](docs/README.md).

For further questions, please write to [Manuel Dahmen](mailto:m.dahmen@fz-juelich.de)

## Installation
At the moment COMANDO is distributed exclusively via the IEK-10 GitLab server.
In the future we plan to upload COMANDO to the Python package index for easy installation with `pip`.
Until then we recommend cloning this repository with `git`.

### Installation options
To install a basic version of COMANDO issue:
```shell
python -m pip install comando
```
As with most packages, we recommended to install COMANDO within a virtual environment.

Several additional features can be installed by listing them in square brackets and separated by commas, e.g., for the [Pyomo](http://www.pyomo.org/) interface and packages required for automatic linearization you would run:
```shell
# NOTE: no spaces between features
python -m pip install comando[cpp-backend,pyomo,linearization]
```
For a list of all available features refer to [`pyproject.toml`](pyproject.toml).

In order to install all available extensions (**recommended**) run:
```shell
python -m pip install comando[all]
```

For development, you may alternatively clone this repository, and install COMANDO from its parent directory by replacing `comando` with `.` in the above command variants.
In addition, you may want to do an editable user installation, adding the `-e` flag, i.e:
```shell
# from the parent directory of this repository...
python -m pip install -e .[all]
```

At this point you have configured COMANDO for the formulation of models and optimization problems, but not yet for their solution!
You can refer to the [interfaces-specific README.md](comando/interfaces/README.md) for insight into which solver and AML interfaces are available and how to install and use them.

### Testing the installation
When comando was installed with the `test` or `dev` features, `pytest` should be available, and you can check if everything worked, by running:
```shell
# from the parent directory of this repository...
python -m pytest tests
```
Some tests will be skipped or have expected failures depending on the extras and interfaces you installed.

## Uninstallation
```shell
# from anywhere
python -m pip uninstall comando
```

## COMANDO Usage
This is a short summary of a typical COMANDO workflow.
For more detailed information please refer to the documentation.

The usage of COMANDO can be split into three phases

1. Modeling phase
   - Component model creation
   - System model creation
2. Problem formulation phase
   - problem generation
     - objective selection
     - time-structure selection
     - scenario-structure selection
     - providing data
   - problem reformulation
     - time discretization
     - linearization
     - ...
3. Problem solution phase
   - via a solver interface (e.g., [GUROBI](https://www.gurobi.com/), [BARON](https://minlp.com/baron-downloads), [MAiNGO](https://git.rwth-aachen.de/avt.svt/public/maingo))
   - via an algebraic modeling language (AML) interface (e.g., [GAMS](https://www.gams.com/download/), [PYOMO](http://www.pyomo.org/installation))
   - via custom algorithm

### Modeling phase
In the modeling phase the system behavior is specified in terms of the
component behavior and system structure.

#### Components
In COMANDO a component is the basic building block of an energy system.
It represents a model of a generic real-world component, specified via a collection of mathematical expressions in symbolic form.

The symbols contained in such an expression are either **Parameters** (input data) or **Variables** (representing decisions to be made).
Both kinds of symbols may be *'indexed'* or not, i.e., they may represent scalars or vectors of values.
An expression that contains any indexed symbol is itself considered to be indexed and it is assumed that all indexed symbols within an expression have conforming dimensions.

Whether a Variable is indexed or not is decided in the modeling phase, by explicitly creating a design variable (scalar) or an operational variable (indexed).
In contrast to this, whether a Parameter is indexed or not is decided during the problem formulation phase by assigning a scalar or vector of values.

The algebraic expressions created in this way can be stored under some name or combined to relational expressions of the form

- e1 <= e2
- e1 == e2
- e1 >= e2

constituting restrictions on the component behavior.

It is also possible to declare operational variables to be **'states'**, i.e., quantities whose time-derivative is given by some algebraic expression.
This allows the consideration of dynamic effects.

Components may also assign individual algebraic expressions to connectors, allowing them to be interfaced with other components.
Connectors may be specified as inputs, outputs or bidirectional connectors.
The former two restrict the value of the corresponding expression to be nonnegative and nonpositive, respectively, while the latter does not impose additional restrictions.

#### Systems
Systems are modeled as collections of interconnected components, i.e., a system model consists of a set of components and the specification of how their connectors are connected.
As systems inherit from components, they can define additional expressions constraints and connectors (for nesting of subsystems).

### Problem formulation phase
Given a system model, COMANDO can currently be used to create a *Problem* object, representing a mathematical optimization problem (OP) of the form:

![](Prob.png)

Where x and y are the vectors of design- and operation-variables, respectively.

#### Problem generation
F_I and F_II,s are user-specified scalar and indexed expressions corresponding to one-time and momentary costs, T_s are time horizons for different scenarios s, represented by a set of time-steps with possibly variable length, and S is a set of scenarios with corresponding weights w_s.

The constraints for the OP are automatically generated from the system model, i.e., all scalar relational expressions are taken as constraints and all indexed relational expressions are taken as constraints, parametrized by t, and s.

The dependence of the objective and constraint functions on time and scenario can be expressed in terms of the values or parameters p, which are user input.
This data can currently be given only in discrete form, i.e., for a discrete time and scenario.

**If any states were defined in the model the corresponding differential equations are currently discretized by default.**
An exception is the use of the [Pyomo.DAE](https://pyomo.readthedocs.io/en/stable/modeling_extensions/dae.html) interface, here the time-continuous representation is passed and discretization via collocation can be performed.
Data for the parameter values and initial guesses for the variable values can be provided based on the user-chosen sets T_s and S.

#### Problem reformulation
It is possible to use manual or automated reformulations of the original problem formulation.
An example reformulation is an automated linearization.

### Problem solution
Given a Problem, the user can chose to pass it directly to a solver capable of handling the corresponding problem type, transform the COMANDO Problem to a representation in an AML, or work directly with the COMANDO representation in a custom algorithm to preprocess or solve the Problem.
A list of available solver and AML interfaces can be found [here](comando/interfaces/README.md).