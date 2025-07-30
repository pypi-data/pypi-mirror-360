"""Package for generic modeling of energy system design and operation."""

# This file is part of the COMANDO project which is released under the MIT
# license. See file LICENSE for full license details.
#
# AUTHORS: Marco Langiu
from collections.abc import Iterable, Mapping

from pandas import DataFrame, Index, MultiIndex, Series, options

from comando import (
    BINARY,
    EPS,
    INF,
    INTEGER,
    NAN,
    REAL,
    USING_SYMENGINE,
    _get_sympy_attr,
)
from comando.utility import (
    _assert_algebraic,
    bounds,
    evaluate,
    fuzzy_not,
    get_index,
    get_type_name,
    is_indexed,
    split,
)

options.display.float_format = "{:,.4g}".format

BACKEND_SYMBOL = _get_sympy_attr("Symbol")


class Connector:
    """An interface used to connect one or more `Component` objects."""

    def __init__(self, component, name, expr):
        self.component = component
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f"Connector({self.component!r}, {self.name!r}, {self.expr!r})"


class ImpossibleConstraintException(Exception):
    pass


class DiscretizationParameters(object):
    """A set of parameters defining discretization"""

    def __init__(self, lower_bound, upper_bound, step_size):
        from numpy import arange

        assert upper_bound > lower_bound
        assert step_size < (upper_bound - lower_bound)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.step_size = step_size
        self.steps = arange(lower_bound, upper_bound, step_size)


def is_trivial(constraint, con_repr=None, warn=True):
    """Handle constraints that are trivially true or false."""
    # NOTE: We need to manually check for two alternative representations of
    #       Inequalities, since they appear to be implemented in a
    #       nonsymmetrical way. This is a bug in Sympy, also see:
    #       https://github.com/sympy/sympy/issues/20372

    from comando import Le, false, true

    if get_type_name(constraint) in {"LessThan", "GreaterThan"}:
        alt_repr = Le(*reversed(constraint.args))
        alternatives = [constraint, alt_repr]
    else:
        alternatives = [constraint]
    if con_repr is None:
        con_repr = "Constraint"
    for constraint in alternatives:
        if constraint is true:
            if warn:
                print(
                    f"\nWARNING: {con_repr} is always satisfied, "
                    "constraint will be skipped!\n"
                )
            return True
        elif constraint is false:
            raise ImpossibleConstraintException(f"{con_repr} can never be satisfied!")
        try:
            if bool(constraint):
                if warn:
                    print(
                        f"\nWARNING: {con_repr} is always satisfied, "
                        "constraint will be skipped!\n"
                    )
                return True
            else:
                raise ImpossibleConstraintException(
                    f"{con_repr} can never be satisfied!"
                )
        except TypeError:
            pass
    return False


class SlotSerializationMixin:
    """A Mixin to make classes with slots serializable."""

    __slots__ = ()

    def __getstate__(self):
        """Get the state."""
        # Collect all data stored in state and slots of mro hierarchy
        state = {}
        for ty in reversed(type(self).__mro__):  # reversed to overwrite
            try:
                state.update(ty.__getstate__())
            except (AttributeError, TypeError):
                pass
            if hasattr(ty, "__slots__"):
                for slot in ty.__slots__:
                    if hasattr(self, slot):
                        state[slot] = getattr(self, slot)
        return state
        # try:
        #     super_state = super().__getstate__()
        # except AttributeError:
        #     super_state = {}
        # return {**super_state, **{slot: getattr(self, slot)
        #         for slot in self.__slots__ if hasattr(self, slot)}}

    def __setstate__(self, state):
        """Set the state."""
        for slot, value in state.items():
            setattr(self, slot, value)


class Symbol(SlotSerializationMixin, BACKEND_SYMBOL):
    """A placeholder for a value which can occur within expressions."""

    __slots__ = ("_value", "_indexed", "_newargs")

    __qualname__ = "Symbol"

    def __new__(cls, name, **assumptions):
        self = BACKEND_SYMBOL.__new__(cls, name, **assumptions)
        if not hasattr(self, "_newargs"):
            self._newargs = (name,)
        return self

    def __getnewargs_ex__(self):
        return self._newargs, {}

    def __hash__(self):
        return id(self)
        return hash((type(self), str(self)))

    def __reduce__(self):
        if USING_SYMENGINE:
            return (Symbol, self._newargs)
        else:
            return super().__reduce__()

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and str(self) == str(other)
            and self._newargs == other._newargs
        )

    @property
    def is_indexed(self):
        """Check if the Symbol is indexed."""
        return self._indexed

    @property
    def value(self):
        """Get the Symbol's value."""
        return self._value


class Parameter(Symbol):
    """A `Symbol` representing a parameter whose value is known."""

    __slots__ = ("expansion", "_parent")

    __qualname__ = "Parameter"

    def __new__(cls, name, value=NAN, parent=None):
        self = Symbol.__new__(cls, name)

        self.value = value
        self._parent = parent

        self._newargs = name, value, parent

        return self

    def __reduce__(self):
        return (Parameter, self._newargs)

    @property
    def is_indexed(self):
        """Check whether the Parameter is indexed or not."""
        return self.expansion is not None

    @property
    def value(self):
        """Return the value or values of the Parameter."""
        return (
            self._value
            if self.expansion is None
            else self.expansion.apply(lambda e: getattr(e, "value"))
        )

    @value.setter
    def value(self, data):
        """Set the value of the Parameter.

        In contrast to the Variable, a Parameter can be made indexed by
        simply providing some Mapping or a pandas.Series that imply
        both an index and values.
        """
        if isinstance(data, (Mapping, Series)):
            self.expand(data)
            self._value = None
        else:
            self._value = None if data is None else float(data)
            self.expansion = None

    @property
    def indices(self):
        return self.expansion.keys()

    @property
    def elements(self):
        return self.expansion.values

    @property
    def items(self):
        return self.expansion.items()

    @property
    def parent(self):
        """Return the parent of this parameter."""
        return self._parent

    def expand(self, data):
        """Expand the `Parameter` with indexed data."""
        if self._parent is not None:
            raise RuntimeError(
                f"Attempted to expand parameter {self} "
                f"which is a member of {self._parent}!"
            )
        self.expansion = Series(
            (Parameter(f"{self.name}[{i}]", v, self) for i, v in data.items()),
            data.keys(),
            dtype="O",
        )

    def __getitem__(self, index):
        try:  # TODO: Custom errors still includes long stack trace...
            return self.expansion[index]
        except KeyError as ex:
            if self.expansion is None:
                raise TypeError(f"Parameter {self.name} is not indexed!") from ex
            raise IndexError("Parameter index out of range") from ex

    def __setitem__(self, index, value):
        """Set the value of the element corresponding to the index."""
        self.expansion[index].value = value

    def __iter__(self):
        """Iterate over the elements of this Parameter."""
        if self.expansion is None:
            raise TypeError(f"{self} is scalar.")
        for elem in self.elements:
            yield elem


class Variable(Symbol):
    """A `Symbol` representing a variable whose value is unknown."""

    __slots__ = (
        "_domain",
        "_bounds",
        "__bounds",
        "_discretization",
        "_init_val",
        "_parent",
    )

    __qualname__ = "Variable"

    def __new__(
        cls,
        name,
        domain=REAL,
        bounds=(None, None),
        discretization: DiscretizationParameters = None,
        init_val=None,
        indexed=False,
        parent=None,
    ):
        if domain is REAL:
            assumptions = {"real": True}
        elif domain in {INTEGER, BINARY}:
            assumptions = {"integer": True}
        else:
            raise ValueError(f"Domain must be either {REAL}, {INTEGER} or {BINARY}!")

        self = Symbol.__new__(cls, name, **assumptions)
        # WITH DEFAULT KWARG: domain='REAL'
        # if domain == 'Binaries':
        #     self._bounds = comando.Interval(0, 1)
        #     self._domain = comando.INTEGER
        # domain = comando.S(domain)
        # if domain not in (comando.INTEGER, comando.REAL):
        #     raise ValueError("Kwarg 'domain' must be one of 'REAL',"
        #                      "' INTEGER' or 'Binaries'!")
        self._domain = domain
        self.bounds = bounds
        self.__bounds = None  # storing bounds when Variable is fixed
        # TODO: This is a second option to create indexed
        #       variables, but at some point we should decide whether
        #       we simply distinguish by value or via a different class
        self._indexed = indexed
        self.init_val = init_val
        # NOTE: indexed Variables need an index that is specified later
        if not indexed:
            self.value = self.init_val
        self._parent = parent

        self._discretization = discretization

        self._newargs = (
            name,
            domain,
            bounds,
            discretization,
            init_val,
            indexed,
            parent,
        )

        return self

    def __reduce__(self):
        return (Variable, self._newargs)

    @property
    def parent(self):
        """Return the parent of this variable."""
        return self._parent

    @property
    def domain(self):
        return self._domain

    @property
    def discretization(self):
        return self._discretization.steps if self._discretization is not None else None
        # return self._discretization

    @discretization.setter
    def discretization(self, discretization: DiscretizationParameters):
        self._discretization = discretization
        self.lb = None  # reset to avoid conflicts
        self.ub = discretization.upper_bound
        self.lb = discretization.lower_bound

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        if self.domain is BINARY:
            lb = 0 if bounds[0] is None else bounds[0]
            ub = 1 if bounds[1] is None else bounds[1]
            if lb not in {0, 1} or ub not in {0, 1}:
                raise ValueError(
                    "Bounds for binary variables may "
                    "only be [0, 0], [0, 1] or [1, 1], "
                    f"but are {[lb, ub]}!"
                )
        else:
            lb = -INF if bounds[0] is None else bounds[0]
            ub = INF if bounds[1] is None else bounds[1]

        if lb <= ub:
            self._bounds = lb, ub  # comando.Interval(lb, ub)
        else:
            raise ValueError(
                "Lower bound of",
                self.name,
                "must be less than or equal to upper bound!",
            )

    @property
    def lb(self):
        return self.bounds[0]  # self.bounds.inf

    @lb.setter
    def lb(self, lb):
        lb = -INF if lb is None else lb
        if lb <= self.ub:
            self.bounds = lb, self.ub  # comando.Interval(lb, self.ub)
        else:
            raise ValueError(
                "Lower bound of",
                self.name,
                "must be less than or equal to upper bound!",
            )

    @property
    def ub(self):
        return self.bounds[1]  # self.bounds.sup

    @ub.setter
    def ub(self, ub):
        ub = INF if ub is None else ub
        if self.lb <= ub:
            self.bounds = self.lb, ub  # comando.Interval(self.lb, ub)
        else:
            raise ValueError(
                "Upper bound of",
                self.name,
                "must be greater than or equal to lower bound!",
            )

    @Symbol.value.setter
    def value(self, data):
        """Set the value of the Variable.

        A variable is declared to be either indexed or not at creation;
        according to this specification the value is a scalar or
        pandas.Series.
        If the Variable is indexed, the first time the value is set, it
        must be specified via a Mapping or pandas.Series, which imply
        an index.
        After this the values can be changed by simply providing
        iterables of appropriate length and the index and length can be
        adapted by again specifying the value via a Mapping or Series.
        """
        if self._indexed:
            if isinstance(data, (Mapping, Series)):
                self._value = Series(data)
            if isinstance(data, (Iterable)):
                try:
                    self._value = Series(data, self._value.index)
                except AttributeError:
                    raise AttributeError(
                        "The variable's index has "
                        "not been specified yet, set "
                        "the value using a Mapping "
                        "or a pandas.Series!"
                    )
                except ValueError:
                    raise ValueError(
                        "The variable's index does not "
                        "match the length of the "
                        "provided value!"
                    )
                    # data & index don't match -> infer from data
                    self._value = Series(data)
        else:
            self._value = NAN if data is None else float(data)

    def fix(self, value=None):
        """Fix the variable by setting both bounds to `value`."""
        if value is None:
            try:
                value = self._value
            except AttributeError:  # uninitialized indexed Variable
                value = self._init_val
        if self.is_integer and not float(value).is_integer():
            lb, ub = self.__bounds if self.__bounds else self.bounds
            if lb <= value <= ub:
                from warnings import warn

                round_val = round(value)
                warn(f"Fixing value of {self.name} to {round_val} instead of {value}!")
                value = round_val
            else:
                kind = self.domain.name.lower()
                raise ValueError(
                    f"Cannot fix {kind} variable "
                    f'"{self.name}" with bounds '
                    f"{lb, ub} to non-integer value "
                    f"{value}!"
                )
        # Get original bounds (either the previously fixed or the
        # current ones)
        lb, ub = self.__bounds if self.__bounds else self.bounds
        if value <= lb - EPS or ub + EPS <= value:
            raise ValueError(
                f"Value {value} is not within original bounds [{lb}, {ub}]"
            )
        self.__bounds = lb, ub  # NoOp or setting current bounds
        self.value = value
        self.bounds = (value, value)

    def unfix(self):
        """Recover the original bounds."""
        if self.__bounds:
            self.bounds = self.__bounds
            self.__bounds = None

    @property
    def init_val(self):
        return self._init_val

    @init_val.setter
    def init_val(self, val):
        from math import ceil, floor, isinf, isnan

        lb, ub = self._bounds
        if val is None:
            if self.is_binary:
                self._init_val = 0
                return
            tmp = (ub + lb) * 0.5
            if isnan(tmp) or isinf(tmp):
                if not isnan(ub) and not isinf(ub):
                    self._init_val = floor(ub) if self.is_integer else ub
                elif not isnan(lb) and not isinf(lb):
                    self._init_val = ceil(lb) if self.is_integer else lb
                else:
                    self._init_val = 0
                return
            val = tmp
        if self.is_integer:  # make adjustments for the integer case
            # ... round val to nearest int
            if not float(val).is_integer():
                l_val = floor(val)
                u_val = ceil(val)
                val = l_val if val - l_val <= u_val - val else u_val
            # TODO: could be moved to the bounds property?
            lb = ceil(lb)
            ub = floor(ub)
        if lb <= val <= ub:
            self._init_val = val
            return
        raise ValueError(f"init_val {val} is incompatible with bounds [{lb}, {ub}]!")

    @property
    def is_integer(self):
        return self.domain in {BINARY, INTEGER}

    @property
    def is_binary(self):
        return self.domain is BINARY

    # TODO: Might need EPS for comparisons as well
    @property
    def is_positive(self):
        """Check if all possible values of the variable are positive.

        We can assert positivity if the lower bound is positive,
        otherwise we can assert nonpositivity if the upper bound is
        nonpositive. If we cannot assert either of these facts, the
        variable may contain both positive and negative values. To
        reflect this we return None.
        """
        return True if self.lb > 0 else False if self.ub <= 0 else None

    @property
    def is_negative(self):
        """Check if all possible values of the variable are negative.

        We can assert negativity if the upper bound is negative,
        otherwise we can assert nonnegativity if the lower bound is
        nonnegative. If we cannot assert either of these facts, the
        variable may contain both positive and negative values. To
        reflect this we return None.
        """
        return True if self.ub < 0 else False if self.lb >= 0 else None

    @property
    def is_nonnegative(self):
        """Check if all possible values of the variable are negative.

        This is the fuzzy not of self.is_negative
        """
        # True if self.lb >= 0 else False if self.ub < 0 else None
        return fuzzy_not(self.is_negative)

    @property
    def is_nonpositive(self):
        """Check if all possible values of the variable are negative.

        This is the fuzzy not of self.is_negative
        """
        # True if self.ub <= 0 else False if self.lb > 0 else None
        return fuzzy_not(self.is_positive)


class VariableVector(Symbol):
    """A `Symbol` representing a vector of `Variables`."""

    __slots__ = (
        "_domain",
        "_bounds",
        "__bounds",
        "_discretization",
        "_init_val",
        "expansion",
    )

    __qualname__ = "VariableVector"

    def __new__(
        cls,
        name,
        domain=REAL,
        bounds=(None, None),
        discretization: DiscretizationParameters = None,
        init_val=None,
    ):
        if domain is REAL:
            assumptions = {"real": True}
        elif domain in {INTEGER, BINARY}:
            assumptions = {"integer": True}
        else:
            raise ValueError(f"Domain must be either {REAL}, {INTEGER} or {BINARY}!")

        self = Symbol.__new__(cls, name, **assumptions)

        self._domain = domain
        self.expansion = Series(dtype="O")

        self.bounds = bounds
        # TODO
        self.__bounds = None  # for storing bounds
        # self._bounds = bounds
        self.init_val = init_val

        self._discretization = discretization

        self._newargs = name, domain, bounds, discretization, init_val

        return self

    def __reduce__(self):
        return (VariableVector, self._newargs)

    # TODO: Rename (here and elsewehere) to is_indexed
    @property
    def is_indexed(self):
        return True

    @property
    def is_expanded(self):
        return bool(len(self.expansion))

    @property
    def domain(self):
        return self._domain

    @property
    def indices(self):
        return self.expansion.keys()

    @property
    def elements(self):
        return self.expansion.values

    @property
    def items(self):
        return self.expansion.items()

    def _get_property(self, property):
        """Get a `Series` with property values from `self.elements`."""
        return self.expansion.apply(lambda e: getattr(e, property)).rename(property)

    def _set_property(self, property, scalar_or_mapping):
        """Set the property values of `self.elements`."""
        # Attempting to treat `scalar_or_mapping` as a mapping...
        if not self.is_expanded:
            raise RuntimeError(
                f"VariableVector {self.name} has not been instantiated yet."
            )
        if isinstance(scalar_or_mapping, (Mapping, Series, DataFrame)):
            for i, elem in self.expansion.items():
                try:
                    setattr(elem, property, scalar_or_mapping[i])
                except KeyError:
                    continue  # Leave existing value
            return
        try:  # treating as iterable
            for (i, elem), val in zip(self.expansion.items(), scalar_or_mapping):
                setattr(elem, property, val)
            return
        except TypeError:  # scalar_or_mapping not iterable -> scalar
            for elem in self.elements:
                setattr(elem, property, scalar_or_mapping)
            return
        raise RuntimeError(
            f"Could not set {property} property of "
            f"{self.name} with {scalar_or_mapping}!"
        )

    @property
    def value(self):
        values = self._get_property("value")
        return values if len(values) else None

    @value.setter
    def value(self, values):
        self._set_property("value", values)

    @property
    def discretization(self):
        return self._discretization.steps if self._discretization is not None else None

    @discretization.setter
    def discretization(self, discretization: DiscretizationParameters):
        self._discretization = discretization
        self.lb = None  # reset to avoid conflicts
        self.ub = discretization.upper_bound
        self.lb = discretization.lower_bound

    @property
    # def bounds(self): return self._bounds
    def bounds(self):
        return (
            (self._get_property("lb"), self._get_property("ub"))
            if self.is_expanded
            else self._bounds
        )

    @bounds.setter
    def bounds(self, bounds):
        if self.is_expanded:
            # NOTE: We expect bounds to be a 2-tuple of scalars,
            #       Iterables or Mappings
            _lb, _ub = (0, 1) if self.domain is BINARY else (-INF, INF)
            lb, ub = self._get_property("lb"), self._get_property("ub")
            if isinstance(bounds[0], (Iterable, Mapping, Series)):
                lb.update(Series(bounds[0]).fillna(_lb))
            else:
                lb[:] = _lb if bounds[0] is None else bounds[0]
            if isinstance(bounds[1], (Iterable, Mapping, Series)):
                ub.update(Series(bounds[1]).fillna(_ub))
            else:
                ub[:] = _ub if bounds[1] is None else bounds[1]
            if all(lb <= ub):
                self._bounds = lb.min(), ub.max()
                bounds_dict = {
                    index: tuple(bounds)
                    for index, bounds in lb.to_frame().join(ub).T.items()
                }
                self._set_property("bounds", bounds_dict)
            else:
                raise ValueError(
                    "Lower bound of " + self.name + " must be less than or "
                    "equal to upper bound!"
                )
        else:
            # NOTE: We expect bounds to be a 2-tuple of scalars
            if self.domain is BINARY:
                lb = 0 if bounds[0] is None else bounds[0]
                ub = 1 if bounds[1] is None else bounds[1]
                if lb not in {0, 1} or ub not in {0, 1}:
                    raise ValueError(
                        "Bounds for binary variables may "
                        "only be [0, 0], [0, 1] or "
                        f"[1, 1], but are {[lb, ub]}!"
                    )
            else:
                lb = -INF if bounds[0] is None else bounds[0]
                ub = INF if bounds[1] is None else bounds[1]

            if lb <= ub:
                self._bounds = lb, ub  # comando.Interval(lb, ub)
            else:
                raise ValueError(
                    "Lower bound of " + self.name + " must be less than or "
                    "equal to upper bound!"
                )

    @property
    # def lb(self): return self._bounds[0]
    def lb(self):
        return self._get_property("lb") if self.is_expanded else self._bounds[0]

    @lb.setter
    def lb(self, lb):
        try:  # Scalar lb
            lb = -INF if lb is None else float(lb)
        except (ValueError, TypeError):  # assume intended for elements
            # setting lb by iterable
            old_lb = self.lb
            try:
                self._set_property("lb", lb)
            except ValueError as e:
                self._set_property("lb", old_lb)
                raise e
            self._bounds = min(self.lb), self._bounds[1]
            return
        ub = self.ub
        if self.is_expanded:
            if all(lb <= ub):
                self._set_property("lb", lb)
                self._bounds = (self.lb.min(), self._bounds[1])
            else:
                raise ValueError(
                    "Lower bound of " + self.name + " must be less than or "
                    "equal to upper bound!"
                )
        else:
            if lb <= ub:
                self._bounds = lb, ub
            else:
                raise ValueError(
                    "Lower bound of " + self.name + " must be less than or "
                    "equal to upper bound!"
                )

    @property
    # def ub(self): return self._bounds[1]
    def ub(self):
        return self._get_property("ub") if self.is_expanded else self._bounds[1]

    @ub.setter
    def ub(self, ub):
        try:  # Scalar ub
            ub = INF if ub is None else float(ub)
        except (ValueError, TypeError):  # assume intended for elements
            # setting ub by iterable
            old_ub = self.ub
            try:
                self._set_property("ub", ub)
            except ValueError as e:
                self._set_property("ub", old_ub)
                raise e
            self._bounds = self._bounds[0], max(self.ub)
            return
        lb = self.lb
        if self.is_expanded:
            if all(lb <= ub):
                self._set_property("ub", ub)
                self._bounds = self._bounds[0], self.ub.max()
            else:
                raise ValueError(
                    "Upper bound of " + self.name + " must be greater than or "
                    "equal to lower bound!"
                )
        else:
            if lb <= ub:
                self._bounds = lb, ub
            else:
                raise ValueError(
                    "Upper bound of " + self.name + " must be greater than or "
                    "equal to lower bound!"
                )
        #
        # self._set_property('ub', ub)
        # ub = INF if ub is None else ub
        # if self.lb <= ub:
        #     self.bounds = self.lb, ub

    @property
    def init_val(self):
        return self._init_val

    @init_val.setter
    def init_val(self, val):
        from math import ceil, floor, isinf, isnan

        lb, ub = self._bounds
        if val is None:
            tmp = (ub + lb) * 0.5
            if isnan(tmp) or isinf(tmp):
                if not isnan(ub) and not isinf(ub):
                    self._init_val = floor(ub) if self.is_integer else ub
                elif not isnan(lb) and not isinf(lb):
                    self._init_val = ceil(lb) if self.is_integer else lb
                else:
                    self._init_val = 0
                return
            val = tmp
        if self.is_integer:  # make adjustments for the integer case
            if not float(val).is_integer():  # ... round to nearest int
                l_val = floor(val)
                u_val = ceil(val)
                val = l_val if val - l_val <= u_val - val else u_val
            # TODO: could be moved to the bounds property?
            lb = ceil(lb)
            ub = floor(ub)
        if lb <= val <= ub:
            self._init_val = val
            return
        raise ValueError(f"init_val {val} is incompatible with bounds [{lb}, {ub}]!")

    def fix(self, value=None):
        """Fix `self.elements` by setting both bounds to `value`."""
        if value is None:
            try:
                value = self.value
            except AttributeError:  # uninitialized
                value = self._init_val

        lb, ub = self.__bounds if self.__bounds else self.bounds
        if self.is_expanded:
            if any(value <= lb - EPS) or any(ub + EPS <= value):
                raise ValueError(
                    f"Value {value} is not within original bounds [{lb}, {ub}]"
                )
            self.value = value
        elif value <= lb - EPS or ub + EPS <= value:
            raise ValueError(
                f"Value {value} is not within original bounds [{lb}, {ub}]"
            )
        self.__bounds = lb, ub  # NoOp or setting current bounds
        self.bounds = (value, value)

    def unfix(self):
        """Recover the original bounds."""
        self.bounds = self.__bounds
        self.__bounds = None

    @property
    def is_integer(self):
        return self.domain in {BINARY, INTEGER}

    @property
    def is_binary(self):
        return self.domain is BINARY

    @property
    def is_positive(self):
        """Check if all possible values of the variable are positive.

        We can assert positivity if the lower bound is positive,
        otherwise we can assert nonpositivity if the upper bound is
        nonpositive. If we cannot assert either of these facts, the
        variable may contain both positive and negative values. To
        reflect this we return None.
        """
        try:
            return True if self.lb > 0 else False if self.ub <= 0 else None
        except ValueError:
            return True if all(self.lb > 0) else False if all(self.ub <= 0) else None

    @property
    def is_negative(self):
        """Check if all possible values of the variable are negative.

        We can assert negativity if the upper bound is negative,
        otherwise we can assert nonnegativity if the lower bound is
        nonnegative. If we cannot assert either of these facts, the
        variable may contain both positive and negative values. To
        reflect this we return None.
        """
        try:
            return True if self.ub < 0 else False if self.lb >= 0 else None
        except ValueError:
            return True if all(self.ub < 0) else False if all(self.lb >= 0) else None

    @property
    def is_nonnegative(self):
        """Check if all possible values of the variable are negative.

        This is the fuzzy not of self.is_negative
        """
        # True if self.lb >= 0 else False if self.ub < 0 else None
        return fuzzy_not(self.is_negative)

    @property
    def is_nonpositive(self):
        """Check if all possible values of the variable are negative.

        This is the fuzzy not of self.is_negative
        """
        # True if self.ub <= 0 else False if self.lb > 0 else None
        return fuzzy_not(self.is_positive)

    def instantiate(self, index):
        """Create `Variable` instances for every element in `index`."""
        self.expansion = Series(
            (
                Variable(
                    name=f"{self.name}[{i}]",
                    domain=self.domain,
                    bounds=self._bounds,
                    discretization=self._discretization,
                    init_val=self.init_val,
                    parent=self,
                )
                for i in index
            ),
            index,
            dtype="O",
        )

    def __getitem__(self, index):
        try:  # TODO: Custom errors still includes long stack trace...
            return self.expansion[index]
        except KeyError as ex:
            raise IndexError("Vector index out of range") from ex

    def __setitem__(self, index, value):
        """Set the value of the element corresponding to the index."""
        self.expansion[index].value = value

    def __iter__(self):
        """Iterate over the elements of this VariableVector."""
        for elem in self.elements:
            yield elem


# TODO: Generalize the concept of objective to design cost and operational cost
#       with appropriate annualization in the EnergySystem class. For example,
#       when minimizing CO2 production, a Component's design cost might be the
#       Carbon footprint for its production and its operational cost might be
#       the CO2 ouput caused by operation.
class Component:
    """A component representing a part of an energy system.

    The Component class is a model of a generic real-world component of an
    energy system, represented by a collection of algebraic and logical
    expressions which describe how the component can be controlled, its
    limitations and its interactions with other components.

    For every component, two kinds of decisions may be taken:
    - design decisions a.k.a. 'here-and-now' decisions
    - operational decisions a.k.a. 'wait-and-see' decisions
    The former constitute decisions that are taken once, prior to all operation
    while the operational decisions need to be taken for every time-point under
    consideration.

    The component may define named expressions that can be accessed at any time
    for informational purposes. These expressions may also be used to impose
    additional constraints at a later stage, or to aggregate information from
    multiple different components. In a similar way an objective for a system
    optimization can be generated by aggregating different types of costs
    defined by some subset of the system's components.

    Parameters that are contained in the various expressions may or may not be
    given a default value that can be changed at a later stage.

    Attributes
    ----------
    label : `str`
        A unique sting that serves as an identifier

    parameters : `set` of `Symbol`
        Set of unspecified system parameters the user can assign values to.

    design_variables : `set` of `Variable`
        Set of variables of the design stage, i.e. time-independent variables
        such as the number or size of newly added components.

    operational_variables : `set` of `Variable`
        Set of unique names for variables of the operational stage, e.g.
        the output of a given component or an operational state.

    states : dict
        Dictionary mapping a subset of operational_variables to automatically
        created Variables, representing the corresponding time derivatives.
        Examples are the SOC of a battery, the fill-level of a tank, etc.

    constraints : `dict` of `sympy.core.relational.Relational`
        Dictionary of relational sympy expressions that represent constraints.

    expressions : `dict`
        mapping of shared identifiers to algebraic sympy expressions.
        The expressions different `Component` instances associate with a shared
        identifier may be aggregated to additional constraints or objectives.

    connectors : `dict`
        mapping of strings to algebraic expressions representing in or outputs
        to the component. When multiple connectors are connected to each other,
        the connection represents the requirement that the sum of their
        expressions need to be equal to zero.
    """

    existing_components = dict()

    def __init__(self, label):
        if label in self.existing_components:
            raise RuntimeError(
                f"A component with the label {label} has already been defined!"
            )
        self.existing_components[label] = self
        self._label = label

        # self._parameters = set()
        self._parameters_dict = dict()
        # self._design_variables = set()
        self._design_variables_dict = dict()
        # self._operational_variables = set()
        self._operational_variables_dict = dict()

        self._constraints_dict = dict()
        self._expressions_dict = dict()

        self._states_dict = dict()

        self.connectors = dict()

    def _prefix(self, name):
        """Prefix the given name to obtain a unique identifier."""
        return f"{self.label}_{name}"

    def __repr__(self):
        return f"Component({self.label!r})"

    def __iter__(self):
        """Prevent iteration that is implicitly introduced with __getitem__."""
        raise TypeError("Component object is not iterable")

    def __getitem__(self, identifier):
        """Get a Connector, Parameter or Variable matching the identifier."""
        # NOTE: We may add this for users confused by system scope access...
        # if identifier.startswith(self.label + '_'):  # strip prefix
        #     identifier = identifier[len(self.label) + 1:]
        for d in [
            self._parameters_dict,
            self._design_variables_dict,
            self._operational_variables_dict,
            self._constraints_dict,
            self._expressions_dict,
        ]:
            if identifier in d:
                return d[identifier]
            # TODO: also search components?
        raise KeyError(f"No entry for '{identifier}' found in {self}!")

    @property
    def label(self):
        """Get the Component's unique label."""
        return self._label

    # Define descriptors for all symbols, constraints and expressions
    for ty in [
        "parameters",
        "design_variables",
        "operational_variables",
        "constraints",
        "expressions",
    ]:
        exec(
            f"""
@property
def {ty}(self):
    \"\"\"Get a set of the Component's {ty}.\"\"\"
    return set(self._{ty}_dict.values())
"""
        )
        exec(
            f"""
@property
def {ty}_dict(self):
    \"\"\"Get a dictionary of the Component's {ty}.\"\"\"
    return {{self._prefix(n): p for n, p in self._{ty}_dict.items()}}
"""
        )
    del ty

    @property
    def states(self):
        return set(self._states_dict)

    @property
    def states_dict(self):
        return self._states_dict.copy()

    def make_parameter(self, name, value=None):
        """Create a parameter with a localized name & store it."""
        par = Parameter(self._prefix(name), value=value)
        # self._parameters.add(par)
        self._parameters_dict[name] = par
        return par

    def make_design_variable(
        self, name, domain=REAL, bounds=(None, None), discretization=None, init_val=None
    ):
        """Create a design variable with a localized name & store it."""
        var = Variable(
            name=self._prefix(name),
            domain=domain,
            bounds=bounds,
            discretization=discretization,
            init_val=init_val,
        )
        self._design_variables_dict[name] = var
        return var

    def make_operational_variable(
        self, name, domain=REAL, bounds=(None, None), discretization=None, init_val=None
    ):
        """Create an operational variable with a localized name & store it."""
        var = VariableVector(
            name=self._prefix(name),
            domain=domain,
            bounds=bounds,
            discretization=discretization,
            init_val=init_val,
        )
        self._operational_variables_dict[name] = var
        return var

    # TODO: Make the creation of derivative variable optional (and allow for
    #       the use of state_change instead)
    def declare_state(
        self,
        var,
        rate_of_change=None,
        init_state=float("nan"),
        der_bounds=(None, None),
        der_init_val=None,
    ):
        """Declare var to be a state.

        A state is an operational variable whose time derivative is described
        by the rate_of_change expression, beginning at an initial_state.
        """
        if var.name.startswith(self.label):
            name = var.name[len(self.label) + 1 :]  # strip prefix
        else:  # This can happen if the variable was not created in self!
            name = var.name
        der_s = self.make_operational_variable(
            f"{name}dot", var.domain, der_bounds, der_init_val
        )
        if isinstance(init_state, Symbol):
            pass
        elif isinstance(init_state, (int, float)):  # create parameter for user
            init_state = self.make_parameter(f"{name}_init", init_state)
        else:
            raise TypeError(f"Cannot use '{init_state}' as an initial state!")

        # TODO: should we already do this or wait until problem generation?
        if rate_of_change is not None:
            self.add_eq_constraint(der_s, rate_of_change, name=f"state_{name}")

        # TODO: Which order should we store this?
        self._states_dict[var] = (init_state, der_s, rate_of_change)
        return der_s

    # TODO: Should we actually consider domains other than REAL???
    def make_state(
        self,
        name,
        rate_of_change=None,
        init_state=float("nan"),
        domain=REAL,
        bounds=(None, None),
        der_bounds=(None, None),
        init_val=None,
        der_init_val=None,
    ):
        """Create a state with a localized name, its derivative and store them.

        A state is an operational variable whose time derivative is described
        by the rate_of_change expression, beginning at an initial_state.
        """
        s = self.make_operational_variable(name, domain, bounds, init_val)
        return s, self.declare_state(
            s, rate_of_change, init_state, der_bounds, der_init_val
        )

    def _handle_constraint(self, rel_op, lhs_expr, rhs_expr, name):
        from comando import __getattr__ as comandoattr

        _assert_algebraic(lhs_expr)
        _assert_algebraic(rhs_expr)
        token = {"Le": "≤", "Eq": "=", "Ge": "≥"}[rel_op]
        con = comandoattr(rel_op)(lhs_expr, rhs_expr)
        if name is None:
            name = f"{lhs_expr} {token} {rhs_expr}"
        if not is_trivial(con, f"Constraint {name} in {self._label}"):
            self._constraints_dict[name] = con

    def add_le_constraint(self, lhs_expr, rhs_expr, name=None):
        """Add a constraint of the form lhs_expr ≤ rhs_expr."""
        self._handle_constraint("Le", lhs_expr, rhs_expr, name)

    def add_ge_constraint(self, lhs_expr, rhs_expr, name=None):
        """Add a constraint of the form lhs_expr ≥ rhs_expr."""
        self._handle_constraint("Ge", lhs_expr, rhs_expr, name)

    def add_eq_constraint(self, lhs_expr, rhs_expr, name=None):
        """Add a constraint of the form lhs_expr = rhs_expr."""
        self._handle_constraint("Eq", lhs_expr, rhs_expr, name)

    # TODO: Logical constraints (http://ben-israel.rutgers.edu/386/Logic.pdf)
    ###########################################################################
    # def declare_alternative(self, con1_id, con2_id, name=None):
    #     """Specify that at least one of the two constraints must hold."""
    #     pass
    #
    # def enforce_k(self, *con_ids, k, name=None):
    #     """Specify that at least k of the constraints must hold."""
    #     pass
    #
    # def declare_exclusive(self, con1_id, con2_id, name=None):
    #     """Specify that only a single one of the two constraints hold."""
    #     pass
    #
    # def declare_implication(self, con1_id, con2_id, name=None):
    #     """Specify that if con1 holds con2 must also hold."""
    #     pass
    #
    # def declare_equivalence(self, con1_id, con2_id, name=None):
    #     """Specify that either both con1 and con2 hold or none."""
    #     pass
    ###########################################################################

    # TODO: Either introduce a modifier of this form or a flag in the
    #       `make_xxx_variable` methods.
    # def declare_semicont(self, var, bound):
    #     """Specify that the given variable is semicontinuous.
    #
    #     A semicontinuous variable can be either zero or above/below a certain
    #     threshold value. This behavior is enforced on the given variable by
    #     introducing a binary variable and two constraints.
    #     The bound argument may be positive or negative resulting in a
    #     lower or upper semi-continuous bound respectively.
    #     """
    #     name = var.name
    #     active = self.make_operational_variable(f'{name}_active',
    #                                             domain=INTEGER, bounds=(0, 1))
    #     # the upper/lower bound for Qdot_out is given by nominal output, but
    #     # since that's a variable  we have to write this bound as a constraint:
    #     self.add_le_constraint(var, active * var.ub, name=f'{name}_limit')
    #     self.add_ge_constraint(var, active * lb, name=f'{name}_threshold')

    def add_expression(self, identifier, expr):
        """Add a named algebraic expression."""
        from comando import S

        _assert_algebraic(expr)
        self._expressions_dict[identifier] = S(expr)
        return expr

    def get_expression(self, identifier, default=None):
        """Get the expression corresponding to the identifier."""
        if default is None:
            return self._expressions_dict[identifier]
        return self._expressions_dict.get(identifier, default)

    def add_connector(self, id, expr):
        """Insert the connector in connectors and add it as an attribute."""
        connector = Connector(self, id, expr)
        self.connectors[id] = connector
        setattr(self, id, connector)

    # TODO: Probably we should have a simple add_connector method instead!
    def add_connectors(self, id=None, expr=None, **connectors):
        """Add one or more named connectors to this component.

        Examples
        --------
        >>> self.add_connectors('A', sympy.S('A'))
        >>> self.add_connectors(B=sympy.S('B'), C=sympy.S('C'))
        """
        if id and expr is not None:  # user passed (identifier, expr)
            if getattr(self, id, None):
                raise RuntimeError(
                    f"Cannot add connector: {self} already has "
                    f"an attribute called {id}!"
                )
            _assert_algebraic(expr)
            self.add_connector(id, expr)
        else:  # user passed (**connectors)
            for id, expr in connectors.items():  # Check if all is well first!
                if getattr(self, id, None):
                    raise RuntimeError(
                        f"Cannot add connector: {self} already "
                        f"has an attribute called {id}!"
                    )
                _assert_algebraic(expr)
            for id, expr in connectors.items():  # Then do the work
                self.add_connector(id, expr)

    def add_input(self, identifier, expr):
        """Add a connector that corresponds to an input into the component.

        The expr is assumed to always be positive and is thus bounded by 0 from
        below. By convention the input into a Component is positive so the new
        Connector's expression corresponds to expr.
        """
        try:  # If it's a variable, bound it corresponding to the input...
            expr.lb = 0
        except AttributeError:  # ...or add a constraint ensuring positivity
            self.add_le_constraint(0, expr, identifier)
        self.add_connector(identifier, expr)

    def add_output(self, identifier, expr):
        """Add a connector that corresponds to an output from the component.

        The expr is assumed to always be positive and is thus bounded by 0 from
        below. By convention the output from a Component is negative so the new
        Connector's expression corresponds to the negated expr.
        """
        try:  # Bound the variable corresponding to the input...
            expr.lb = 0
        except AttributeError:  # ...or add a constraint ensuring positivity
            self.add_le_constraint(0, expr, identifier)
        self.add_connector(identifier, -expr)


class ConnectorUnion(Connector):
    """A union of multiple Connectors."""

    def __init__(self, component, name, *connectors):
        self.component = component
        self.name = name
        self.elements = set(connectors)

    @property
    def expr(self):
        """Return an expression for the flow through the ConnectorUnion."""
        return sum(c.expr for c in self.elements)


class System(Component):
    """A class for a generic system, made up of individual components.

    Note that a system is itself a component and can therefore function as a
    subsystem for a larger system, allowing for nested structures!

    Attributes
    ----------
    components : iterable of `Component`
        components that form part of the considered energy system
    connections : dict
        mapping of `str` to an iterable of `Connector`. The in- and outputs of
        all connectors within an iterable are assumed to balance each other.
    """

    def __init__(self, label, components=None, connections=None):
        super().__init__(label)
        self._components = set()
        if components is not None:
            for component in components:
                self.add(component)

        # NOTE: A 'bus' is understood to be a set of connected  `Connector`
        #       objects, while a 'connection' is a mapping of an identifier to
        #       a bus!
        self.connections = {}
        if connections is not None:
            for bus_id, bus in connections.items():
                self.connect(bus_id, bus)

    def __repr__(self):
        return (
            f"System({self.label!r}, components={self._components}, "
            f"connections={self.connections})"
        )

    def __iter__(self):
        """Iterate over the components of the system."""
        for component in self.components:
            yield component

    def __getitem__(self, identifier):
        """Get a Connector, Parameter or Variable matching the identifier."""
        # NOTE: We may add this for users confused by system scope access...
        # if identifier.startswith(self.label + '_'):  # strip prefix
        #     identifier = identifier[len(self.label) + 1:]
        for ty in [
            "parameters",
            "design_variables",
            "operational_variables",
            "constraints",
            "expressions",
        ]:
            # For all types of attributes check own then those of components...
            for d in [
                getattr(self, f"_{ty}_dict"),
                *[getattr(c, f"{ty}_dict") for c in self.components],
            ]:
                if identifier in d:
                    return d[identifier]
        raise KeyError(f"No entry for '{identifier}' found in {self}!")

    @property
    def components(self):
        """Get the set of components that are part of the system."""
        return self._components.union(
            *(c.components for c in self._components if isinstance(c, System))
        )

    # Define descriptors for all symbols
    for ty in [
        "parameters",
        "design_variables",
        "operational_variables",
        "constraints",
        "expressions",
    ]:
        exec(
            f"""
@property
def {ty}(self):
    \"\"\"Get a set of the System's {ty}.\"\"\"
    res = set(self._{ty}_dict.values())
    return res.union(*(c.{ty} for c in self.components))
"""
        )
        exec(
            f"""
@property
def {ty}_dict(self):
    \"\"\"Get a dictionary of the System's {ty}.\"\"\"
    res = {{self._prefix(n): p for n, p in self._{ty}_dict.items()}}
    for c in self.components:
        res.update(c.{ty}_dict)
    return res
"""
        )
    del ty

    @property
    def states(self):
        """Get a set of the System's states."""
        res = set(self._states_dict)
        return res.union(*(c.states for c in self.components))

    @property
    def states_dict(self):
        """Get a set of the System's states."""
        res = self._states_dict.copy()
        for c in self.components:
            res.update(c.states_dict)
        return res

    def _update_connection_constraint(self, bus_id):
        """Update the constraint enforcing a given connection."""
        bus = self.connections[bus_id]
        lhs = sum(connector.expr for connector in bus)
        self.add_eq_constraint(lhs, 0, name=bus_id)

    def close_connector(self, connector, expr=0):
        """Specify the flow over the connector (default 0)."""
        if connector.name in self.connections:
            specification = self.connections[connector.name] - {connector}
            if len(specification) != 1:
                raise RuntimeError(
                    "It seems that you used the identifier "
                    f"'{connector.name}' both as a connector "
                    "name and as a bus_id... You should be "
                    "able to fix this by changing the bus_id "
                    "in the corresponding connect statement of "
                    f"{self}!"
                )
            spec = specification.pop()
            spec.expr = expr
        else:
            spec = Connector(self, f"{connector.name}_specification", expr)
            self.connect(connector.name, {connector, spec})
        self._update_connection_constraint(connector.name)

    def expose_connector(self, connector, alias=None):
        """Expose an existing connector to the outside of the system."""
        if connector.component not in self.components:
            raise RuntimeError(
                f"Tried to expose connector '{connector.name}' "
                f"of component '{connector.component}', which "
                f"is not part of the system '{self}'!"
            )
        id = alias if alias else connector.name
        if id in self.connectors:
            raise RuntimeError(
                f"Tried to expose connector '{connector.name}' "
                f"of component '{connector.component}', under "
                f"the name '{id}', which is already used. You "
                "should be able to fix this by using a "
                "different alias!"
            )
        self.connectors[id] = connector
        setattr(self, id, connector)

    def extend_connection(self, bus_id, alias=None):
        """Extend the connection to the outside of the system."""
        if bus_id not in self.connections:
            raise RuntimeError(f"Tried to extend nonexisting connection '{bus_id}'!")
        id = alias if alias else bus_id
        if id in self.connectors:
            raise RuntimeError(
                f"Tried to extend connection '{bus_id}' "
                f"of component {self}, as a connector with "
                f"the name '{id}', which is already used. You "
                "should be able to fix this by using a "
                "different alias!"
            )
        cu = ConnectorUnion(self, id, *self.connections.pop(bus_id))
        self._constraints_dict.pop(bus_id)  # remove the previous constraint
        self.connectors[id] = cu
        setattr(self, id, cu)
        # # TODO: blacklist variable names ending in '_extension'
        # varname = f'{bus_id}_extension'
        # v = self.operational_variables_dict.get(
        #     varname, self.make_operational_variable(f'{bus_id}_extension')
        # )
        # # internal connection with a dummy connector
        # c = Connector(self, f'{bus_id}_dummy', -v)
        # self.connect(bus_id, c)
        # # external connector exposing the connection
        # self.add_connectors(bus_id, v)

    def connect(self, bus_id, connectors):
        """Connect all elements of `connectors` to a bus with id `bus_id`."""
        connectors = set(connectors)  # ensure connectors is a set
        non_members = set(
            c for c in connectors if c.component not in {self}.union(self.components)
        )
        if non_members:
            # TODO: Possibly we can just add the component here:
            # self.add(component)
            msg = "\n\t- ".join(repr(c) for c in non_members)
            raise RuntimeError(
                "Attempted to connect the following connectors "
                f"which are not part of the system {self} or "
                f"any of its components:\n\t- {msg}"
            )
        if bus_id not in self.connections:
            self.connections[bus_id] = set()
        self.connections[bus_id].update(connectors)
        self._update_connection_constraint(bus_id)

    def detach(self, bus_id, connectors=None):
        """Detach all `Connector`s in `connectors` from the specified bus."""
        bus = self.connections[bus_id]
        if connectors is None:  # detach the entire bus
            del self.connections[bus_id]
            del self._constraints_dict[bus_id]
        else:
            invalid_connectors = set(c for c in connectors if c not in bus)
            if invalid_connectors:
                raise KeyError(
                    f"The connectors {invalid_connectors} are not part of bus {bus}!"
                )
            for connector in connectors:
                # TODO: What if the bus only has 1 connector left?
                bus.remove(connector)
            if len(bus) == 0:
                del self.connections[bus_id]
                del self._constraints_dict[bus_id]
            else:  # if there are some connectors left
                self._update_connection_constraint(bus_id)

    def add(self, component):
        """Add a `Component` to the system."""
        if not isinstance(component, Component):
            raise RuntimeError(
                f"Tried to add something that is not a Component to the system {self}"
            )
        if isinstance(component, System) and self in component.components:
            raise RuntimeError(
                f"Tried to add {component} to {self} which is "
                "already a component of the former!"
            )
        self._components.add(component)
        return component

    def remove(self, component):
        """Remove a `Component` from the system."""
        # Remove the eliminated component's connectors from all buses
        cc = set(component.connectors.values())
        for bus_id, bus in self.connections.items():
            if bus.intersection(cc):
                bus -= cc
                self._update_connection_constraint(bus_id)

    def get_open_connectors(self):
        """Return the set of all connectors that are not connected yet."""
        connectors = set()
        for com in self.components:
            for con in com.connectors.values():
                connectors.add(con)
                # if not con.bus:
                #     open_connectors.append(con)
        connected_connectors = set()
        for bus in self.connections.values():
            for con in bus:
                connected_connectors.add(con)
        return connectors - connected_connectors

    def aggregate_component_expressions(self, id, aggregator=sum):
        """Aggregate expressions from the components matching the identifier.

        The passed identifier is used to look up matching expressions in the
        components of this system. The resulting expressions are then
        aggregated using the passed aggregator function and the resulting
        expression is returned.
        """
        from comando import Zero

        return aggregator(c.get_expression(id, Zero) for c in self.components)

    def create_problem(
        self,
        design_objective=0,
        operational_objective=0,
        timesteps=None,
        scenarios=None,
        data=None,
        name=None,
    ):
        """Create a problem with the specified time and scenario structure.

        Arguments
        ---------
        T : The end time of the operational period (default 8760)
            If T is not specified, timesteps needs to be a mapping (see below).
        timesteps : tuple, Mapping or Series.
            If timesteps is tuple it is assumed to consist of timestep labels
            and data for the time horizon T. This data may be a scalar numeric
            value, a Mapping or a Series. In the latter two cases T maps from
            different scenarios s to corresponding time horizons T[s].
            If timesteps is a Mapping, it can either be mapping from timestep
            labels to timestep lengths or from scenarios to a corresponding
            specification of the time structure, consisting of either the tuple
            representation or the timestep mapping.
        scenarios : None or an iterable of timestep labels.
            If scenarios is a Mapping or pandas Series, the values are
            interpreted as the probabilities / relative likelihoods of the
            individual scenarios.
        """
        return Problem(
            design_objective,
            operational_objective,
            self.constraints_dict,
            self.states_dict,
            timesteps,
            scenarios,
            data,
            name,
        )


class DataProxy(SlotSerializationMixin):
    """A proxy object to access and set data."""

    from typing import Callable, Optional

    __slots__ = ("getter", "setter")

    def __init__(
        self,
        getter: "Callable(Optional[object])",
        setter: "Callable(str, [int, float])",
    ) -> None:
        self.getter = getter
        self.setter = setter

    def __getitem__(self, key) -> object:
        """Get items from the object returned from the getter."""
        return self.getter(key)

    def __setitem__(self, key, value) -> None:
        """Get items from the object returned from the getter."""
        self.setter(key, value)

    def __delitem__(self, key, value):
        """Raise AttributeError since deleting items is not possible."""
        raise AttributeError("can't delete item")

    def __getattr__(self, attr):
        """Defer all attribute access to the object returned by the getter."""
        try:
            return getattr(self.getter(), attr)
        except:
            raise AttributeError("no such attribute")

    def __eq__(self, other):
        """Explicitly defer eq comparison."""
        if isinstance(other, DataProxy):
            other = other.getter()
        return self.getter().__eq__(other)

    def __ne__(self, other):
        """Explicitly defer ne comparison."""
        return ~(self.__eq__(other))


class Problem:
    """A simple optimization problem."""

    def __init__(
        self,
        design_objective=0,
        operational_objective=0,
        constraints=None,
        states=None,
        timesteps=None,
        scenarios=None,
        data=None,
        name="Unnamed Problem",
    ):
        self.name = name
        self.design_objective = design_objective
        self.operational_objective = operational_objective
        # TODO: In contrast to Components we store variables, constraints and
        #       parameters as dicts and not as sets here.
        #       As this can be confusing to users we should probably change it!
        self.constraints = (
            {} if constraints is None else self._handle_duplicates(constraints)
        )
        self.states = {} if states is None else states

        self.parameters = set()
        self.design_variables = set()
        self.operational_variables = set()
        self._collect_symbols()
        self.Delta_t = Parameter(f"Delta_t_{self.name}")
        self._set_scenarios(scenarios)
        self._set_timesteps(timesteps)
        self._update_operational_index()

        self._initial_states = DataProxy(
            self._get_initial_states, self._set_initial_states
        )
        self._data = DataProxy(self._get_data, self._set_data)
        # Update parameter values with user given ones
        if data is not None:
            self.data = data

    def _collect_symbols(self):
        # NOTE: We could require the user to specify symbols as well, but
        #       not all of them will be always be relevant. We can just get all
        #       relevant symbols from the expressions for the objective
        #       contributions, constraints and states...
        #       Note that when manipulating the problem later on, care must be
        #       taken to add or remove symbols, e.g., deleting the only
        #       constraint with variable 'v', v will not be automatically
        #       removed as a variable.
        expressions = (
            self._do,
            self._oo,
            *self.constraints.values(),
            *(e for s, (_, ds, f) in self.states.items() for e in (s, ds, f)),
        )
        self.parameters = set()
        self.design_variables = set()
        self.operational_variables = set()
        self.add_symbols(set().union(*(e.free_symbols for e in expressions)))

    def add_symbols(self, syms):
        """Sort symbols into parameters, design- and operational variables."""
        from comando.utility import is_indexed, split

        bvs, bps = split(syms, lambda s: isinstance(s, Parameter))
        params = {p if p.parent is None else p.parent for p in bps}
        dvs, ovs = split(bvs, is_indexed)
        fake_dvs, real_dvs = split(dvs, lambda dv: dv.parent is None)
        ovs.update({fdv.parent for fdv in fake_dvs})
        self.parameters.update(params)
        self.design_variables.update(real_dvs)
        self.operational_variables.update(ovs)

    def _set_scenarios(self, scenarios):
        if scenarios is None:
            self._scenario_weights = None
        elif isinstance(scenarios, (Mapping, Series)):
            self._scenario_weights = Series(
                scenarios, Index(scenarios.keys(), name="s"), name="pi"
            )
        elif isinstance(scenarios, Iterable):
            self._scenario_weights = Series(
                1 / len(scenarios), Index(scenarios, name="s"), name="pi"
            )
        else:
            raise TypeError(
                "scenarios should be an iterable of "
                "scenario-labels, a mapping from "
                "scenario-labels to the associated "
                "probabilities or `None`!"
            )
        if scenarios:  # update initial states
            iv_updates = {}
            for state, (iv, *_) in self.states.items():
                if isinstance(iv, (Variable, VariableVector)):
                    # create  a variable vector
                    new_iv = VariableVector(iv.name, iv.domain, iv.bounds, iv.init_val)
                    new_iv.instantiate(scenarios)
                    iv_updates[state] = (new_iv, *_)
                elif isinstance(iv, Parameter):
                    if isinstance(iv.value, (int, float)):
                        iv.value = {s: iv.value for s in scenarios}
                    else:
                        iv.value = {s: float("nan") for s in scenarios}
                else:
                    msg = "Expected Variable or Parameter as initial state!"
                    raise NotImplementedError(msg)
            self.states.update(iv_updates)

    def _norm_timesteps(self, timesteps):
        """Normalize the time structure representation."""
        if isinstance(timesteps, (Mapping, Series)):
            index = Index(timesteps.keys(), name="t")
            return Series(timesteps, index, name="timesteps")
        elif isinstance(timesteps[0], Iterable):  # same length for all timesteps
            labels, T = timesteps
            index = Index(labels, name="t")
            return Series(T / len(labels), index, name="timesteps")
        else:
            raise ValueError(
                "timesteps should be an iterable of "
                "timestep-labels, a mapping from timestep-labels "
                "to the associated timestep-length, or `None`!"
            )

    def _set_timesteps(self, timesteps):
        scenarios = self.scenarios
        if scenarios is None:
            if timesteps is None:
                # TODO: We may relax this in the future, to allow for pure
                #       design problems!
                raise ValueError("Either timesteps or scenarios must be specified!")
            # e.g. timesteps = {'t1': 1, 't2': 4, ...} or (['t1', ...], 24)
            self._timesteps = self._norm_timesteps(timesteps)
            self._uniform_timesteps = True
        else:
            if timesteps is None:
                self._timesteps = timesteps
                self._uniform_timesteps = True
            elif isinstance(timesteps, (Mapping, Series)):
                try:  # to see whether timesteps is already a Multiindex Series
                    if len(timesteps.index.levels) == 2:
                        # looks like the user knows what they're doing!
                        timesteps.index.rename(["s", "t"], inplace=True)
                        timesteps.rename("timesteps", inplace=True)
                        self._timesteps = timesteps
                        # now we need to see whether timesteps are uniform
                        first = timesteps[next(iter(scenarios))]
                        for s in scenarios:
                            try:
                                if all(timesteps[s] == first):
                                    continue
                                break
                            except ValueError:
                                break
                        else:
                            self._uniform_timesteps = True
                            return
                        self._uniform_timesteps = False
                        return
                    else:
                        raise ValueError("Incorrect format of timesteps!")
                except AttributeError:
                    pass
                first_key = next(iter(timesteps.keys()))
                first_value = timesteps[first_key]
                if isinstance(first_value, (Mapping, Series, tuple)):
                    # e.g. timesteps = {'a': {'t1': 1, ...},
                    #                   'b': (['t1', ...], 5)}
                    data = {
                        (s, t): dti
                        for s in scenarios
                        for t, dti in self._norm_timesteps(timesteps[s]).items()
                    }
                    index = MultiIndex.from_tuples(data, names=["s", "t"])
                    self._timesteps = Series(data, index, name="timesteps")
                    self._uniform_timesteps = False
                else:  # e.g. timesteps = {'t1': 1, 't2': 4, ...}
                    timesteps = self._norm_timesteps(timesteps)
                    index = MultiIndex.from_product(
                        [scenarios, timesteps.keys()], names=["s", "t"]
                    )
                    self._timesteps = Series(
                        (dti for s in scenarios for ti, dti in timesteps.items()),
                        index,
                        name="timesteps",
                    )
                    self._uniform_timesteps = True
            else:  # timesteps = labels, T
                labels, T = timesteps
                index = MultiIndex.from_product([scenarios, labels], names=["s", "t"])
                if isinstance(T, (Mapping, Series)):  # scenario specific T
                    self._timesteps = Series(
                        (
                            dti
                            for s in scenarios
                            for dti in self._norm_timesteps([labels, T[s]])
                        ),
                        index,
                        name="timesteps",
                    )
                    self._uniform_timesteps = False
                # same T for all scenarios
                timesteps = self._norm_timesteps(timesteps)
                self._timesteps = Series(
                    (dts for s in scenarios for dts in timesteps),
                    index,
                    name="timesteps",
                )
                self._uniform_timesteps = True

    def _update_operational_index(self):
        """Update the index of operational symbols."""
        for p in self.parameters:
            if p.is_indexed:
                # TODO: Reusing old data may not be what users expect or want,
                #       Maybe it is better to force them to reset values.
                #       On the other hand, scalar default values may have been
                #       specified during Component modelling, so the best
                #       option is likely to store these defaults during problem
                #       initialization
                try:  # To re-use existing data, e.g., when extending timesteps
                    p.value = Series(p.value, self.index, float)
                except ValueError:  # Default to nan
                    p.value = Series(float("nan"), self.index, float)
        for ov in self.operational_variables:
            # TODO: This somehow causes VariableVector elements to be modified,
            #       even if the index stays the same!
            #       Oddly enough explicitly creating a variable in this loop
            #       stops this from happening, i.e. if ov contains variables
            #       named f'{ov.name}[1]' and f'{ov.name}[2]', adding the
            #       following line:
            # comando.Variable(f'{ov.name}[1]')
            #       will result in f'{ov.name}[1]' staying the same and
            #       f'{ov.name}[2]' being replaced by another object!
            ov.instantiate(self.index)
        self.Delta_t.value = self._timesteps

    def _handle_duplicates(self, constraints):
        rev_dict = {}
        for con_id, con in constraints.items():
            if con in rev_dict:
                print(
                    f"INFO: Identifiers {rev_dict[con]} and {con_id} map to "
                    "the same constraint! Keeping the former..."
                )
            else:
                rev_dict[con] = con_id
        return {con_id: constraints[con_id] for con_id in rev_dict.values()}

    def __iter__(self):
        """Prevent iteration that is implicitly introduced with __getitem__."""
        raise TypeError("Component object is not iterable")

    def __getitem__(self, identifier):
        """Get a Symbol or Expression matching the identifier."""
        for s in [self.parameters, self.design_variables, self.operational_variables]:
            # TODO: This seems unnecessarily costly!
            d = {e.name: e for e in s}
            if identifier in d:
                return d[identifier]
        raise KeyError(f"No entry for '{identifier}' found in {self}!")

    def __setitem__(self, identifier, value):
        """Set the value of a Parameter."""
        # Simple solution (requiring scalar or exactly matching dimension):
        # self.parameter_values[identifier] = value
        # return
        # if self.index is None:
        #     # TODO this shouldn't happen
        #     raise NotImplementedError('Setting values without having timesteps'
        #                               'specified has not been implemented yet')
        # TODO: unnecessarily costly if we only want to set Parameter values
        # item = self.parameters[identifier]
        item = self[identifier]

        if isinstance(value, Iterable):
            if item in self.design_variables:
                raise RuntimeError(
                    "Attempted to set value of design variable "
                    f"{item} with vector valued data!"
                )
            # TODO If the value's index changes here this will raise an error!
            index = self.index
            data = Series(item.value, index, float, identifier)
            len_i = len(self.index)
            scenarios = self.scenarios
            len_s = 0 if scenarios is None else len(scenarios)
            if isinstance(value, Mapping):
                for k in index:
                    try:  # Get just the necessary data from the Mapping
                        data[k] = value[k]
                    except KeyError:
                        pass  # Stick to the previous data
            elif len(value) == len_i:  # complete, ordered specification
                for k, v in zip(data.index, value):
                    data[k] = v
            # NOTE: From here on it is assumed that the index consist of
            #       scenario-time pairs and we interpret `value` as
            #       either time or scenario dependent
            elif self._uniform_timesteps:
                if scenarios is None:
                    len_t = len(self._timesteps)
                else:
                    len_t = len(self._timesteps[next(iter(scenarios))])
                if len(value) == len_t:  # time dependent
                    # NOTE: If the numbers of timesteps and scenarios are
                    #       identical we assume time-dependence!
                    for s in scenarios:
                        data[s] = value
                elif len(value) == len_s:  # scenario dependent
                    for i, s in enumerate(scenarios):
                        for t in self.timesteps[s].keys():
                            data[s, t] = value[i]
                else:
                    if len_t == len_s:
                        msg = (
                            f"{len_t} for time-dependent data, or {len_i} "
                            "for data depending on both scenario and time"
                        )
                    else:
                        msg = (
                            f"{len_t} for time-dependent data, {len_s} for "
                            f"scenario-dependent data or {len_i} for "
                            "data depending on both scenario and time"
                        )
                    raise ValueError(
                        "Value must be a scalar, a Mapping or an "
                        "Iterable with appropriate length "
                        f"({msg})!"
                    )
            item.value = data
        else:  # Value is a scalar, store it as such!
            item.value = value
        return

    def __repr__(self):
        return f"Problem(name={self.name!r})"

    @property
    def index(self):
        """Get the index of the Problem."""
        return (
            self._scenario_weights.index
            if self._timesteps is None
            else self._timesteps.index
        )

    @property
    def T(self):
        """Get the Problem's end time."""
        if self._scenario_weights is None:
            return sum(self._timesteps)
        return self._timesteps.groupby(level=0).sum().rename("T")

    @T.setter
    def T(self, T):
        """Set the Problem's end time.

        T : number, Mapping or Series
            The length of the time horizon.
        """
        if self._scenario_weights is None:
            try:
                T = float(T)
            except TypeError:
                raise ValueError("T must be a number!")
            old_T = self.T
            if old_T == 0:  # uniform timesteps
                self._timesteps = self._norm_timesteps((self._timesteps.index, T))
            else:  # Rescale timesteps
                self._timesteps *= T / old_T
        else:  # self._scenario_weights is not None
            if isinstance(T, (Mapping, Series)):
                for s, old_Ti in self.T.items():
                    Ti = T[s]
                    try:
                        Ti = float(Ti)
                    except TypeError:
                        raise ValueError("T must contain numbers!")
                    if old_Ti == 0:  # uniform timesteps
                        self._timesteps[s][:] = self._norm_timesteps(
                            (self._timesteps.index, Ti)
                        )
                    else:  # Rescale timesteps
                        self._timesteps[s][:] *= Ti / old_Ti
            else:
                try:
                    T = float(T)
                except TypeError:
                    raise ValueError("T must be a number, Mapping or Series!")
                for s, old_Ti in self.T.items():
                    if old_Ti == 0:  # uniform timesteps
                        self._timesteps[s][:] = self._norm_timesteps(
                            (self._timesteps.index, T)
                        )
                    else:  # Rescale timesteps
                        self._timesteps[s][:] *= T / old_Ti

    @property
    def timesteps(self):
        """Get the length of the Problem's timesteps."""
        return None if self._timesteps is None else self._timesteps.copy()

    @timesteps.setter
    def timesteps(self, timesteps):
        """Update the Problem's timesteps.

        Arguments
        ---------
        timesteps : None or an iterable of timestep labels.
            If timesteps is a Mapping or pandas Series, the values are
            interpreted as the lengths of the individual timesteps and T is
            taken to be their sum.
        T : The end time of the operational period (default 8760)
            If T is not specified, timesteps needs to be a mapping.
        """
        self._set_timesteps(timesteps)
        self._update_operational_index()

    @property
    def scenarios(self):
        """Get the Problem's scenarios."""
        return (
            None
            if self._scenario_weights is None
            else tuple(self._scenario_weights.keys())
        )

    @scenarios.setter
    def scenarios(self, scenarios, timesteps=None):
        """Update the Problem's scenarios.

        scenarios : None or an iterable of timestep labels.
            If scenarios is a Mapping or pandas Series, the values are
            interpreted as the probabilities / relative likelyhoods of the
            individual scenarios.
        """
        if timesteps is None:
            if self._uniform_timesteps:
                if self._scenario_weights is None:
                    timesteps = self.timesteps
                else:
                    s, timesteps = next(iter(self.timesteps.groupby("s")))
                    timesteps = timesteps[s]
            else:
                raise ValueError(
                    "Tried to update scenarios for a problem "
                    "without uniform timesteps.\nYou need to "
                    "either make timesteps uniform first or "
                    "specify scenario-specific timesteps."
                )
        self._set_scenarios(scenarios)
        self._set_timesteps(timesteps)
        self._update_operational_index()

    @property
    def scenario_weights(self):
        """Get the Problem's scenario weights."""
        return None if self._scenario_weights is None else self._scenario_weights.copy()

    @scenario_weights.setter
    def scenario_weights(self, weights):
        """Update the Problem's scenario weights."""
        if {*self._scenario_weights.keys()} == {weights.keys()}:
            self._scenario_weights.update(weights)

    @property
    def design_objective(self):
        return self._do

    @design_objective.setter
    def design_objective(self, do):
        from comando import sympify

        self._do = sympify(do)

    @property
    def operational_objective(self):
        return self._oo

    @operational_objective.setter
    def operational_objective(self, oo):
        from comando import sympify

        self._oo = sympify(oo)

    def weighted_sum(self, op_expr, symbolic=True):
        """Compute the scenario- and/or time-weighted sum of an expression.

        Arguments
        ---------
        op_expr : Expression
            an operational expression that is to be weighted
        symbolic : bool
            if True creates a new expression (default) if False evaluate
            numerically
        """
        if symbolic:
            # from comando.utility import _idx_parse
            # sym_map = {sym: sym for sym in op_expr.free_symbols}
            # op_map = comando.op_map

            def func(idx):
                # return _idx_parse(op_expr, sym_map, op_map, idx, float)
                sym_map = {
                    sym: sym[idx] for sym in op_expr.free_symbols if sym.is_indexed
                }
                return op_expr.subs(sym_map)

        else:
            from comando.utility import evaluate

            vals = evaluate(op_expr)

            def func(idx):
                return vals[idx]

        if self._timesteps is None:
            return sum(p * func(s) for s, p in self._scenario_weights.items())
        if self._scenario_weights is None:
            return sum(dti * func(t) for t, dti in self._timesteps.items())
        return sum(
            p * dti * func((s, t))
            for s, p in self._scenario_weights.items()
            for t, dti in self._timesteps[s].items()
        )

    @property
    def objective(self):
        """Get the objective expression of the problem."""
        return self._do + self.weighted_sum(self._oo)

    @property
    def num_vars(self):
        """Get the total number of variables."""
        return len(self.design_variables) + len(self.index) * len(
            self.operational_variables
        )

    @property
    def num_cons(self):
        """Get the total number of variables."""
        dcons, ocons = split(self.constraints, is_indexed)
        return len(dcons) + len(self.index) * (len(ocons) + len(self.states))

    @property
    def initial_states(self):
        """Aggregate and return the parameter data."""
        return self._initial_states

    def _get_initial_states(self, key=None):
        """Get an overview over initial state types and values."""
        if key is None:
            if self.scenarios:
                initial_states = DataFrame(index=self.scenarios, dtype=object)
            else:
                initial_states = Series(dtype=object)

            def rep(iv):
                if isinstance(iv, Parameter):
                    return iv.value
                if isinstance(iv, (Variable, VariableVector)):
                    return f"{iv.lb} ≤ {iv.value} ≤ {iv.ub}"
                raise TypeError(
                    "Initial Values should be of type Parameter or Variable!"
                )

            for state, (iv, *_) in self.states.items():
                if iv.is_indexed:
                    initial_states[state.name] = iv.expansion.apply(rep)
                else:
                    if self.scenarios:
                        initial_states[state.name] = [rep(iv)] * len(self.scenarios)
                    else:
                        initial_states[state.name] = rep(iv)
            return initial_states.fillna("\U0001f504")
        else:
            for state, (iv, *_) in self.states.items():
                if state.name == key:
                    return iv
            else:
                raise KeyError(f"No initial value with the name '{key}'!")

    def _set_initial_states(self, state_name, value):
        """Provide values for a particular initial state of the problem."""
        for state in self.states:
            if state.name == state_name:
                break
        else:
            raise KeyError(f"No state named {state_name} in problem!")
        i_state, *other = self.states[state]

        # numerical value or cyclic (= nan) initial condition
        if isinstance(value, (str, int, float)):
            value = float(value)
            if value != value and isinstance(
                i_state, (Variable, VariableVector)
            ):  # Need to change to Parameter
                new_i_state = Parameter(i_state.name)
                self.states[state] = new_i_state, *other
            else:
                i_state.value = value
        else:
            _value = i_state.value
            try:
                i_state.value = (
                    Series(value, self.scenarios, float, i_state.name)
                    if self.scenarios
                    else value
                )
            except ValueError:
                i_state.value = _value
                raise ValueError("Value does not match problem index!")

    @property
    def data(self):
        """Aggregate and return the parameter data."""
        return self._data

    def _get_data(self, key=None):
        if key is None:
            data = DataFrame(index=self.index)
            for par in self.parameters:
                try:
                    data[par.name] = par.value.values
                except AttributeError:
                    data[par.name] = par.value
            return data
        else:
            return self[key].value

    def _set_data(self, p_name, value):
        """Provide values for a particular parameter of the problem."""
        p = {p.name: p for p in self.parameters}[p_name]
        _value = p.value
        try:
            p.value = value
            Problem._get_data(self)
        except ValueError:
            p.value = _value
            raise ValueError("Value does not match problem index!")

    @data.setter
    def data(self, data):
        """Provide values for multiple parameters of the problem."""
        for par in self.parameters:
            try:
                entry = data[par.name]
            except KeyError:
                if par.value is None:
                    print(f"WARNING: No data for parameter '{par}'!")
                else:
                    print(f"INFO: Using default data for parameter '{par}'!")
                continue
            try:  # To determine whether entry is a mapping...
                # NOTE: We're not using values her since it is an attribute for
                #       normal Mappings but a property for pandas Series and
                #       DataFrames!
                values = [v for k, v in entry.items()]
                # ...with identical values (then use scalar) or different ones
                if len({*values}) == 1:
                    par.value = values[0]
                else:
                    index = self.index
                    scenarios = self.scenario_weights.index
                    try:
                        timesteps = self._timesteps[next(iter(scenarios))]
                    except TypeError:
                        timesteps = None
                    if len(values) == len(index):
                        par.value = Series(values, index, float, par.name)
                    elif len(values) == len(scenarios):
                        par.value = Series(values, scenarios, float, par.name)
                    elif self._uniform_timesteps and len(values) == len(timesteps):
                        par.value = Series(values, timesteps, float, par.name)
                    else:
                        raise ValueError(
                            f"Data for Parameter {par.name} does "
                            "not match length of Problem index, "
                            "timesteps or scenarios!"
                        )
            except AttributeError:  # Nope, it's a scalar
                par.value = entry

    @property
    def design(self):
        """Collect the design variable values in a DataFrame."""
        dv = self.design_variables
        index = Index((v.name for v in dv), name="name")
        dv_data = Series(index=index, dtype=float, name="value")
        for v in dv:
            dv_data[v.name] = v.value
        return DataFrame(dv_data).sort_index()

    @design.setter
    def design(self, data):
        """Set the values of the design variables with the given data."""
        for var in self.design_variables:
            try:
                var.value = data[var.name]
            except KeyError:
                print(f"WARNING: No data for variable '{var}'!")

    @property
    def operation(self):
        """Collect the operational variable values in a DataFrame."""
        ov_data = DataFrame()
        for v in self.operational_variables:
            ov_data[v.name] = v.value
        res = ov_data.T.sort_index()
        res.index.rename("name", inplace=True)
        return res

    @operation.setter
    def operation(self, data):
        """Set the values of the operational variables with the given data."""
        for var in self.operational_variables:
            try:
                var.value = data.loc[var.name]
            except KeyError:
                print(f"WARNING: No data for variable '{var}'!")

    def store_variable_values(self, filename):
        """Serialize current variable values and store in file."""
        import os
        import pickle

        if os.path.isfile(filename):
            while True:
                overwrite = input("File already exists. Overwrite? [y/n]\n")
                if overwrite.lower() in ("y", "yes"):
                    break
                if overwrite.lower() in ("n", "no"):
                    return
        with open(filename, "wb") as file:
            pickle.dump(
                (self.design, self.operation), file, protocol=pickle.HIGHEST_PROTOCOL
            )

    def load_variable_values(self, filename):
        """Collect variable values from file."""
        import pickle

        with open(filename, "rb") as file:
            dv, ov = pickle.load(file)
        self.design = dv
        self.operation = ov

    def get_constraint_violations(self, larger_than=0):
        """Collect the current constraint violations in a DataFrame."""
        from comando.utility import evaluate

        res = Series(dtype=float, name="violation")
        for con_id, con in self.constraints.items():
            try:  # works for inequalities
                viol = evaluate(con.lts - con.gts)
            except AttributeError:
                viol = abs(evaluate(con.lhs - con.rhs))
            try:  # works for indexed constraints
                for i in viol.index:
                    res[f"{con_id}[{i}]"] = viol[i]
            except AttributeError:
                res[con_id] = viol
        return res.sort_index()[res >= larger_than]

    def subs(self, sym=None, rep=None, **reps):
        """Substitute an individual or multiple symbols in the problem."""
        from comando import Eq, linsolve

        if reps:  # keys are symbol identifiers
            reps = {self[sym]: rep for sym, rep in reps.items()}
        elif sym is not None and rep is not None:  # single substitution
            if not isinstance(sym, Symbol):  # sym may be an identifier
                sym = self[sym]
            reps = {sym: rep}
        elif isinstance(sym, Mapping):  # keys may be identifiers or symbols
            reps = sym
            reps = {
                self[sym] if not isinstance(sym, Symbol) else sym: rep
                for sym, rep in reps.items()
            }
        else:
            raise RuntimeError(
                "Either provide a Mapping, a single symbol and "
                "replacement via separate arguments or a list "
                "of replacements via keyword arguments!"
            )

        do = self._do.subs(reps)
        oo = self._oo.subs(reps)
        cons = self._handle_duplicates(
            {c_id: con.subs(reps) for c_id, con in self.constraints.items()}
        )
        states = {}
        aux_cons = {}
        for state, (init_state, der, roc) in self.states.items():
            state_rep = state.subs(reps)
            new_state = state_rep.free_symbols.pop()  # TODO: Assumes a single symbol
            if init_state in reps:
                new_init_state_rep = reps[init_state]
            else:
                new_init_state_rep = linsolve(  # TODO: Assumes linear reps
                    [state_rep - init_state], [new_state]
                )[0]
            if isinstance(new_init_state_rep, Symbol):
                new_init_state = new_init_state_rep
            else:
                index = get_index(new_init_state_rep)
                if any(
                    isinstance(sym, (Variable, VariableVector))
                    for sym in new_init_state_rep.free_symbols
                ):
                    if index is None:
                        new_init_state = Variable(
                            init_state.name + "__aux",
                            REAL,
                            bounds(new_init_state_rep),
                            evaluate(new_init_state_rep),
                        )
                    else:  # One inital state per scenario
                        lb, ub = bounds(new_init_state_rep)
                        new_init_state = VariableVector(
                            init_state.name + "__aux",
                            REAL,
                            (lb.min(), ub.max()),
                        )
                        new_init_state.instantiate(index)
                        new_init_state.bounds = lb, ub
                        new_init_state.value = evaluate(new_init_state_rep)
                else:
                    new_init_state = Parameter(
                        init_state.name + "__aux",
                        evaluate(new_init_state_rep),
                    )

            # The new derivative must be of the form pdiff * der
            pdiff = state_rep.diff(new_state)
            der_rep = (pdiff * der).subs(reps)
            if isinstance(der_rep, VariableVector):
                der_aux = der_rep
            else:
                lb, ub = bounds(der_rep)
                # We create an auxiliary variable that represents the
                # scaled derivative expression...
                der_aux = VariableVector(
                    der.name + "__aux",
                    der.domain,
                    (lb.min(), ub.max()),
                    # TODO: There are cases where we can do better than using a defailt init_val
                )
                der_aux.instantiate(der.expansion.index)
                der_aux.bounds = lb, ub
                der_aux.value = evaluate(der_rep)
                # ... and add a new constraint ensuring equality
                aux_cons[der_aux.name] = Eq(der_aux, der_rep)

            # the same holds for the new rate-of-change expression
            roc_rep = (pdiff * roc).subs(reps)
            # We can nor assemble the new state representation
            states[new_state] = (new_init_state, der_aux, roc_rep)

        # If we got here all went well, so we can update the symbol sets
        self._do = do
        self._oo = oo
        self.constraints = {**cons, **aux_cons}
        self.states = states
        self._collect_symbols()
