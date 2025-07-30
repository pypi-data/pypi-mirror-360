# -*- encoding: utf-8 -*-
import enum
import inspect
import itertools
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from simplejrpc.exceptions import RPCException, TypeError


class _ParameterKind(enum.IntEnum):
    POSITIONAL_ONLY = "positional-only"
    POSITIONAL_OR_KEYWORD = "positional or keyword"
    VAR_POSITIONAL = "variadic positional"
    KEYWORD_ONLY = "keyword-only"
    VAR_KEYWORD = "variadic keyword"

    def __new__(cls, description):
        value = len(cls.__members__)
        member = int.__new__(cls, value)
        member._value_ = value
        member.description = description
        return member

    def __str__(self):
        return self.name


_POSITIONAL_ONLY = _ParameterKind.POSITIONAL_ONLY
_POSITIONAL_OR_KEYWORD = _ParameterKind.POSITIONAL_OR_KEYWORD
_VAR_POSITIONAL = _ParameterKind.VAR_POSITIONAL
_KEYWORD_ONLY = _ParameterKind.KEYWORD_ONLY
_VAR_KEYWORD = _ParameterKind.VAR_KEYWORD


class Parameter(inspect.Parameter):
    """ """

    def __init__(self, name, kind, validate: Any = None, **kwargs):
        """ """
        super().__init__(name, kind, **kwargs)
        self.validate = validate

    def get_validate_err(self) -> Any:
        """ """
        validation = self.validate.required_validator() or self.validate
        return str(validation.err_msg) if validation else None

    def get_validate_err_message(self) -> str | None:
        """ """
        message = self.get_validate_err()
        return message if message else None

    def get_validate_error(self) -> Any:
        """ """
        return RPCException(self.get_validate_err_message())


class Signature(inspect.Signature):
    """ """

    def _bind(self, args, kwargs, *, partial=False):
        """Private method. Don't use directly."""

        arguments = {}

        parameters = iter(self.parameters.values())
        parameters_ex = ()
        arg_vals = iter(args)

        pos_only_param_in_kwargs = []

        while True:
            # Let's iterate through the positional arguments and corresponding
            # parameters
            try:
                arg_val = next(arg_vals)
            except StopIteration:
                # No more positional arguments
                try:
                    param = next(parameters)
                except StopIteration:
                    # No more parameters. That's it. Just need to check that
                    # we have no `kwargs` after this while loop
                    break
                else:
                    if param.kind == _VAR_POSITIONAL:
                        # That's OK, just empty *args.  Let's start parsing
                        # kwargs
                        break
                    elif param.name in kwargs:
                        if param.kind == _POSITIONAL_ONLY:
                            if param.default is inspect._empty:
                                msg = f"missing a required positional-only argument: {param.name!r}"
                                raise param.get_validate_error() or TypeError(msg)
                            # Raise a TypeError once we are sure there is no
                            # **kwargs param later.
                            pos_only_param_in_kwargs.append(param)
                            continue
                        parameters_ex = (param,)
                        break
                    elif (
                        param.kind == _VAR_KEYWORD
                        or param.default is not inspect._empty
                    ):
                        # That's fine too - we have a default value for this
                        # parameter.  So, lets start parsing `kwargs`, starting
                        # with the current parameter
                        parameters_ex = (param,)
                        break
                    else:
                        # No default, not VAR_KEYWORD, not VAR_POSITIONAL,
                        # not in `kwargs`
                        if partial:
                            parameters_ex = (param,)
                            break
                        else:
                            if param.kind == _KEYWORD_ONLY:
                                argtype = " keyword-only"
                            else:
                                argtype = ""
                            msg = "missing a required{argtype} argument: {arg!r}"
                            msg = msg.format(arg=param.name, argtype=argtype)
                            raise param.get_validate_error() or TypeError(msg)
            else:
                # We have a positional argument to process
                try:
                    param = next(parameters)
                except StopIteration:
                    raise param.get_validate_error() or TypeError(
                        "too many positional arguments"
                    )
                else:
                    if param.kind in (_VAR_KEYWORD, _KEYWORD_ONLY):
                        # Looks like we have no parameter for this positional
                        # argument
                        raise param.get_validate_error() or TypeError(
                            "too many positional arguments"
                        )

                    if param.kind == _VAR_POSITIONAL:
                        # We have an '*args'-like argument, let's fill it with
                        # all positional arguments we have left and move on to
                        # the next phase
                        values = [arg_val]
                        values.extend(arg_vals)
                        arguments[param.name] = tuple(values)
                        break

                    if param.name in kwargs and param.kind != _POSITIONAL_ONLY:
                        raise param.get_validate_error() or TypeError(
                            "multiple values for argument {arg!r}".format(
                                arg=param.name
                            )
                        ) from None

                    arguments[param.name] = arg_val

        # Now, we iterate through the remaining parameters to process
        # keyword arguments
        kwargs_param = None
        for param in itertools.chain(parameters_ex, parameters):
            if param.kind == _VAR_KEYWORD:
                # Memorize that we have a '**kwargs'-like parameter
                kwargs_param = param
                continue

            if param.kind == _VAR_POSITIONAL:
                # Named arguments don't refer to '*args'-like parameters.
                # We only arrive here if the positional arguments ended
                # before reaching the last parameter before *args.
                continue

            param_name = param.name
            try:
                arg_val = kwargs.pop(param_name)
            except KeyError:
                # We have no value for this parameter.  It's fine though,
                # if it has a default value, or it is an '*args'-like
                # parameter, left alone by the processing of positional
                # arguments.
                if (
                    not partial
                    and param.kind != _VAR_POSITIONAL
                    and param.default is inspect._empty
                ):
                    raise param.get_validate_error() or TypeError(
                        "missing a required argument: {arg!r}".format(arg=param_name)
                    ) from None

            else:
                arguments[param_name] = arg_val

        if kwargs:
            if kwargs_param is not None:
                # Process our '**kwargs'-like parameter
                arguments[kwargs_param.name] = kwargs
            elif pos_only_param_in_kwargs:
                raise TypeError(
                    "got some positional-only arguments passed as "
                    "keyword arguments: {arg!r}".format(
                        arg=", ".join(param.name for param in pos_only_param_in_kwargs),
                    ),
                )
            else:
                raise TypeError(
                    "got an unexpected keyword argument {arg!r}".format(
                        arg=next(iter(kwargs))
                    )
                )

        return self._bound_arguments_cls(self, arguments)


def _get_validation(name: str, field_validations: List[Tuple[str, Any]]) -> Any:
    """ """
    for field_validation in field_validations:
        """ """
        if name in field_validation:
            return field_validation[-1]


def make_signature(fields: List[Any], field_validations: List[Tuple[str, Any]]):
    """
    The function `make_signature` creates a signature object for a function based on a list of field
    names.

    :param fields: A list of any type of objects
    :type fields: List[Any]
    :return: an instance of the `inspect.Signature` class.
    """
    """ """
    params = []
    for name, required in fields:
        if required:
            params.append(
                Parameter(
                    name,
                    inspect.Parameter.KEYWORD_ONLY,
                    validate=_get_validation(name, field_validations),
                )
            )
        else:
            params.append(
                Parameter(
                    name,
                    inspect.Parameter.KEYWORD_ONLY,
                    validate=_get_validation(name, field_validations),
                    default=None,
                )
            )
    return Signature(params)


def str2int(value: str | int, name: str):
    """ """
    if isinstance(value, int):
        return value
    if not value.isdigit():
        raise TypeError(f"Field {name}, expected integer")

    return int(value)


def order_dict(data: Dict[str, Any], field: str = "lang") -> OrderedDict:
    """Extract the key value pairs corresponding to the fields and place them at the index position at the beginning of the ordered dictionary
    1. Extract the key value pairs corresponding to the fields
    2. Place the extracted key value pairs at the beginning of the ordered dictionary
    3. Place the remaining key value pairs of the ordered dictionary after the ordered dictionary
    4. Return an ordered dictionary

    :param data: Sort dict data
    :param field: Sort dict data by field
    :return: OrderedDict
    """

    if field not in data:
        return OrderedDict(data)
    ordered_dict = OrderedDict()
    ordered_dict[field] = data[field]
    for key, value in data.items():
        if key != field:
            ordered_dict[key] = value
    return ordered_dict
