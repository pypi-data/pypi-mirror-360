"""
The dykes plumbing module.

This is all the things used internally to turn your definitions into something useful.
"""

import argparse
import dataclasses
import typing
from inspect import getdoc
from sys import argv

from . import options, internal, utils

NO_TYPE = options.Action.COUNT, options.Action.STORE_FALSE, options.Action.STORE_TRUE
MUST_BE_FLAG = (
    options.Action.COUNT,
    options.Action.STORE_TRUE,
    options.Action.STORE_FALSE,
)


def parse_args[ArgsType](
    parameter_definition: type[ArgsType], *, args: list | None = None
) -> ArgsType:
    """
    Process arguments and conform them to an input type.

    Supports dataclasses and NamedTuples.

    Sample use:

        from dataclasses import dataclass
        from pathlib import Path

        from dykes import parse_args, Count

        @dataclass
        class Application:
            input: Path
            dry_run: bool
            verbosity: dykes.Count

        args = parse_args(Application)
        print(args)
    """
    if args is None:
        args = argv[1:]
    parser = build_parser(parameter_definition)
    parsed = parser.parse_args(args)
    return parameter_definition(**vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    hints = typing.get_type_hints(application_definition, include_extras=True)
    fields = _get_fields(application_definition)

    for dest, cls in hints.items():
        origin = utils.get_origin(cls)
        parameter_options: internal.ParameterOptions = internal.ParameterOptions(
            dest=dest,
            type=utils.get_field_type(cls),
            default=fields[dest].value if fields[dest].value else internal.UNSET,
        )

        parameter_options = utils.get_meta_args(cls, parameter_options)

        if parameter_options.action is internal.UNSET:
            if parameter_options.type is bool:
                if parameter_options.default is True:
                    parameter_options.action = options.Action.STORE_FALSE
                elif parameter_options.default in (False, internal.UNSET):
                    parameter_options.action = options.Action.STORE_TRUE

        if parameter_options.action in NO_TYPE:
            parameter_options.type = internal.UNSET

        store_flag_unset = (
            parameter_options.action is options.Action.STORE
            and parameter_options.flags is internal.UNSET
        )
        # If explicit Store action, we assume it's a flag.
        must_be_flag_unset = (
            parameter_options.action in MUST_BE_FLAG and not parameter_options.flags
        )
        if store_flag_unset or must_be_flag_unset:
            parameter_options.flags = [f"-{dest[0]}", f"--{dest.replace('_', '-')}"]

        if parameter_options.action is options.Action.COUNT:
            parameter_options.default = (
                parameter_options.default if parameter_options.default else 0
            )

        if origin is list and parameter_options.nargs is internal.UNSET:
            parameter_options.nargs = "+"

        flag_unset = parameter_options.flags is internal.UNSET
        default_set = parameter_options.default is not internal.UNSET
        nargs_not_default_friendly = parameter_options.nargs not in ("?", "*")
        if default_set and flag_unset and nargs_not_default_friendly:
            raise ValueError(
                "Positional arguments cannot have defaults without NumberOfArguments '?' or '*'."
            )
        arguments = parameter_options.as_dict()
        dest = arguments["dest"]
        flags = arguments.pop("flags", None)
        name_or_flags = flags if flags else [dest]
        if not flags:
            arguments.pop("dest")
        parser.add_argument(*name_or_flags, **arguments)
    return parser


class _Field(typing.Protocol):
    default: typing.Any
    default_factory: typing.Callable[[], typing.Any]


def _get_default(data_class_field: _Field):
    if data_class_field.default is not dataclasses.MISSING:
        return data_class_field.default
    elif data_class_field.default_factory is not dataclasses.MISSING:
        return data_class_field.default_factory()
    else:
        return internal.UNSET


def _get_fields(cls: type) -> dict["str", internal.Field]:
    fields = {}
    if dataclasses.is_dataclass(cls):
        fields = {
            field.name: internal.Field(
                field.name, _get_default(typing.cast(_Field, field))
            )
            for field in dataclasses.fields(cls)
        }

    elif isinstance(cls, internal.NamedTupleProtocol):
        fields = {
            field: internal.Field(field, cls._field_defaults.get(field, internal.UNSET))
            for field in cls._fields
        }
    else:
        raise ValueError(
            f"{cls.__name__} is not a supported class type. Please use a dataclass or NamedTuple."
        )
    return fields
