import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from simplejrpc import exceptions
from simplejrpc._text import ErrorTextMessage as _
from simplejrpc.field import IntegerField, StringField, StringRangField
from simplejrpc.validate import BaseForm, RequireValidator, Validator


class StringForm(BaseForm):
    """ """

    action = StringRangField(validators=[RequireValidator()], allow=["add", "del"])


# Customize age field
class AgeField(IntegerField):
    """ """

    def __init__(self, *args, max_age=100, **kwargs):
        """ """
        self.max_age = max_age
        super().__init__(*args, **kwargs)

    def validator(self, value):
        """ """
        if not isinstance(value, int):
            raise exceptions.ValidationError("Age must be an integer")
        if not value:
            raise exceptions.ValidationError("Age is required")
        if value > self.max_age:
            raise exceptions.ValidationError(f"Age must be less than {self.max_age}")
        return value


class NameValidator(Validator):
    """ """

    def clean_data(self, instance):
        """ """
        if len(self.value) < 3:
            raise exceptions.ValidationError("Name must be at least 3 characters long")
        if len(self.value) > 20:
            raise exceptions.ValidationError(
                "Name must be less than 20 characters long"
            )
        return self.value


class UserForm(BaseForm):
    """ """

    age = AgeField()


class SynCZoneForm(BaseForm):
    """同步时间参数校验"""

    continent = StringField(validators=[RequireValidator(_(message="aaa"))])
    city = StringField(validators=[RequireValidator(_("REQUIRE_VALIDATION_TM"))])


class PersonalForm(BaseForm):
    # Attention: Different order of verification methods may result in different impacts
    name = StringField(validators=[RequireValidator("sss"), NameValidator()])


class I18nForm(BaseForm):
    """ """

    action = StringRangField(
        validators=[RequireValidator(_("[*] action is required"))],
        allow=["add", "del"],
        err_msg=_("[action] action is required: {}", "test"),
    )


class TestForm(unittest.TestCase):

    @unittest.skip
    def test_custom_form_i18n(self):
        """ """
        data = {"action": ""}
        # data = {}
        form = I18nForm(**data)
        self.assertEqual(form.action, "")
        self.assertEqual(form.errors, [])
        self.assertEqual(form.is_valid(), False)

    # @unittest.skip
    def test_custom_form_validator(self):
        """ """
        data = {"name": ""}
        # data = {}
        form = PersonalForm(**data)
        print(form.errors)
        form.raise_valid()
        # self.assertEqual(form.name, "John")
        # self.assertEqual(form.errors, [])
        # self.assertEqual(form.is_valid(), True)

        # data1 = {"name": "0"}
        # form = PersonalForm(**data1)
        # self.assertRaises(
        #     exceptions.RPCException,
        #     form.raise_all_errors,
        # )

        # data2 = {}
        # form = PersonalForm(**data2)
        # self.assertRaises(
        #     exceptions.RPCException,
        #     form.raise_all_errors,
        # )

    @unittest.skip
    def test_custom_form_field(self):
        """ """
        data = {"age": 10}
        form = UserForm(**data)
        self.assertEqual(form.age, 10)
        self.assertEqual(form.errors, [])
        self.assertEqual(form.is_valid(), True)

        data1 = {"age": 200}
        self.assertRaises(
            exceptions.RPCException,
            UserForm,
            **data1,
        )

        data2 = {}
        self.assertRaises(
            exceptions.RPCException,
            UserForm,
            **data2,
        )

    @unittest.skip
    def test_form(self):
        """ """
        data = {"action": "add"}
        form = StringForm(**data)
        self.assertEqual(form.action, "add")
        self.assertEqual(form.errors, [])
        self.assertEqual(form.is_valid(), True)

        data1 = {"action": "delete"}
        self.assertRaises(
            exceptions.RPCException,
            StringForm,
            **data1,
        )

        data2 = {}
        self.assertRaises(
            exceptions.RPCException,
            StringForm,
            **data2,
        )


if __name__ == "__main__":
    unittest.main()
