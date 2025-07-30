"""Configuration of the backends for COMANDO."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
import operator
import os
from enum import Enum
from functools import partial, reduce

os.environ["SYMPY_CACHE_SIZE"] = "None"
import sympy  # noqa: E402

sympy.Boolean = sympy.logic.boolalg.Boolean

try:
    # symengine brings significant speedup when using arrays of variables or constraints.
    # this code tries to use it, if available

    import symengine
    from symengine.lib import symengine_wrapper

    symengine.Boolean = symengine_wrapper.Boolean

    def _0(self):
        return self.args[0]

    def _1(self):
        return self.args[1]

    symengine_wrapper.Relational.lhs = property(_0)
    symengine_wrapper.Relational.rhs = property(_1)
    symengine_wrapper.Le.lts = property(_0)
    symengine_wrapper.Le.gts = property(_1)

    # this variable is used by core.py to correctly use the symengine.Symbol or the sympy.Symbol as a backup
    USING_SYMENGINE = True
except ImportError:
    USING_SYMENGINE = False


class Domain(Enum):
    """Simple Enum for variable domains, specify other types via bounds."""

    REAL = 1
    INTEGER = 2
    BINARY = 3


REAL, INTEGER, BINARY = Domain.REAL, Domain.INTEGER, Domain.BINARY
NAN = float("nan")
INF = float("inf")
UNBOUNDED = {-INF, INF}
EPS = 1e-9


def identity(expr):
    """Return expr."""
    return expr


def _sum(*args):
    """Return the sum of the elements in args."""
    return sum(args)


def prod(*args):
    """Return the product of the elements in args."""
    return reduce(operator.mul, args)


base_op_map = {
    "()": identity,
    "Add": _sum,
    "Neg": lambda arg: -arg,
    "Mul": prod,
    "Div": operator.truediv,
    "Pow": operator.pow,
    "Inv": partial(operator.truediv, 1),
    "LessThan": operator.le,
    "GreaterThan": operator.ge,
    "Equality": operator.eq,
}


exponential_function_names = {"exp", "log"}
nonsmooth_function_names = {"sign", "Abs", "Min", "Max", "ceiling", "floor"}
trigonometric_function_names = {"sin", "cos", "tan", "cot", "sec", "csc"}
trigonometric_inverse_function_names = {"asin", "acos", "atan", "acot", "asec", "acsc"}
hyperbolic_function_names = {"sinh", "cosh", "tanh", "coth", "sech", "csch"}
hyperbolic_inverse_function_names = {
    "asinh",
    "acosh",
    "atanh",
    "acoth",
    "asech",
    "acsch",
}
# NOTE: All of these functions depend on the backend and therefore need to be
#       looked up dynamically to allow for backend switches!
comando_functions = set().union(
    exponential_function_names,
    nonsmooth_function_names,
    trigonometric_function_names,
    trigonometric_inverse_function_names,
    hyperbolic_function_names,
    hyperbolic_inverse_function_names,
)


def _get_sympy_attr(name):
    if USING_SYMENGINE:
        return getattr(symengine, name)
    else:
        return getattr(sympy, name)


def __getattr__(name):
    """Get attributes that can't be found from the backend."""
    from comando import core

    try:
        return getattr(core, name)
    # if comando.core does not have an attribute, we check symengine/sympy for it
    except AttributeError:
        return _get_sympy_attr(name)


op_map = base_op_map.copy()
for f_name in comando_functions:
    op_map[f_name] = _get_sympy_attr(f_name)

Zero = _get_sympy_attr("S")(0)

from .core import *  # noqa: F401, E402, F403

# DEPRECATED - use evaluate from comando/utility.py instead!
## Teaching all sympy expressions about their value (Won't work with symengine!)
## sympy.Expr.value = property(comando.utility.evaluate)

# NOTE: must be last line of file!
__version__ = "1.2.0"