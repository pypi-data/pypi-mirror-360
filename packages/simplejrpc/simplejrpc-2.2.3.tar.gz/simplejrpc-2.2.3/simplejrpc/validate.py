# -*- encoding: utf-8 -*-
import re
from typing import Any, NoReturn, Type, TypeVar, Union

from simplejrpc._types import _BaseForm  # type: ignore
from simplejrpc._types import _Validator  # type: ignore
from simplejrpc._types import _NoValue as NoValue  # type: ignore
from simplejrpc.exceptions import AttributeError, ValidationError
from simplejrpc.field import StringField
from simplejrpc.form import Form
from simplejrpc.i18n import Language
from simplejrpc.i18n import T as i18n

T = Type[Union[str, int, float, bool]]
F = TypeVar("F", bound=_BaseForm)


# +--------------------------------------------------
# Validator
# +--------------------------------------------------
class ValidatorBase(_Validator):
    """ """

    require = False

    def __init__(self, err_msg: Any = "", code: int | None = None) -> None:
        """ """
        self.name = NoValue
        self.label: str = ""
        self.value: Any = NoValue
        self.err_msg: str = err_msg
        self.instance = NoValue
        self.code = code

    def update_attr(self, value: Any) -> None:
        """ """
        raise NotImplementedError

    def get_validate_err(self) -> Any:
        """ """
        return self.err_msg

    def raise_except(self, e: Exception | None = None) -> NoReturn:
        """
        The function raises an exception based on the value of the err_msg attribute.
        """
        if self.err_msg:
            if self.code is not None:
                raise ValidationError(self.err_msg, code=self.code)
            raise ValidationError(self.err_msg)
        elif e is not None:
            raise e
        else:
            msg = f"Please enter a valid {self.label or self.name} value"
            if self.code is not None:
                raise AttributeError(msg)
            raise AttributeError(msg)

    def clean(self, instance: Type[F]) -> Any:
        """
        The function "clean" attempts to clean data, raises a FormValidateError if validation fails, and
        raises any other exceptions.
        """
        try:
            self.clean_data(instance)
        except ValidationError as e:  # Explicitly use imported ValidationError
            raise e
        except Exception as e:
            self.raise_except(e)

    # @abstractmethod
    def clean_data(self, instance: Type[F]) -> Any:
        """
        The function clean_data is not implemented yet.

        If the parameter does not meet the condition,
        please use exception thrown,
        will automatically catch processing
        """
        raise NotImplementedError


class Validator(ValidatorBase):
    """ """

    """
    The function updates an attribute of an instance with a new value.

    :param value: The parameter "value" in the above code is of type "Type[T]". This means that it can
    accept any type of value, but it must be a subclass of type "T"
    :type value: Type[T]
    """

    def update_attr(self, value: T):
        """
        Updates the attribute value of the instance.

        Args:
            value: The new value to be assigned to the attribute.

        Returns:
            None

        Examples:
            # Update the attribute value of the instance
            >>> update_attr(10)
        """
        if not isinstance(self.name, str) or not self.name:
            raise AttributeError(
                "Validator 'name' attribute must be a non-empty string before updating attribute."
            )
        self.instance.__dict__[self.name] = value
        self.value = value


class BooleanValidator(Validator):
    """
    The BooleanValidator class is a subclass of ValidatorBase that validates a boolean value and raises
    an exception if the value is not true.
    """

    def clean(self, instance: Type[F]):
        """
        The function "clean" attempts to clean data, raises an exception if an error occurs, and raises an
        exception if the cleaned data is empty.
        """
        try:
            value: Any = self.clean_data(instance)
        except Exception as e:
            self.raise_except(e)
        if not value:
            self.raise_except()


class RequireValidator(Validator):
    """
    The `RequireValidator` class is a subclass of `ValidatorBase` that checks if a value is empty or
    None and raises an exception if it is.
    """

    NULL_VALUE: list[Any] = ["", None, [], {}]
    require = True

    def clean_data(self, instance: Type[F]):
        """
        The function `clean_data` checks if a value is empty or None and raises an exception if it is.
        """
        if self.value in self.NULL_VALUE:
            if self.err_msg:
                if self.code is not None:
                    raise ValidationError(f"{self.err_msg}", code=self.code)
                raise ValidationError(f"{self.err_msg}")

            msg = f"Please enter a valid {self.label or self.name} value"
            if self.code is not None:
                raise ValidationError(
                    message=msg,
                    code=self.code,
                )
            raise ValidationError(msg)


class StrictPasswordValidator(Validator):
    """ """

    PASSWD_VALIDATE_LENGTH = 8

    def __init__(self, err_msg: str = "", length: int = 8) -> None:
        """ """
        self.name = NoValue
        self.value = NoValue
        self.err_msg = err_msg
        self.instance = NoValue
        self.length = self.PASSWD_VALIDATE_LENGTH or length

    def clean_data(self, instance: Type[F]):
        """
        Clean the data by validating the password input.

        Args:
            instance: The instance of the data to be cleaned.

        Raises:
            FormValidateError: If the password input is invalid, such as empty, too short, not starting with a letter,
            not containing at least three character types, or not meeting the specified criteria.
        """

        _err_message = f"Check whether the password is valid: it must start with a letter and contain at least {self.length} digits and uppercase letters."
        if self.value == "" or self.value is None:
            raise ValidationError(_err_message)
        if len(self.value) < self.length:
            raise ValidationError(_err_message)
        if not self.value[0].isalpha():
            raise ValidationError(_err_message)
        char_types = 0
        if any(c.isupper() for c in self.value):
            char_types += 1
        if any(c.islower() for c in self.value):
            char_types += 1
        if any(c.isdigit() for c in self.value):
            char_types += 1
        if any(not c.isalnum() for c in self.value):
            char_types += 1
        if char_types < 3:  # 满足四分之三原则
            raise ValidationError(_err_message)


class NameValidator(Validator):
    """ """

    def clean_data(self, instance: Type[F]):
        if not bool(re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", str(self.value))):
            tmp = f"Invalid name: {self.value}. Name must start with a letter or underscore and contain only letters, digits, or underscores."
            raise ValidationError(tmp)


class StringLangValidator(Validator):
    """ """

    def clean_data(self, instance: Type[F]):
        values = Language.values()
        if self.value not in values:
            tmp = f"Please enter a valid language code, such as {values} :{self.label or self.name}"
            raise ValidationError(tmp)
        i18n.set_lang(Language(self.value))


# The `BaseForm` class is a subclass of `MetaBase`.
class BaseForm(Form):
    """ """

    lang = StringField(validators=[StringLangValidator()])
