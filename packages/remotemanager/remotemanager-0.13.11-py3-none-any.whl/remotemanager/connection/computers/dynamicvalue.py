"""
DynamicValue stub class allows for deferred calculation of values.

Constructing a "tree" of values using these objects allows for later
assessment. Used in Computers for dynamic resource assignment.

>>> val_a = DynamicValue(10)
>>> val_b = DynamicValue(6)
>>> val_c = DynamicValue(val_a + val_b)
>>> val_c.value
16
"""

import logging
import math
from numbers import Number
from typing import Union, Any

from remotemanager.connection.computers.utils import format_time, try_value
from remotemanager.utils import ensure_list

logger = logging.getLogger(__name__)

EMPTY_TREATMENT_STYLES = [
    "line",  # default, removes the whole line
    "local",  # locally removes the value, ignoring the line
    "ignore",  # do nothing, performing no replacement
]

INVALID_EMPTY_TREATMENT = "empty_treatment must be one of the available styles: {style}"


class ChainingMixin:
    """Adds chaining ability for DynamicMixin and DynamicValue"""

    __slots__ = []

    @property
    def shortform_op(self) -> Union[str, None]:
        """
        Returns the operator in a readable form for calc insertion

        eg +, -, * instead of add, sub, mul, etc.
        """
        op = getattr(self, "op", None)
        ops = {
            "pow": "**",
            "div": "/",
            "mul": "*",
            "add": "+",
            "sub": "-",
            "eq": "==",
            "ne": "!=",
            "le": "<=",
            "lt": "<",
            "ge": ">=",
            "gt": ">",
            "get": "get",
        }
        return ops.get(op, None)

    def __pow__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "pow")

    def __mul__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "mul")

    def __truediv__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "div")

    def __add__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "add")

    def __sub__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "sub")

    def __eq__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "eq")

    def __ne__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "ne")

    def __le__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "le")

    def __lt__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "lt")

    def __ge__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "ge")

    def __gt__(self, other: Any) -> "DynamicValue":  # noqa: F821
        return self._chain_operation(other, "gt")

    def __getitem__(self, item):
        return self._chain_operation(item, "get")

    def __bool__(self):
        return bool(self.value)

    def _chain_operation(self, other, operation) -> NotImplemented:
        return NotImplemented

    @property
    def value(self) -> NotImplemented:
        return NotImplemented


class DynamicMixin(ChainingMixin):
    """
    Provides functions to enable Entities using DynamicValue to chain properly

    .. important::
        The DynamicValue in question must be directly available at `_value`

    Args:
        assignment (str):
            The variable to which this object is assigned, for introspection
        default (Any, None):
            Default value, marks this Resource as optional if present
        value (Any, None):
            Sets the value directly. You should ideally set the default, as this is easy
            to override and break
        optional (bool):
            Marks this resource as Optional. Required as there are actually
            three states:
                - Required input, required by scheduler.
                - Optional input, required by scheduler.
                - Optional input, optional by scheduler.
        requires (str, list):
            Stores the name(s) of another variable which is required alongside this one
        replaces (str, list):
            Stores the name(s) of another variable which is replaced by this one
        hidden (bool):
            The value will be present, but requests to not be displayed
        min (int):
            Minimum value for numeric inputs
        max (int):
            Maximum value for numeric inputs
        format (str):
            Expected format for number. Allows None, "time" or "float"
        empty_treatment (bool):
            Dictates how an empty value is treated. Possible options are:
            - line
                default, removes the whole line
            - local
                locally removes the output
            - ignore
                does nothing, leaves the output unchanged
        static (bool):
            Does not chain with other values if True
    """

    __slots__ = [
        "_name",
        "_optional",
        "_requires",
        "_replaces",
        "hidden",
        "_min",
        "_max",
        "_value",
        "format",
        "_empty_treatment",
        "static",
        "processed",
    ]

    def __init__(
        self,
        assignment: Union[str, None] = None,
        default: Union[Any, None] = None,
        value: Union[Any, None] = None,
        optional: bool = True,
        requires: Union[str, list, None] = None,
        replaces: Union[str, list, None] = None,
        hidden: bool = False,
        min: Union[int, None] = None,
        max: Union[int, None] = None,
        format: Union[str, None] = None,
        empty_treatment: str = "line",
        static: bool = False,
    ):
        self._name = assignment

        if optional in ["False", "false"]:
            optional = False
        elif optional == ["True", "true"]:
            optional = True
        self._optional = optional

        self._requires = ensure_list(requires, semantic=True)
        self._replaces = ensure_list(replaces, semantic=True)

        self.hidden = hidden

        self._min = min
        self._max = max

        self.format = format

        self._empty_treatment = None
        self.empty_treatment = empty_treatment

        self.static = static

        if isinstance(default, DynamicMixin):
            # assigning a default directly to a Resource or Substitution object causes
            # that object to be added, instead of a DynamicValue
            default = default._value

        if isinstance(value, DynamicMixin):
            value = value._value

        default = entry_format(default, format)
        value = entry_format(value, format)

        self._value = DynamicValue(
            a=value, b=None, op=None, default=default, assignment=assignment
        )

    def _chain_operation(self, other: Any, operation: str) -> "DynamicValue":
        try:
            other = other._value
        except AttributeError:
            pass
        obj = DynamicValue(self._value, other, operation)
        return obj

    @property
    def name(self) -> str:
        """Returns the name under which this resource is stored"""
        return self._name

    @property
    def min(self) -> Union[int, None]:
        """Minimal numeric value"""
        if self._min is not None:
            return int(self._min)
        return self._min

    @property
    def max(self) -> Union[int, None]:
        """Maximal numeric value"""
        if self._max is not None:
            return int(self._max)
        return self._max

    @property
    def default(self):
        """Returns the default, if available"""
        return self._format_value(self._value.default)

    @default.setter
    def default(self, default):
        self._value.default = default

    @property
    def _default(self):
        """Returns the "raw" default"""
        return self._value.default

    @property
    def optional(self):
        """Returns True if this Resource is optional at Dataset level"""
        return self._value.default is not None or self._optional

    @property
    def replaces(self) -> list:
        """
        List of arguments whom are no longer considered `required` if this
        resource is specified
        """
        return self._replaces

    @property
    def requires(self) -> list:
        """
        List of requirements if this resource is specified.
        e.g. nodes for mpi_per_node
        """
        return self._requires

    @property
    def empty_treatment(self):
        """
        Dictates how this parameter is treated if it is empty.

        Possible behaviours:

        ``line``:
            This is the default, and deletes the whole line. Useful when
            parameterising resource requests such as

            ``#SBATCH nodes=#nodes#``

        ``local``:
            Locally deletes the value, leaving the remainder of the line.
            Note that this does not delete anything _outside_ of the extents of the
            parameter. For example:

            ``#SBATCH nodes=#NODES:empty_treatment=local#`` -> ``#SBATCH nodes=``

            Useful when arguments may follow one another:

            ``#a:empty_treatment=local# #b:empty_treatment=local#``

            In this case, a missing ``a`` or ``b`` will not delete the other
        ``ignore``:
            Disables any treatment, values will be left as is:

            ``#a=#a:empty_treatment=local#`` -> ``#a=#a:empty_treatment=local#``
        """
        return self._empty_treatment

    @empty_treatment.setter
    def empty_treatment(self, style: str):
        if style.lower() not in EMPTY_TREATMENT_STYLES:
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=style))
        self._empty_treatment = style.lower()

    def _format_value(self, val):
        try:
            val = val.value
        except AttributeError:
            pass

        if val is None:
            return None
        if isinstance(val, bool):
            return val

        try:
            if self.format == "float":
                return float(val)
            if self.format == "time":
                return format_time(val)
        except ValueError:
            pass

        # no hard formatting, apply default ceil()
        if isinstance(val, (int, float)):
            val = int(math.ceil(float(val)))

        return val

    @property
    def value(self):
        """Attempt to safely return the value (default) from self"""
        if self.default is not None and self._value is None:
            val = self.default
        else:
            val = self._value

        try:
            val = val.value
        except AttributeError:
            pass

        val = self._format_value(val)

        self._validate(val)

        return val

    @value.setter
    def value(self, value):
        self.set_value(value)

    @property
    def temporary_value(self):
        return self._value.temporary_value

    @temporary_value.setter
    def temporary_value(self, value):
        self._value.temporary_value = value

    def reset_temporary_value(self):
        """Reset the temporary value back to None"""
        self.temporary_value = None

    @property
    def linked(self) -> bool:
        """Returns True if this Value has been linked by Script"""
        return self.temporary_value is not None

    def set_value(self, value):
        """
        Sets the value, separating out the function allows for property overloading

        Since this function handles value setting for both Resource/Substitution
        AND the DynamicValues within, we have some extra edge cases to catch

        case 1
            We have a resource, and are setting the value
            to a static int
        case 2
            We have a resource and are setting the value
            to directly mirror another resource
        case 3
            We have a resource and are setting the value
            to be a combination of other resources (DV)
        """
        self._validate(value)

        if isinstance(self._value, DynamicValue):
            # we're setting on an Argument _value
            if isinstance(value, DynamicValue):
                # if _value has any extra properties,
                # need to be careful not to drop them
                self._value._a = value._a
                self._value._b = value._b
                self._value._op = value._op
            else:
                self._value.value = value
            return

        if isinstance(value, DynamicValue):
            self._value = value
        else:
            self._value = DynamicValue(value)

    @property
    def has_value(self) -> bool:
        return self.value is not None

    def _validate(self, value) -> None:
        """
        Validates `value`. Raises exception if invalid
        """
        try:
            value = value.value
        except AttributeError:
            pass

        try:
            value / 1
            isnumeric = True
        except TypeError:
            isnumeric = False

        if isnumeric:
            name = getattr(self, "name", None)
            nameinsert = ""
            if name is not None:
                nameinsert = f" for {name}"
            if self.min is not None and value < self.min:
                raise ValueError(
                    f"{value}{nameinsert} is less than minimum value {self.min}"
                )
            if self.max is not None and value > self.max:
                raise ValueError(
                    f"{value}{nameinsert} is more than maximum value {self.max}"
                )

    @property
    def reduced(self):
        return self._value.reduced

    def pack(self, collect_value: bool = True):
        """
        Packs this Dynamic object down to a dictionary for storage

        Args:
            collect_value:
                Also collects the stored value if True
        """
        self.reset_temporary_value()
        data = {}

        def get_reduction(attr: str):
            """Attempts to get the reduced form of a value, returning None otherwise"""
            val = getattr(self, attr, None)
            if val is not None:
                try:
                    val = val.reduced
                    # remove redundant outer brackets
                    if val.startswith("(") and val.endswith(")"):
                        val = val[1:-1]
                except AttributeError:
                    # if the value is a string, it should be stored quoted
                    return treat_for_storage(val)

            return val

        default = get_reduction("_default")
        if default is not None:
            data["default"] = default

        if collect_value:
            value = self._value
            if isinstance(value, DynamicValue):
                if value.reduced == value.assignment:
                    # values can self-refer,
                    # returning the assignment instead of the value
                    value = treat_for_storage(value._a)
                else:
                    value = value.reduced
                    if value.startswith("(") and value.endswith(")"):
                        value = value[1:-1]
            if try_value(value) is not None and try_value(value) != try_value(default):
                data["value"] = value

        if not self.optional:
            data["optional"] = False
        if len(self.requires) != 0:
            data["requires"] = self.requires
        if len(self.replaces) != 0:
            data["replaces"] = self.replaces
        if self.min is not None:
            data["min"] = self.min
        if self.max is not None:
            data["max"] = self.max
        if self.format is not None:
            data["format"] = self.format

        return data


class DynamicValue(ChainingMixin):
    """
    Args:
        a:
            "First" number in operation
        b:
            "Second" number in operation. Can be None,
            in which case this value is considered "toplevel"
        op:
            Operation to use. Can be None for toplevel values
        default:
            Default value can be set in case the primary value is
            set to None
    """

    __slots__ = ["_a", "_b", "_op", "_default", "_assignment", "temporary_value"]

    def __init__(
        self,
        a: Union[Number, "DynamicValue", None],
        b: Union[Number, "DynamicValue", None] = None,
        op: Union[str, None] = None,
        default: Union[Number, "DynamicValue", None] = None,
        assignment: Union[str, None] = None,
    ):
        if try_value(a) == "":
            a = None
        if try_value(b) == "":
            b = None
        if op == "":
            op = None
        if b is None and op is not None:
            raise ValueError("Operator specified without 2nd value")
        if b is not None and op is None:
            raise ValueError("Cannot specify 2nd value without operator")

        self._a = a
        self._b = b
        self._op = op
        self._default = default
        self.temporary_value = None

        self._assignment = assignment

    def _chain_operation(self, other: Union[Any], operation: str):
        obj = DynamicValue(self, other, operation)
        return obj

    def __repr__(self):
        op = self.shortform_op
        if op is None:
            return str(self._a)
        return f"DynamicValue({self._a}{op}{self._b})"

    @property
    def a(self):
        """
        Returns:
            Value of "first" number
        """
        try:
            val = self._a.value
        except (ValueError, AttributeError):
            val = self._a
        return val

    @property
    def b(self):
        """
        Returns:
            Value of "second" number
        """
        try:
            val = self._b.value
        except (ValueError, AttributeError):
            val = self._b
        return val

    @property
    def op(self):
        """
        Returns:
            Operation string
        """
        return self._op

    @property
    def default(self):
        """
        Returns:
            The default value
        """
        return self._default

    @default.setter
    def default(self, default):
        """default setter"""
        self._default = default

    @property
    def assignment(self) -> Union[str, None]:
        """The variable at which this value is assigned, if available"""
        return self._assignment

    @property
    def static(self) -> bool:
        """Returns True if this Dynamic variable is static, rather than dynamic"""
        return self.op is None and self.a is not None

    @property
    def value(self):
        """
        Calculates value by calling the whole chain of numbers

        Returns:
            Value
        """
        logger.debug("evaluating %s", self.assignment)
        if self.temporary_value is not None:
            val = self.temporary_value
            logger.debug("\treturning temporary value: %s", val)
            return val

        if self.static:
            val = self.a
            logger.debug("\tstatic, returning self.a %s", val)
            return val

        if self.b is None:
            try:
                default = self.default.value
            except AttributeError:
                default = self.default
            logger.debug("\tself.b is None, returning default: %s", default)
            return default
        a = self.a
        b = self.b

        logger.debug("\tproceeding with a=%s, b=%s, op=%s", a, b, self.op)

        if isinstance(a, str) or isinstance(b, str):
            if self.op == "add":
                a = str(a)
                b = str(b)

        try:
            if self.op == "eq":
                return a == b
            if self.op == "ne":
                return a != b
            if self.op == "ge":
                return a >= b
            if self.op == "gt":
                return a > b
            if self.op == "le":
                return a <= b
            if self.op == "lt":
                return a < b
            if self.op == "add":
                return a + b
            if self.op == "sub":
                return a - b
            if self.op == "div":
                return a / b
            if self.op == "mul":
                return a * b
            if self.op == "pow":
                return a**b
            if self.op == "get":
                return a[b]
        except TypeError:
            return None

    @value.setter
    def value(self, val):
        """
        It is possible to update the value of a toplevel DynamicValue

        Args:
            val:
                New Value
        """
        if self._b is not None:
            name = self.assignment or "val"
            print(f"WARNING! Dynamic chain broken when assigning {name}={val}")
            self._b = None
            self._op = None
        self._a = val

    @property
    def reduced(self) -> str:
        """
        Returns the string form "reduced" version of this DynamicValue.

        In theory this should be storable as text within a database, without losing
        dependency information

        Extracts details from the assignment, if provided. Else returns the value.

        e.g.
        .. code:: python
            a = Resource(name="a")
            b = Resource(name="b")
            c = Resource(name="c")

            c = a + b

            c.reduce
            > "(a + b)"
        """

        def chain_reduction(obj):
            """Tries to "chain" the reduction to any other reducible objects"""
            try:
                return obj.reduced
            except AttributeError:
                # if we're at the end of the chain,
                # preferably return the assignment
                return get_assignment(obj)

        def get_assignment(obj):
            """
            Preferably returns the assignment property,
            otherwise returning the string form of obj
            """
            assign = getattr(obj, "assignment", None)
            if assign is None:
                return treat_for_storage(obj)
            return assign

        op = self.shortform_op

        if op is None:
            return get_assignment(self)

        a = chain_reduction(self._a)
        if self._b is None:
            return a

        b = chain_reduction(self._b)
        return f"({a} {op} {b})"


def treat_for_storage(var: Any) -> str:
    """
    Ensures that var is stored properly

    Strings must be quoted, but _not_ those that are
    actually ints
    """
    if var is None:
        return None
    if isinstance(var, str):
        try:
            tmp = str(int(var))
            # make sure we don't cast any floats to int
            if "." in tmp:
                return str(float(var))
            return tmp
        except (TypeError, ValueError):
            return f'"{var}"'
    return var


def concat_basic(
    a: Union[int, "DynamicValue", "Resource", "Substitution"],  # noqa: F821
    b: Union[int, "DynamicValue", "Resource", "Substitution"],  # noqa: F821
) -> "DynamicValue":
    """
    Concat two values a and b

    Required in the case where we want to add a value to a string

    Since str + Resource will call the __add__ method of the str object,
    we get a TypeError

    We need to sidestep this by adding the string to the _value_,
    then reversing the value.

    Doing it this way calls the corrent DynamicMixin.__add__(...) function,
    rather than str.__add__(...)

    ..note::
        This function will at least _try_ to return a+b beforehand

    Args:
        a: first value
        b: second value

    Returns:
        a+b
    """
    logger.debug(
        "Attempting to concat a=%s (type %s), b=%s (type %s)", a, type(a), b, type(b)
    )
    if try_value(a) == "":
        return b
    if try_value(b) == "":
        return a

    try:
        # works only if a is a DynamicMixin instance
        return a + b
    except TypeError:
        # create the sum in reverse then swap _a and _b
        tmp = b + a

        b_store = tmp._b
        tmp._b = tmp._a
        tmp._a = b_store

        return tmp


def entry_format(val, format: Union[str, None] = None):
    if val is None:
        return None

    if isinstance(val, DynamicValue):
        return val

    if isinstance(val, bool):
        return val

    if format == "time":
        try:
            return int(val)
        except (TypeError, ValueError):
            return val.strip('"')

    try:
        val = float(val)

        if val % 1 == 0:
            return int(val)
        return val

    except ValueError:  # non numeric
        return val
