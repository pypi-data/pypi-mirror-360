import copy
import importlib
import json
import logging
import os.path
import re
import typing
import warnings
from typing import Union

import yaml

try:
    from warnings import deprecated
except ImportError:
    from typing_extensions import deprecated

from remotemanager.connection.computers.dynamicvalue import (
    DynamicMixin,
    DynamicValue,
    concat_basic,
)
from remotemanager.connection.computers.resource import Resource, Resources
from remotemanager.connection.computers.substitution import Substitution
from remotemanager.connection.computers.utils import try_value
from remotemanager.connection.url import URL
from remotemanager.logging_utils.utils import format_iterable
from remotemanager.storage.function import Function
from remotemanager.storage.sendablemixin import get_class_storage, INTERNAL_STORAGE_KEYS
from remotemanager.utils.tokenizer import Tokenizer
from remotemanager.utils.uuid import generate_uuid
from remotemanager.utils.version import Version

logger = logging.getLogger(__name__)

DEPRECATION_WARNING = (
    "BaseComputer is deprecated, being replaced entirely by Computer"
    "\n(from remotemanager import Computer)"
)


@deprecated(DEPRECATION_WARNING)
class BaseComputer(URL):
    """
    Base computer module for HPC connection management.

    Extend this class for connecting to your machine
    """

    def __init__(self, template: Union[str, None] = None, **kwargs):
        super().__init__(**kwargs)

        self._template = None
        self.template = template

        self._temporary_args = {}

        self.resource_tag = "--"
        self.resource_separator = "="

        self._extra = ""
        self._internal_extra = ""

        self._super_issued = True  # enables check for super() call

    def __getattribute__(self, item):
        if (
            item != "_temporary_args"
            and hasattr(self, "_temporary_args")
            and item in self._temporary_args
        ):
            val = self._temporary_args[item]
            logger.debug("returning alt __getattribute__ %s=%s", item, val)
            return val
        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        """
        If the set `key` attribute is a Resource, and `value` is not a Resource,
        instead set the `value` of that attribute

        Args:
            key:
                attribute name to set
            value:
                value to set to

        Returns:
            None
        """
        # if this resource already exists, and we're _not_ trying to set a new resource,
        # set the value of the Resource to value
        if key in self.__dict__ and isinstance(getattr(self, key), DynamicMixin):
            # need to get before we can set
            getattr(self, key).value = value
            logger.debug("used __setattr__ Resource override for %s=%s", key, value)
            return

        object.__setattr__(self, key, value)

    @property
    def uuid(self):
        seed = super().uuid
        base = format_iterable(self.arguments)

        return generate_uuid(seed + base)

    @property
    def short_uuid(self):
        return self.uuid[:8]

    def get_parser(self):
        parser = getattr(self, "parser", None)

        if parser is None:
            # legacy _parser
            parser = getattr(self, "_parser", None)

        return parser

    def _extract_subs(self, link: bool = True):
        symbols = re.finditer(r"#(\w+)(?::([^#]+))?#", self.template)  # noqa: W605
        logger.info("Found substitution targets within script:%s", symbols)
        processed = []
        for match in symbols:
            logger.debug("processing match %s", match)
            target = match.group(0)
            sym = match.group(1)
            kwargs = match.group(2)

            name = sym.lower()
            if name in processed:
                if kwargs is not None and kwargs != "":
                    raise ValueError(
                        f"Got more kwargs for already registered argument "
                        f"{name}: {target}"
                    )
                logger.debug("\talready processed, continuing")
                continue

            tmp = Substitution.from_string(target)

            existing = getattr(self, tmp.name, None)
            if existing is not None and not isinstance(existing, DynamicMixin):
                raise ValueError(
                    f'Variable "{tmp.name}" already exists. This could '
                    f"cause unintended behaviour, please choose another "
                    f"name"
                )

            setattr(self, tmp.name, tmp)

            processed.append(name)

        if link:
            self._link_dynamic_subs()

    def _link_dynamic_subs(self):
        # expand any {calculable} variables
        for sub in self.substitution_objects:
            default = sub.target_kwargs.get("default", None)
            # skip if None, not a string, or no {}
            if default is None or not isinstance(default, str) or "{" not in default:
                continue

            logger.debug("Further processing on default %s", default)

            main_cache = []
            proc_cache = []
            indent = 0
            for char in default:
                if char == "{":  # "indent" into brackets
                    indent += 1
                    continue
                if char == "}":  # "dedent" out of brackets
                    indent -= 1
                    # if we drop back into non processing stream, process what's in the
                    # process cache
                    if indent == 0:
                        tokenized = Tokenizer("".join(proc_cache))
                        for name in self.arguments:
                            tokenized.exchange_name(name, f"self.{name}")
                        logger.debug("\tevaluating source %s", tokenized.source)
                        try:
                            evaluated = eval(tokenized.source)
                        except Exception as ex:
                            raise RuntimeError(
                                f"{ex.__class__.__name__} when evaluating substitution "
                                f"{sub.name}: {tokenized.source}"
                                f"\n(see above)"
                            ) from ex
                        logger.debug("\tevaluated to: %s", evaluated)
                        main_cache.append(
                            evaluated
                        )  # This can be a DynamicValue, which needs to be handled later
                        proc_cache = []
                    continue

                if indent == 0:
                    # non processing stream, just append
                    main_cache.append(char)
                else:
                    proc_cache.append(char)

            logger.debug("Compacting cache %s", main_cache)
            # First, "squash" any strings
            # converts ["a", "b", "c"]
            # to ["abc"], respecting any breaks for dynamic values
            squashed = []
            tmp = []
            for char in main_cache:
                logger.debug(f"\tchar {char}")
                if isinstance(char, (DynamicValue, DynamicMixin, bool)) or char is None:
                    logger.debug(
                        "\t\tchar is dynamic or otherwise unjoinable, "
                        "add to output cache and continue"
                    )
                    squashed.append("".join(tmp))
                    squashed.append(char)
                    tmp = []
                else:
                    try:
                        char / 1
                        char = str(char)
                    except (TypeError, ValueError):
                        pass
                    logger.debug("\t\tadded to tmp, tmp is now: %s", tmp)
                    tmp.append(char)
            if len(tmp) != 0:
                logger.debug("\tfinal tmp comact: %s", tmp)
                squashed.append("".join(tmp))

            # then concat the items
            logger.debug("Pre concat list: %s", squashed)
            output = None
            for item in squashed:
                if try_value(item) == "" or item is None:
                    continue
                if output is None:
                    output = item
                else:
                    output = concat_basic(output, item)

            sub.default = output

    def unreduce_args(self) -> None:
        """
        Attempts to find any arguments who have had their chains "reduced", and
        unreduce them back into dynamic variables
        """

        def unreduce_attribute(tmp):
            replace = False
            if isinstance(tmp, str):
                if tmp.startswith('"'):
                    logger.debug(
                        """\tValue is quoted, stripping ", but not replacing"""
                    )
                    tmp = tmp.strip('"')
                elif tmp.startswith("'"):
                    logger.debug(
                        """\tValue is quoted, stripping ', but not replacing"""
                    )
                    tmp = tmp.strip("'")
                else:
                    replace = True

            if replace:
                replaced = False  # only evaluate if a replacement occurs
                for name in self.arguments:
                    if name in tmp:
                        tmp = tmp.replace(name, f"self.{name}")
                        replaced = True
                logger.debug("\tUpdated default for %s to %s.)", arg.name, tmp)
                if replaced:
                    try:
                        tmp = eval(tmp)
                        logger.debug("\tEvaluated to %s.)", tmp)
                    except Exception as E:
                        logger.warning(
                            "Got an exception when attempting to "
                            "evaluate the arg %s with default %s:\n%s",
                            arg.name,
                            tmp,
                            str(E),
                        )
                else:
                    logger.debug("\tNo replacement, no evaluation.")
                logger.debug(
                    "\tDone.)",
                )
            else:
                logger.debug(f"\tNot stringtype ({type(tmp)}, no replacement.")
            return tmp

        logger.debug("unreducing all args, %s", self.arguments)
        for arg in self.argument_objects:
            tmp = getattr(arg, "default", None)
            logger.debug("Treating default for %s=%s.)", arg.name, tmp)
            arg.default = unreduce_attribute(tmp)

    @classmethod
    def from_dict(cls, spec: dict, **url_args):
        """
        Create a Computer class from a `spec` dictionary. The required values are:

        - resources:
            a dict of required resources for the machine (mpi, nodes, queue, etc.)
        - resource_parser:
            a function which takes a dictionary of {resource: Option}, returning a list
            of valid jobscript lines

        You can also provide some optional arguments:

        - required_or:
            list of resources, ONE of which is required. Note that this must be a
            _list_ of dicts, one for each or "block"
        - optional_resources:
            as with `resources`, but these will not be stored as required values
        - optional_defaults:
            provide defaults for the names given in optional_resources. When adding the
            optional arg, the optional_defaults will be checked to see if a default is
            provided
        - host:
            machine hostname. Note that this _must_ be available for a job run, but if
            not provided within the spec, can be added later with
            ``url.host = 'hostname'``
        - submitter:
            override the default submitter
        - python:
            override the default python
        - extra:
            any extra lines that should be appended after the resource specification.
            Note that this includes module loads/swaps, but this can be specified on a
            per-job basis, rather than locking it into the `Computer`

        The `resources` specification is in `notebook`:`machine` order. That is to say
        that the `key` is what will be required in the _notebook_, and the `value` is
        what is placed in the jobscript:

        >>> spec = {'resources': {'mpi': 'ntasks'}, ...}
        >>> url = BaseComputer.from_dict(spec)
        >>> url.mpi = 12
        >>> url.script()
        >>> "--ntasks=12"

        Args:
            spec (dict):
                input dictionary
            url_args:
                any arguments to be passed directly to the created `url`

        Returns:
            Computer class as per input spec
        """
        from remotemanager import Logger

        payload = copy.deepcopy(spec)
        # initialise with the version checking
        version = payload.pop("remotemanager_version", None)
        if version is not None:
            version = Version(version)
            Logger.debug(f"unpacking file generated by remotemanager v{version}")
        else:
            Logger.debug("no version detected within file, proceeding with care")

        # check if we have a stored Computer Class
        class_store_key = INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"]
        if class_store_key in payload:
            class_storage = payload[class_store_key]
            Logger.debug(f"using class storage {class_storage}")
            # first, try grab the module
            try:
                mod = importlib.import_module(class_storage["mod"])
                # then try import from that module
                try:  # replace the cls if possible
                    cls = getattr(mod, class_storage["name"])
                except AttributeError:  # inner import error, no class
                    warnings.warn(f"Could not import class {class_storage['name']}")
            except ModuleNotFoundError:  # outer import error, no module
                warnings.warn(f"Could not import module {class_storage['mod']}")
        Logger.debug(f"from_dict called on {cls}")
        # now attempt to unpack the parser, if it exists
        parser = None
        parser_source = payload.pop("resource_parser_source", None)
        if parser_source is not None:
            Logger.debug("generating parser from source code")
            parser = unpack_parser(parser_source)
        else:  # legacy unpack method
            Logger.debug("parser source code not found at resource_parser_source")
            parser_source = payload.pop("resource_parser", None)
            parser = unpack_parser(parser_source)
        # parser object must be assigned (monkey patched) at class level, or it will
        # not be a bound-method, which is required for `self` and inspect to work
        if parser is not None:
            Logger.debug("assigning parser object at parser")
            cls.parser = parser.object
            cls._parser_source = parser.raw_source
        else:
            Logger.debug("parser NOT assigned")
        # create a new instance of the class
        computer = cls()
        # collect the resources and substitutions that are stored
        # these need to be handled later
        resources = payload.pop("resources")
        substitutions = payload.pop("substitutions", {})
        # `extra` is nuanced, needs to be split into internal and external
        external_extra = payload.pop("extra", "")
        setattr(computer, "_extra", external_extra)
        internal_extra = payload.pop("internal_extra", "")
        setattr(computer, "_internal_extra", internal_extra)

        # add bulk of the content first
        for key, val in payload.items():
            setattr(computer, key, val)
        for key, val in url_args.items():
            setattr(computer, key, val)

        # add the argument objects after
        # this allows any special settings to take priority
        oldstyle = False
        for field, resource_args in resources.items():
            if isinstance(resource_args, str):
                # this is a consequence of an older style "name": "flag" spec
                # cast to new type by setting it to "flag"
                # other args can be set later
                oldstyle = True
                resource_args = {"flag": resource_args, "optional": False}
            if "name" not in resource_args:
                resource_args["name"] = field
            resource = Resource(**resource_args)
            # we need to use the base object setattr, since we override it here
            object.__setattr__(computer, field, resource)

        for field, sub_args in substitutions.items():
            sub_args["name"] = field
            sub = Substitution(**sub_args)
            object.__setattr__(computer, field, sub)
        # legacy style spec has some extra fields to handle
        # update the computer inplace with a function
        if oldstyle:
            legacy_unpack(computer, payload)

        computer.unreduce_args()
        return computer

    @property
    def parser_source(self) -> str:
        if getattr(self, "_parser_source", None) is not None:
            parser = Function(self._parser_source, force_self=True).raw_source
        else:
            parser = self.get_parser()
            try:
                # avoids a strange error where the parser source cant be found.
                # likely loads it into memory where `inspect` can access it
                # noinspection PyStatementEffect
                parser
            except AttributeError:
                pass

        if isinstance(parser, Function):
            return parser.raw_source
        elif parser is not None:
            return Function(parser, force_self=True).raw_source

    def to_dict(
        self,
        include_extra: bool = True,
        include_version: bool = True,
        collect_values: bool = True,
    ) -> dict:
        """
        Generate a spec dict from this Computer

        Args:
            include_extra:
                includes the `extra` property if True (default True)
            include_extra:
                includes the current remotemanager version if True (default True)
            collect_value:
                Also collects the stored values of the arguments if True

        Returns:
            dict
        """
        from remotemanager import __version__

        logger.debug(f"to_dict called on {self}")

        # gather all non resource objects
        spec = {
            k: getattr(self, k)
            for k in self.__dict__
            if k not in self.arguments and not k.startswith("_")
        }

        spec["resources"] = {
            n: r.pack(collect_value=collect_values)
            for n, r in self.resource_dict.items()
        }

        spec["substitutions"] = {
            n: r.pack(collect_value=collect_values)
            for n, r in self.substitution_dict.items()
        }

        spec["resource_parser_source"] = self.parser_source

        # grab `extra` if requested
        spec["internal_extra"] = self._internal_extra
        if include_extra and self.extra is not None:
            spec["extra"] = try_value(self._extra)
        # round up missing package inclusions
        collect = [
            "submitter",
            "shebang",
            "python",
            "pragma",
            "host",
            "user",
            "port",
            "template",
        ]
        for name in collect:
            val = getattr(self, name, None)
            if val is None:
                continue
            spec[name] = val
        # parser object is not required, and looks ugly
        if "parser" in spec:
            del spec["parser"]
        cls_store_key = INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"]
        spec[cls_store_key] = get_class_storage(self)

        if include_version:
            spec["remotemanager_version"] = __version__

        return spec

    @classmethod
    def from_yaml(cls, filepath: str, **url_args):
        """
        Create a Computer from `filepath`.

        Args:
            filepath:
                path containing yaml computer spec
            **url_args:
                extra args to be passed to the internal URL

        Returns:
            BaseComputer
        """
        if isinstance(filepath, str):
            try:
                with open(filepath, "r") as o:
                    data = yaml.safe_load(o)
            except OSError:
                data = yaml.safe_load(filepath)
        else:
            data = yaml.safe_load(filepath)

        return cls.from_dict(data, **url_args)

    def to_yaml(
        self,
        filepath: Union[str, typing.IO, None] = None,
        include_extra: bool = True,
        include_version: bool = True,
        collect_values: bool = True,
    ) -> Union[str, None]:
        """
        Dump a computer to yaml `filepath`.

        Args:
            filepath:
                path containing yaml computer spec
            include_extra:
                includes the `extra` property if True (default True)
            collect_value:
                Also collects the stored values of the arguments if True
        """
        data = self.to_dict(
            include_extra=include_extra,
            include_version=include_version,
            collect_values=collect_values,
        )
        # source will simply not print correctly with base yaml
        # extract it and do it manually, if it exists
        if "resource_parser_source" in data:
            parser_string = ["resource_parser_source: |"] + [
                f"    {line}" for line in data.pop("resource_parser_source").split("\n")
            ]
            # dump the remaining content to string
            prepared = yaml.dump(data)
            # append the cleaned string
            prepared += "\n".join(parser_string)
        else:
            prepared = yaml.dump(data)

        if filepath is None:  # "dump" to string
            return prepared
        elif isinstance(filepath, str):  # dump to path
            with open(filepath, "w+") as o:
                o.write(prepared)
        else:  # assume file handler and dump there
            filepath.write(prepared)

    @staticmethod
    def download_file(file_url: str, filename: str) -> None:
        """
        Download file at url `file_url` and write the content out to `filename`

        Args:
            file_url: url of file
            filename: name to write content to
        """
        import requests

        response = requests.get(file_url)

        if response.status_code == requests.codes.ok:
            # Save the file
            fld, file = os.path.split(filename)
            if fld != "" and not os.path.exists(fld):
                os.makedirs(fld)

            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Grabbed file '{filename}'")
        else:
            raise RuntimeError(f"Could not find a file at: {file_url}")

    @classmethod
    def from_repo(
        cls,
        name: str,
        branch: str = "main",
        repo: str = "https://gitlab.com/l_sim/remotemanager-computers/",
        **url_args,
    ):
        """
        Attempt to access the remote-computers repo, and pull the computer with name
        `name`

        Args:
            name (str):
                computer name to target
            branch (str):
                repo branch (defaults to main)
            repo (str):
                repo web address (defaults to main l_sim repo)

        Returns:
            BaseComputer instance
        """
        from remotemanager.utils import ensure_filetype

        filename = ensure_filetype(name, "yaml").lower()
        url = f"{repo}-/raw/{branch}/storage/{filename}"

        print(f"polling url {url}")

        cls.download_file(url, filename)

        return cls.from_yaml(filename, **url_args)

    def generate_cell(
        self, name: Union[str, None] = None, return_string: bool = False
    ) -> Union[None, str]:
        """
        Prints out copyable source which regenerates this Computer

        Args:
            name (str, None):
                Optional name for new computer. Defaults to `new`
            return_string (bool):
                Also returns the string if True. Defaults to False

        Returns:
            (None, str)
        """
        if name is None:
            name = "new"
        output = [
            "# Copy the following into a jupyter cell or python script "
            "to generate a modifiable source",
            "\n# Parser source code",
        ]
        source = self.to_dict(include_version=False)

        try:
            output.append(self.parser_source)
            parser = Function(self.parser_source)

            source.pop("resource_parser_source")
            # use json.dumps with indent=4 to format dict
            output.append(
                f"\n# JSON compatibility\n"
                f"true = True\n"
                f"false = False\n\n"
                f"# spec dict\n\nspec = {json.dumps(source, indent=4)}"
            )
            output.append(f'spec["resource_parser"] = {parser.name}')

            output.append(f"\n{name} = BaseComputer.from_dict(spec)")

        except TypeError:
            output.append(
                f"# JSON compatibility\n"
                f"true = True\n"
                f"false = False\n\n"
                f"# spec dict\n\nspec = {json.dumps(source, indent=4)}"
            )
            output.append(f"\n{name} = BaseComputer.from_dict(spec)")

        output = "\n".join(output)

        print(output)

        if return_string:
            return output

    @property
    def is_super(self):
        if not hasattr(self, "_super_issued"):
            return False
        return self._super_issued

    @property
    def arguments(self) -> list:
        return sorted(
            [
                k
                for k, v in self.__dict__.items()
                if isinstance(v, (Resource, Substitution))
            ]
        )

    @property
    def substitutions(self) -> list:
        return sorted(
            [k for k, v in self.__dict__.items() if isinstance(v, Substitution)]
        )

    @property
    def resources(self) -> list:
        return sorted([k for k, v in self.__dict__.items() if isinstance(v, Resource)])

    @property
    def argument_objects(self) -> list:
        return [
            v
            for k, v in self.__dict__.items()
            if isinstance(v, (Resource, Substitution))
        ]

    @property
    def substitution_objects(self) -> list:
        return [v for k, v in self.__dict__.items() if isinstance(v, Substitution)]

    @property
    def resource_objects(self) -> list:
        return [v for k, v in self.__dict__.items() if isinstance(v, Resource)]

    @property
    def argument_dict(self) -> dict:
        return {k.name: k for k in self.argument_objects}

    @property
    def substitution_dict(self) -> dict:
        return {k.name: k for k in self.substitution_objects}

    @property
    def resource_dict(self) -> dict:
        return {k.name: k for k in self.resource_objects}

    @property
    def required(self) -> list:
        """
        Returns a list of required arguments
        """
        required = []

        def append_if(item):
            if item not in required:
                required.append(item)

        for name, resource in self.argument_dict.items():
            if not resource.optional:
                append_if(name)
            for name in resource.requires:
                append_if(name)

        return required

    @property
    def missing(self) -> list:
        """
        Returns the currently missing arguments
        """
        missing = []
        covered = []
        for resource in self.argument_objects:
            # this resource has a value, so is not missing, and can replace others
            if resource.value is not None:
                covered.append(resource.name)
                for name in resource.replaces:
                    if name in missing:
                        missing.remove(name)
                    covered.append(name)
            # resource is missing a value and is non optional
            elif not resource and not resource.optional:
                if resource.name not in covered:
                    missing.append(resource.name)

            for name in resource.requires:
                if name not in covered and not self.argument_dict[name]:
                    missing.append(name)

        return missing

    @property
    def valid(self) -> bool:
        """Returns True if there are no missing attributes"""
        return len(self.missing) == 0

    def parser(self, resources) -> list:
        """
        Default parser for use on basic "SLURM style" machines.

        Will iterate over resource objects, creating a script of the format:

        {pragma} --{flag}={value}

        ..note::
            This method can (and should) be overidden for a custom parser.

        Args:
            resources:
                Resources object, to be created by BaseComputer

        Returns:
            list of resource lines
        """
        output = []
        for r in resources:
            if r:
                output.append(r.resource_line)

        return output

    @property
    def extra(self):
        return try_value(self._internal_extra) + try_value(self._extra)

    @extra.setter
    def extra(self, external):
        self._extra = external

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._template = template
        if template is not None:
            self._extract_subs()

    def script(self, **kwargs) -> str:
        """
        Takes job arguments and produces a valid jobscript

        Args:
            insert_stub (add to kwargs):
                inserts the submission block stub if True (Used by Dataset)

        Returns:
            (str):
                script
        """
        if not self.is_super:
            raise RuntimeError(
                "This Computer does not seem to have the correct attributes.\n"
                "Is the super().__init__() line missing from this class' __init__?"
            )

        logger.info(f"script method called with run_args {kwargs}")
        # set temp args
        for k, v in kwargs.items():
            if k in self.arguments:
                self.argument_dict[k].temporary_value = v
            else:
                self._temporary_args[k] = v

        self._link_dynamic_subs()

        for key, val in kwargs.items():
            if key in self.arguments:
                logger.info("\tset temporary arg of %s to %s", key, val)
                self.argument_dict[key].temporary_value = val

        if not self.valid:
            raise RuntimeError(f"missing required arguments: {self.missing}")

        if self.template is None:
            logger.debug("Creating script from Resources")
            script = self._standard_script(**kwargs)
        else:
            logger.debug("Using template for generation")
            empty_treatment = kwargs.get("empty_treatment", "wipe")
            script = self.apply_substitutions(
                self.template.split("\n"), empty_treatment=empty_treatment
            )

        self._temporary_args = {}
        for arg in self.argument_objects:
            arg.reset_temporary_value()

        return script

    def _standard_script(self, **kwargs):
        pragma = getattr(self, "pragma", None)
        submit_args = Resources(
            resources=copy.deepcopy(self.resource_objects),
            pragma=pragma,
            tag=self.resource_tag,
            separator=self.resource_separator,
            run_args=kwargs,
        )

        script = [self.shebang]

        script += self.parser(submit_args)

        if self.extra is not None:
            script.append(self.extra)

        extras = ["global_extra", "runner_extra", "tmp_extra"]
        for key in extras:
            extra = kwargs.get(key, None)
            if extra is not None:
                script.append(extra)

        insert_stub = kwargs.pop("insert_stub", False)
        if insert_stub:
            script.append("#SUBMISSION_SUBSTITUTION#")

        script = self.apply_substitutions(script)

        return script

    def apply_substitutions(self, script: list, empty_treatment: str = "wipe") -> str:
        """
        Apply Substitution objects to the script

        Args:
            script: Base script to operate on
            empty_treatment: Defines the default behaviour for valueless args
                wipe: deletes the whole line (default)
                ignore: skip the value, leaving the substitution object there
                local: deletes only the missing argument
        """
        empty_behaviours = ["wipe", "ignore", "local"]

        if empty_treatment not in empty_behaviours:
            raise ValueError(
                f"empty_treatment={empty_treatment} is "
                f"not in available behaviours: {empty_behaviours}"
            )

        script = "\n".join(script)

        logger.debug("applying substitutions to script:\n%s", script)

        for sub in self.substitution_objects:
            logger.debug("processing Sub pointed at %s", sub.target)
            if sub.target == "":
                continue  # can't replace "" with something

            term = re.compile(f"#{sub.name}#", re.IGNORECASE)
            logger.debug("\tusing search term %s", term)

            value = sub.value
            logger.debug("\tvalue evaluated to %s", value)
            if sub.target not in script and re.search(term, script) is None:
                logger.debug("target not found")
                continue
            elif value is not None:
                sub.executed = True
                # replace once, using regex to collect differing cases
                script = re.sub(term, str(value), script)
                # replace again using the original target, since the regex will miss it
                script = script.replace(sub.target, str(value))
                logger.debug("replaced")
            elif empty_treatment in ["wipe", "local"]:  # remove nonvalued entries
                script = re.sub(term, "~mark_for_deletion~", script)
                script = script.replace(sub.target, "~mark_for_deletion~")
                logger.debug("no value, replaced with deletion mark")
        # remove any lines marked for deletion by appending those without the mark
        clean = []
        for line in script.split("\n"):
            if "~mark_for_deletion~" not in line:
                clean.append(line)
            elif empty_treatment == "local":
                tmp = line.replace("~mark_for_deletion~", "")
                clean.append(tmp)
            elif "#SUBMISSION_SUBSTITUTION#" in line:
                clean.append("#SUBMISSION_SUBSTITUTION#")
        script = "\n".join(clean)
        del clean

        return script

    def pack(self, file=None):
        if file is not None:
            self.to_yaml(filepath=file)
            return
        return self.to_dict()

    @classmethod
    def unpack(cls, data: dict = None, file: str = None, limit: bool = True):
        if file is not None:
            return cls.from_yaml(file)
        return cls.from_dict(data)


def unpack_parser(parser_data) -> Function:
    """
    Parser data can be either a string, dict or callable.
    Handle all and return the Function

    Args:
        parser_data:
            stored parser
    Returns:
        Function
    """
    if callable(parser_data):
        return Function(parser_data, force_self=True)
    if isinstance(parser_data, str):
        return Function(parser_data, force_self=True)
    if isinstance(parser_data, dict):
        return Function.unpack(parser_data, force_self=True)
    if isinstance(parser_data, Function):
        return parser_data
    return parser_data


def legacy_unpack(computer: BaseComputer, payload: dict) -> None:
    """
    Handle legacy style dictionary specs

    Args:
        computer:
            BaseComputer subclass to be updated
        payload:
            spec payload

    Returns:
        None
    """
    optional = payload.pop("optional_resources", {})
    for name, flag in optional.items():
        resource = Resource(name=name, flag=flag)
        object.__setattr__(computer, name, resource)

    required_or = payload.pop("required_or", [])
    for group in required_or:
        for name, flag in group.items():
            replaces = [n for n in group if n != name]
            resource = Resource(name=name, flag=flag, optional=False, replaces=replaces)
            object.__setattr__(computer, name, resource)

    defaults = payload.pop("optional_defaults")
    for name, default in defaults.items():
        computer.resource_dict[name].default = default

    print(
        "WARNING! Old style import detected. "
        "You should check the validity of the "
        "resulting Computer then re-dump to yaml."
    )
