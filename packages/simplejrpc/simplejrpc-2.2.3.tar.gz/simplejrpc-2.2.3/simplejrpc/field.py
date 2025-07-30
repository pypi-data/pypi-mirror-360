# -*- encoding: utf-8 -*-
import re
from abc import abstractmethod
from typing import Generic, List, NoReturn, Optional, TypeVar, Union

from simplejrpc._types import _NoValue as NoValue  # type: ignore
from simplejrpc._types import _Validator as Validator  # type: ignore
from simplejrpc.exceptions import RPCException, TypeError, ValidationError
from simplejrpc.func import str2int

T = TypeVar("T")


class nan:
    """ """

    def __str__(self) -> str:
        """ """
        return self.__class__.__name__

    def __repr__(self) -> str:
        """ """
        return self.__class__.__name__


# +--------------------------------------------------
# Field
# +--------------------------------------------------
class BaseField(Generic[T]):
    """ """

    value: Optional[T] = None

    def __init__(
        self,
        validators: Optional[List[Validator]] = None,
        err_msg: str = "",
        default: Optional[T] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """
        The above function is a constructor that initializes the instance variables `_validators`, `name`,
        and `err_msg`.

        :param validators: The `validators` parameter is a list of functions that will be used to validate
        the input. Each function should take a single argument (the input value) and return `True` if the
        value is valid, or `False` otherwise. By default, if no validators are provided, an empty list
        :param err_msg: The `err_msg` parameter is a string that represents the error message that will be
        displayed if any of the validators fail
        """
        if validators is None:
            validators = []
        self._validators: List["Validator"] = list(validators)
        self.name: Optional[str] = None
        self.err_msg: str = err_msg
        self.default = default
        self.valid: str = valid
        self.label: str = label

    @abstractmethod
    def validator(self, value: T) -> T:
        """ """
        raise NotImplementedError

    def get_validators(self):
        """
        The function returns the validators associated with an object.
        :return: The method is returning the value of the variable `self._validators`.
        """
        return self._validators

    def required_validator(self) -> "Validator":
        """ """
        for v in self._validators:
            require = getattr(v, "require", False)
            if require:
                return v
        raise ValidationError("No required validator found")

    @property
    def required(self):
        """
        The function checks if any of the validators in a list have the "require" attribute set to True.
        :return: The code is returning a boolean value indicating whether any of the validators in the
        `_validators` list have the `require` attribute set to `True`.
        """
        return any(getattr(v, "require", False) for v in self._validators)

    def raise_except(
        self, err_msg: str, except_type: Optional[Exception] = None
    ) -> NoReturn:
        """
        The function raises an exception based on the value of the err_msg attribute.
        """
        if self.err_msg:
            raise except_type(self.err_msg)  # type: ignore
        elif except_type is not None:
            raise except_type(err_msg)  # type: ignore
        else:
            raise ValidationError(err_msg)


class Field(BaseField[T]):
    """
    The `Field` class is a descriptor that sets a value for an attribute in an instance, checks if the
    value is of the expected type, and cleans the data using a list of validators.
    """

    expected_type: Optional[type] = None
    _attr = ["name", "label", "value", "instance"]

    def _get_value(self, value: T) -> T:
        """Get the value"""
        if self.default is None:
            return value
        if value is not None:
            return value
        return self.default  # self.default is now Optional[T], matching return type T

    def __set__(self, instance: T, value: T, *args: object, **kw: object):
        """
        The function sets a value for an attribute in an instance, checking if the value is of the expected
        type and cleaning the data.

        :param instance: The instance object being modified
        :param value: The value being assigned to the attribute
        """
        if self.expected_type is not None and not isinstance(value, self.expected_type):
            _err_message = f"Field {self.label or self.name}, expect type {self.expected_type.__name__}"
            self.raise_except(_err_message, TypeError)  # type: ignore
        try:
            if isinstance(value, bool):
                _value = self._get_value(value)  # type: ignore
                new_value: T = self.validator(_value) or value  # type: ignore
            else:
                validated_value = self.validator(self._get_value(value))  # type: ignore
                new_value: T = self._get_value(validated_value)
        except NotImplementedError as e:
            raise e
        except RPCException as e:
            raise e
        except Exception as e:
            self.raise_except(str(e), ValidationError)  # type: ignore
        self.clean_data(instance, new_value if "new_value" in locals() else value)

    def validator(self, value: T) -> T:
        """ """
        return value

    def clean_data(self, instance: T, value: T):
        """
        The `clean_data` function iterates through a list of validators, sets the necessary attributes for
        each validator, and then calls the `clean` method of each validator to validate the data.

        :param instance: The `instance` parameter refers to an instance of a class or object that contains
        the data to be cleaned. It is likely that this method is part of a larger class or form validation
        system
        :param value: The `value` parameter represents the value that needs to be cleaned. It is passed to
        the `clean_data` method as an argument
        """
        for validator in self._validators:
            err_dict = {}
            for __k, __v in zip(self._attr, [self.name, self.label, value, instance]):
                validator.__dict__[__k] = __v
            try:
                validator.clean(instance)
            except RPCException as e:
                err_dict["msg"] = e.message
                err_dict["code"] = e.code
                setattr(instance, "code", e.code)
                instance.errors.append(err_dict)  # type: ignore
                break
            except Exception as e:
                err_dict["msg"] = self.err_msg or str(e)
                instance.errors.append(err_dict)  # type: ignore
                break
        instance.__dict__[self.name] = value  # type: ignore
        self.value = value

    def __delete__(self, instance: T):
        """ """
        del instance.__dict__[self.name]  # type: ignore


class StringField(Field[str]):
    """ """

    expected_type = str


class StringIdentifierField(Field[str]):
    """ """

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        err_msg: str = "",
        default: Optional[str] = None,
        max_len: int = 25,
        min_len: int = 1,
        valid: str = "",
        label: str = "",
    ) -> None:
        self.max_len = max_len
        self.min_len = min_len
        super().__init__(validators, err_msg, default, valid, label=label)

    def validator(self, value: str) -> str:
        """ """
        pattern = r"^[a-zA-Z].[a-z0-9A-Z_/]+"
        if value in [None, ""] or not re.match(pattern, value):
            """ """
            _err_message = f"Please enter a valid {self.label or self.name} value"
            self.raise_except(_err_message, ValidationError)  # type: ignore

        if len(value) < self.min_len or len(value) > self.max_len:
            """ """
            _err_message = f"Please enter a valid {self.label or self.name} value length: {self.min_len} ~ {self.max_len}"
            self.raise_except(_err_message, ValidationError)  # type: ignore

        return value


class StringRegexField(StringField):
    """ """

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        err_msg: str = "",
        regex: Optional[str] = None,
        default: Optional[str] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        self.regex = regex
        super().__init__(validators, err_msg, default, valid=valid, label=label)

    def validator(self, value: str) -> str:
        """ """
        if value in [None, ""]:
            tmp = f"Please enter a valid {self.label or self.name} value"
            self.raise_except(tmp, ValidationError)  # type: ignore

        if self.regex is None:
            return value

        if not re.match(self.regex, value):
            tmp = f"Please enter a valid {self.label or self.name} value"
            self.raise_except(tmp, ValidationError)  # type: ignore
        return value


class BooleanField(Field[bool]):
    """ """

    expected_type = bool


class IntegerField(Field[int]):
    """ """

    expected_type = int


from typing import Any


class ListField(Field[List[Any]]):
    """ """

    expected_type = list


from typing import Any


class DictField(Field[dict[str, Any]]):
    """ """

    expected_type = dict


class NoValueField(Field[NoValue]):
    """ """

    expected_type = NoValue


class RangeField(Field[T]):
    """ """

    ALLOW: list[T] = []

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        err_msg: str = "",
        allow: Optional[list[T]] = None,
        default: Optional[T] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        if allow is None:
            allow = []
        self.ALLOW = allow or self.ALLOW  # type:ignore
        super().__init__(validators, err_msg, default, valid=valid, label=label)

    def validator(self, value: T):
        """ """
        if value not in self.ALLOW:
            tmp = f"Please enter a valid {self.label or self.name} value: range {str(self.ALLOW)}"
            self.raise_except(tmp, ValidationError)  # type:ignore
        return value


class StrRangeField(StringField, RangeField[str]):
    pass


class IntRangeField(IntegerField, RangeField[int]): ...


class PortField(Field[int]):
    """ """

    MIN = 1
    MAX = 65535
    expected_type = NoValue

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        min_value: Optional[int] = 1,
        max_value: Optional[int] = 65535,
        err_msg: str = "",
        default: Optional[int] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        super().__init__(validators, err_msg, default, valid=valid, label=label)
        self.min_value = min_value or self.MIN
        self.max_value = max_value or self.MAX

    def validator(self, value: Union[str, int, Any]) -> Any:
        """ """
        if value in [None, ""]:
            return

        tmp = f"Please enter a valid port value: {value}"
        if isinstance(value, str):
            """ """
            if not value.isdigit():
                self.raise_except(tmp, ValidationError)  # type:ignore
            port = int(value)
        elif isinstance(value, int):
            port = value
        else:
            self.raise_except(tmp, ValidationError)  # type:ignore
        if port < self.min_value or port > self.max_value:
            self.raise_except(tmp, ValidationError)  # type:ignore
        return port


class LengthLimitField(StringField, Field[str]):
    """ """

    MIN_LENGTH = 0
    MAX_LENGTH = 32

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        min_length: Optional[int] = 0,
        max_length: Optional[int] = 32,
        err_msg: str = "",
        default: Optional[str] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        super().__init__(validators, err_msg, default, valid=valid, label=label)
        self.min_length = min_length or self.MIN_LENGTH
        self.max_length = max_length or self.MAX_LENGTH

    def validator(self, value: str) -> Any:
        """ """
        if value in [None, ""]:
            return
        if len(value) < self.min_length or len(value) > self.max_length:
            tmp = f"Please enter a valid {self.label or self.name} value length: {self.min_length} ~ {self.max_length}"
            self.raise_except(tmp, ValidationError)  # type:ignore
        return value


class StringRegexLimitField(StringField, Field[str]):
    """ """

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        min_length: Optional[int] = 0,
        max_length: Optional[int] = 32,
        err_msg: str = "",
        default: Optional[str] = None,
        regex: Optional[str] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        super().__init__(validators, err_msg, default, valid=valid, label=label)
        self._str_limit_field = LengthLimitField(
            validators=validators, min_length=min_length, max_length=max_length
        )
        self._str_regex_field = StringRegexField(validators=validators, regex=regex)

    def validator(self, value: T) -> T:
        """ """
        self._str_limit_field.validator(value)  # type:ignore
        self._str_regex_field.validator(value)  # type:ignore
        return value


class IntegerLimitField(IntegerField):
    """ """

    MIN = 0
    MAX = 100

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        min_value: Optional[int] = 0,
        max_value: Optional[int] = 32,
        err_msg: str = "",
        default: Optional[int] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        super().__init__(validators, err_msg, default, valid=valid, label=label)
        self.min_value = min_value or self.MIN
        self.max_value = max_value or self.MAX

    def validator(self, value: int) -> int:
        """
        Validate the input value against the minimum and maximum values.

        Args:
            value (int): The value to be validated.

        Raises:
            FormValidateError: If the value is not within the specified range.
        """
        if value in [None, ""]:
            tmp = f"Please enter a valid {self.label or self.name} value: {self.min_value} ~ {self.max_value}"
            self.raise_except(tmp, ValidationError)  # type:ignore

        if self.min_value is nan and self.max_value is nan:
            return value

        tmp = f"Please enter a valid {self.label or self.name} value: {self.min_value} ~ {self.max_value}"
        if self.min_value is nan and value > self.max_value:
            self.raise_except(tmp, ValidationError)  # type:ignore

        if self.max_value is nan and value < self.min_value:
            self.raise_except(tmp, ValidationError)  # type:ignore

        if not (self.min_value <= value <= self.max_value):
            self.raise_except(tmp, ValidationError)  # type:ignore
        return value


class StringValueLimitField(StringField):
    """ """

    def __init__(
        self,
        validators: Optional[List["Validator"]] = None,
        min_value: type = nan,
        max_value: type = nan,
        err_msg: str = "",
        default: Optional[str] = None,
        valid: str = "",
        label: str = "",
    ) -> None:
        """ """
        super().__init__(validators, err_msg, default, valid=valid, label=label)
        self.min_value = min_value
        self.max_value = max_value

    def validator(self, value: str) -> Any:
        """Validate"""

        if value in [None, ""]:
            return

        if self.min_value is nan and self.max_value is nan:
            """ """
            return

        if isinstance(value, str):  # type:ignore
            value_int = str2int(value, self.label or self.name)  # type:ignore
        else:
            value_int = value

        tmp = f"Please enter a valid {self.label or self.name} value: {self.min_value} ~ {self.max_value}"
        if self.min_value is nan:
            """ """
            max_value = str2int(self.max_value, "max_value")  # type:ignore
            if value_int > max_value:
                self.raise_except(tmp, ValidationError)  # type:ignore
            return

        if self.max_value is nan:
            """ """
            min_value = str2int(self.min_value, "min_value")  # type:ignore
            if value_int < min_value:
                self.raise_except(tmp, ValidationError)  # type:ignore
            return

        max_value = str2int(self.max_value, "max_value")  # type:ignore
        min_value = str2int(self.min_value, "min_value")  # type:ignore
        if value_int < min_value or value_int > max_value:
            self.raise_except(tmp, ValidationError)  # type:ignore
        return value


class StringLengthLimitField(LengthLimitField):
    """ """


class StringRangField(StrRangeField):
    """ """


class IntegerRangeField(IntRangeField):
    """ """
