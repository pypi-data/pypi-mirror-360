"""Tests for user defined functions."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
import pytest

import comando
import comando.core


def test_user_defined_function():
    try:
        from comando.utility import define_function, evaluate, parse

        x = comando.core.Variable("x", bounds=(-1.5, 1.5))
        name = "lb_func"
        lb_func = define_function(name, lambda x, lb: max(x, lb))
        const_lb_func = lb_func(0, comando.EPS)
        assert float(const_lb_func) == comando.EPS
        lb_func_instance = lb_func(2 + x, comando.EPS)

        # NOTE: this part is here because a prior version of
        #       define_function always used sympy.Function instead of
        #       comando.Function.
        #       This resulted in directly created functions to be sympy
        #       types, but incorporating them in other expressions
        #       resulted in unwanted conversions!
        con_gts = (2 + x) / lb_func_instance
        # NOTE: sympy and symengine have different canonical forms
        comp_expr = con_gts.args[False].args[0]
        for expr in lb_func_instance, comp_expr:
            # assert get_type_name(expr) == name

            for sym in comp_expr.free_symbols:
                print(sym, type(sym))
            assert evaluate(expr) == 2
            assert expr == parse(expr)
    except NotImplementedError:
        pytest.xfail("backend is not available")
