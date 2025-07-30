"""
This module stores the placeholder arguments who's job it is to convert
arguments from the Dataset level `mpi`,  `omp`, `nodes`, etc. to what the
scheduler is expecting within a jobscript.

.. note::
    Placeholders without a `value` are "falsy". So checking their value in an
    if statement will return `True` if they have a value, `False` otherwise.
"""

import logging
from typing import Union

from remotemanager.connection.computers.dynamicvalue import DynamicMixin

logger = logging.getLogger(__name__)


class Resource(DynamicMixin):
    """
    Stub class to sit in place of an option within a computer.

    Args:
        name (str):
            name under which this arg is stored
        flag (str):
            Flag to append value to e.g. `--nodes`, `--walltime`
        separator (str):
            Override the separator between flag and value (defaults to "=")
        tag (str):
            Override the tag preceding the flag (defaults to "--")

    .. note::
        For other args see the DynamicMixin class
    """

    __slots__ = [
        "flag",
        "pragma",
        "tag",
        "separator",
    ]

    def __init__(
        self,
        name: str,
        flag: Union[str, None] = None,
        tag: Union[str, None] = None,
        separator: Union[str, None] = None,
        **kwargs,
    ):
        super().__init__(assignment=name, **kwargs)
        self.flag = flag

        self.pragma = None
        self.tag = tag
        self.separator = separator

    def __hash__(self):
        return hash(self.flag)

    def __repr__(self):
        return str(self.value)

    def __bool__(self):
        """
        Makes objects "falsy" if no value has been set, "truthy" otherwise
        """
        return self.value is not None and self.flag is not None

    @property
    def resource_line(self) -> str:
        """
        Shortcut to output a suitable resource request line

        Returns:
            str: resource request line
        """
        pragma = f"{self.pragma} " if self.pragma is not None else ""
        tag = self.tag if self.tag is not None else "--"
        separator = self.separator if self.separator is not None else "="

        return f"{pragma}{tag}{self.flag}{separator}{self.value}"

    def pack(self, collect_value: bool = True) -> dict:
        """Store this Resource in dict form"""
        data = super().pack(collect_value=collect_value)

        for k in self.__slots__:
            v = getattr(self, k, None)

            if v is not None:
                data[k] = v

        return data


class runargs(dict):
    """
    Class to contain the dataset run_args in a way that won't break any loops
    over the resources

    Args:
        args (dict):
            Dataset run_args
    """

    _accesserror = (
        "\nParser is attempting to access the flag of the run_args, you "
        "should add an `if {option}: ...` catch to your parser."
        "\nRemember that placeholders without an argument are 'falsy', "
        "see the docs for more info. https://l_sim.gitlab.io/remotemanager"
        "/remotemanager.connection.computers.options.html"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __bool__(self):
        return False

    @property
    def value(self):
        """
        Prevents an AttributeError when a parser attempts to access the value.

        Returns:
            (dict): internal dict
        """
        return self.__dict__

    @property
    def flag(self):
        """
        Parsers should not access the flag method of the run_args, doing so likely
        means that a loop has iterated over this object and is attempting to insert
        it into a jobscript.

        Converts an AttributeError to one more tailored to the situation.

        Returns:
            RuntimeError
        """
        raise RuntimeError(runargs._accesserror)


class Resources:
    """
    Container class to store Resource objects for use by a parser
    """

    __slots__ = ["_names", "_resources", "_run_args", "pragma"]

    def __init__(self, resources, pragma, tag, separator, run_args):
        self._names = []
        self._resources = resources
        self._run_args = run_args

        self.pragma = pragma

        for resource in self._resources:
            self._names.append(resource.name)
            # add pragma to Resource for resource_line property
            resource.pragma = pragma
            if resource.tag is None:
                resource.tag = tag
            if resource.separator is None:
                resource.separator = separator

    def __iter__(self):
        return iter(self._resources)

    def __getitem__(self, item: str) -> Union[Resource, dict]:
        """
        Need to enable Resources["mpi"], for example

        Args:
            item:
                name of resource to get

        Returns:
            Resource
        """
        if item == "run_args":
            return self.run_args
        try:
            return self._resources[self._names.index(item)]
        except ValueError:
            raise ValueError(f"{self} has no resource {item}")

    def get(self, name: str, default: any = "_unspecified"):
        """Allows resource.get(name)"""
        if default == "_unspecified":
            return getattr(self, name)
        return getattr(self, name, default)

    def items(self):
        """dict.items() like proxy"""
        for resource in self:
            yield resource.name, resource

    @property
    def run_args(self) -> dict:
        """Returns the stored run_args"""
        return self._run_args
