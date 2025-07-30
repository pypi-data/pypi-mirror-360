###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import re
from collections.abc import Iterator
from sys import maxsize as max_int
from typing import Any
from zoneinfo import ZoneInfo

from everysk.core import fields
from everysk.core.datetime.date import date, Date
from everysk.core.datetime.datetime import datetime, DateTime
from everysk.core.exceptions import ReadonlyError, RequiredError, FieldValueError
from everysk.core.object import BaseObject, BaseDict
from everysk.core.unittests import TestCase


class FieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.Field()
        self.assertEqual(field.attr_type, Any)

    def test_vscode_autocomplete(self):
        for cls in fields.Field.__subclasses__():
            self.assertEqual(cls.__new__.__annotations__['return'], cls.attr_type)

    def test_choices_empty(self):
        field = fields.Field(choices=set())
        self.assertEqual(field.choices, set())

    def test_choices_default(self):
        choices = {'a', 'b'}
        with self.assertRaisesRegex(FieldValueError, f"The default value 'c' must be in this list {choices}."):
            fields.Field(default='c', choices=choices)

    def test_choices(self):
        field = fields.Field(choices={'a', 'b'})
        self.assertEqual(field.choices, {'a', 'b'})
        with self.assertRaisesRegex(FieldValueError, f"The value 'c' for field 'banana' must be in this list {field.choices}."):
            field.validate(attr_name='banana', value='c', attr_type=str)


class BoolFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.BoolField()
        self.assertEqual(field.attr_type, bool)

    def test_clean_value_true(self):
        field = fields.BoolField()
        self.assertTrue(field.clean_value(1))
        self.assertTrue(field.clean_value(True))
        self.assertTrue(field.clean_value('y'))
        self.assertTrue(field.clean_value('yes'))
        self.assertTrue(field.clean_value('on'))

    def test_clean_value_false(self):
        field = fields.BoolField()
        self.assertFalse(field.clean_value(0))
        self.assertFalse(field.clean_value(False))
        self.assertFalse(field.clean_value('n'))
        self.assertFalse(field.clean_value('no'))
        self.assertFalse(field.clean_value('off'))

    def test_clean_value_error(self):
        field = fields.BoolField()
        with self.assertRaisesRegex(ValueError, "Invalid truth value 'banana'"):
            field.clean_value('BANANA')

    def test_default_value_readonly(self):
        with self.assertRaisesRegex(RequiredError, 'If field is readonly, then default value is required.'):
            fields.BoolField(default=None, readonly=True)

        fields.BoolField(default=True, readonly=True)
        fields.BoolField(default=False, readonly=True)


class ChoiceFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.ChoiceField(default='1', choices=['1', '2'])
        self.assertEqual(field.attr_type, str)

    def test_validate(self):
        field = fields.ChoiceField(default='1', choices=['1', '2'])
        field.validate(attr_name='test', value='2', attr_type=str)
        self.assertRaises(FieldValueError, field.validate, attr_name='test', value='3', attr_type=str)

    def test_undefined(self):
        # Allow Undefined as a value outside of the list
        field = fields.ChoiceField(default=Undefined, choices=['1', '2'])
        field.validate(attr_name='test', value=Undefined, attr_type=str)

    def test_choices_list(self):
        field = fields.ChoiceField(default='', choices=None)
        self.assertListEqual(field.choices, [])


class DateFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.DateField()
        self.assertEqual(field.attr_type, Date)

    def test_clean_value(self):
        field = fields.DateField()
        self.assertEqual(
            field.clean_value('2022-09-12'),
            Date(year=2022, month=9, day=12)
        )

        self.assertEqual(
            field.clean_value('20220912'),
            Date(year=2022, month=9, day=12)
        )

    def test_validate(self):
        field = fields.DateField()
        field.validate(attr_name='test', value=Date.fromisoformat('2023-01-01'))
        field.validate(attr_name='test', value=date.fromisoformat('2023-01-01'))# pylint: disable=no-member


class DateTimeFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.DateTimeField()
        self.assertEqual(field.attr_type, DateTime)

    def test_clean_value_str(self):
        field = fields.DateTimeField()
        self.assertEqual(
            field.clean_value('2022-09-12T13:00:00+00:00'),
            DateTime(year=2022, month=9, day=12, hour=13, tzinfo=ZoneInfo('UTC'))
        )
        self.assertEqual(
            field.clean_value('2022-09-12 13:00:00+00:00'),
            DateTime(year=2022, month=9, day=12, hour=13, tzinfo=ZoneInfo('UTC'))
        )
        self.assertEqual(
            field.clean_value('2022-09-14'),
            DateTime(year=2022, month=9, day=14, hour=0, tzinfo=ZoneInfo('UTC'))
        )
        self.assertEqual(
            field.clean_value('20220914'),
            DateTime(year=2022, month=9, day=14, hour=0, tzinfo=ZoneInfo('UTC'))
        )
        self.assertEqual(
            field.clean_value('20220914 13:00:00'),
            DateTime(year=2022, month=9, day=14, hour=13, tzinfo=ZoneInfo('UTC'))
        )

    def test_clean_value_str_date(self):
        field = fields.DateTimeField()
        self.assertEqual(
            field.clean_value('2022-09-12'),
            DateTime(year=2022, month=9, day=12, tzinfo=ZoneInfo('UTC'))
        )

    def test_clean_value_date(self):
        field = fields.DateTimeField()
        self.assertEqual(
            field.clean_value(Date(2022, 9, 12)),
            DateTime(year=2022, month=9, day=12, tzinfo=ZoneInfo('UTC'))
        )

    def test_validate(self):
        field = fields.DateTimeField()
        field.validate(attr_name='test', value=DateTime.fromisoformat('2022-09-12T13:00:00+00:00'))
        field.validate(attr_name='test', value=datetime.fromisoformat('2022-09-12T13:00:00+00:00')) # pylint: disable=no-member


class DictFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.DictField()
        self.assertEqual(field.attr_type, dict | BaseDict)

    def test_readonly(self):
        field = fields.DictField(default={'a': 1}, readonly=True)
        self.assertRaises(ReadonlyError, field.default.__setitem__, 'a', 2)
        self.assertRaises(ReadonlyError, field.default.__delitem__, 'a')
        self.assertRaises(ReadonlyError, field.default.pop)
        self.assertRaises(ReadonlyError, field.default.popitem, 'a')
        self.assertRaises(ReadonlyError, field.default.clear)
        self.assertRaises(ReadonlyError, field.default.update, {'a': 2})
        self.assertRaises(ReadonlyError, field.default.setdefault, 'b', 2)
        self.assertDictEqual(field.default, {'a': 1})

    def test_int_keys(self):
        class DictObjectIntKey(BaseObject):
            field = fields.DictField(default={1: 0})

        obj = DictObjectIntKey()
        self.assertEqual(obj.field[1], 0)
        obj.field = {1: 1}
        self.assertEqual(obj.field[1], 1)
        obj.field[1] = 2
        self.assertEqual(obj.field[1], 2)

    def test_int_keys_readonly(self):
        class DictObjectIntKey(BaseObject):
            field = fields.DictField(default={1: 0}, readonly=True)

        obj = DictObjectIntKey()
        self.assertEqual(obj.field[1], 0)

    def test_base_dict(self):
        field = fields.DictField(default=BaseDict(a=1))
        field.default = BaseDict(a=1)
        self.assertEqual(field.default, BaseDict(a=1))


class EmailFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.EmailField()
        self.assertEqual(field.attr_type, str)

    def test_valid_email(self):
        field = fields.EmailField()
        field.validate(attr_name='test', value='fscariott@everysk.com', attr_type=field.attr_type)

    def test_invalid_email(self):
        field = fields.EmailField()
        with self.assertRaisesRegex(FieldValueError, 'Key test must be an e-mail.'):
            field.validate(attr_name='test', value='fscariott.everysk.com', attr_type=field.attr_type)

    def test_invalid_email_with_more_at(self):
        field = fields.EmailField()
        with self.assertRaisesRegex(FieldValueError, 'Key test must be an e-mail.'):
            field.validate(attr_name='test', value='fscariott@everysk@com', attr_type=field.attr_type)


class FloatFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.FloatField()
        self.assertEqual(field.attr_type, float)

    def test_clean_value_str(self):
        field = fields.FloatField()
        self.assertEqual(field.clean_value('1.1'), 1.1)

    def test_clean_value_int(self):
        field = fields.FloatField()
        self.assertEqual(field.clean_value(2), 2.0)

    def test_min_size(self):
        field = fields.FloatField(min_size=1.5, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The value '1' for field 'banana' must be between 1.5 and 2.",
            field.validate,
            attr_name='banana',
            value=1
        )

    def test_max_size(self):
        field = fields.FloatField(min_size=1.5, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The value '2.5' for field 'banana' must be between 1.5 and 2.",
            field.validate,
            attr_name='banana',
            value=2.5
        )

    def test_none(self):
        field = fields.FloatField(min_size=1.5, max_size=2)
        self.assertIsNone(field.validate(attr_name='banana', value=None))


class IntFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.IntField()
        self.assertEqual(field.attr_type, int)

    def test_clean_value(self):
        field = fields.IntField()
        self.assertEqual(field.clean_value('1'), 1)

    def test_min_size(self):
        field = fields.IntField(min_size=1, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The value '0' for field 'banana' must be between 1 and 2.",
            field.validate,
            attr_name='banana',
            value=0
        )

    def test_max_size(self):
        field = fields.IntField(min_size=1, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The value '3' for field 'banana' must be between 1 and 2.",
            field.validate,
            attr_name='banana',
            value=3
        )

    def test_none(self):
        field = fields.IntField(min_size=1.5, max_size=2)
        self.assertIsNone(field.validate(attr_name='banana', value=None))


class IteratorFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.IteratorField()
        self.assertEqual(field.attr_type, Iterator)

    def test_clean_value(self):
        field = fields.IteratorField()
        self.assertIsInstance(field.clean_value('aaa'), Iterator)
        self.assertIsInstance(field.clean_value([0, 1]), Iterator)


class ListFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.ListField()
        self.assertEqual(field.attr_type, list)

    def test_clean_value(self):
        field = fields.ListField()
        self.assertEqual(field.clean_value('aaa'), ['aaa'])
        self.assertEqual(field.clean_value([0, 1]), [0, 1])
        self.assertEqual(field.clean_value(1), 1)
        self.assertEqual(field.clean_value({'a': 1}), {'a': 1})

    def test_max_size_default(self):
        # https://stackoverflow.com/questions/855191/how-big-can-a-python-list-get#comment112727918_15739630
        field = fields.ListField()
        self.assertEqual(field.max_size, max_int / 8)

    def test_max_size(self):
        field = fields.ListField(min_size=1, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The attribute 'banana' is not within the specified list range. min_size: 1 max_size: 2",
            field.validate,
            attr_name='banana',
            value=[1, 2, 3]
        )

    def test_min_size(self):
        field = fields.ListField(min_size=2, max_size=3)
        self.assertRaisesRegex(
            FieldValueError,
            "The attribute 'banana' is not within the specified list range. min_size: 2 max_size: 3",
            field.validate,
            attr_name='banana',
            value=[1]
        )

    def test_min_size_negative(self):
        self.assertRaisesRegex(
            FieldValueError,
            'List min_size cloud not be a negative number.',
            fields.ListField,
            min_size=-1,
            max_size=3
        )

    def test_validate(self):
        field = fields.ListField()
        self.assertRaisesRegex(
            FieldValueError,
            "The 'banana' value must be a list.",
            field.validate,
            attr_name='banana',
            value=1234
        )

    def test_default_choices(self):
        fields.ListField(default=['a'], choices=['a', 'b'])

    def test_default_choices_raise_error(self):
        with self.assertRaises(FieldValueError) as error:
            fields.ListField(default=['c'], choices=['a', 'b'])
        self.assertEqual(error.exception.msg, "The default value '['c']' must be in this list ['a', 'b'].")

    def test_choices(self):
        field = fields.ListField(choices=['a', 'b'])
        field.validate(attr_name='banana', value=['a'])

    def test_choices_raise_error(self):
        field = fields.ListField(choices=['a', 'b'])
        with self.assertRaises(FieldValueError) as error:
            field.validate(attr_name='banana', value=['c'])
        self.assertEqual(error.exception.msg, "The value '['c']' for field 'banana' must be in this list ['a', 'b'].")

    def test_readonly(self):
        field = fields.ListField(default=[9, 1, 2, 3], readonly=True)
        self.assertRaises(ReadonlyError, field.default.__setitem__, 0, 1)
        self.assertRaises(ReadonlyError, field.default.__delitem__, 0)
        self.assertRaises(ReadonlyError, field.default.append, 4)
        self.assertRaises(ReadonlyError, field.default.clear)
        self.assertRaises(ReadonlyError, field.default.extend, [5, 6])
        self.assertRaises(ReadonlyError, field.default.insert, 0, 7)
        self.assertRaises(ReadonlyError, field.default.pop)
        self.assertRaises(ReadonlyError, field.default.remove, 0)
        self.assertRaises(ReadonlyError, field.default.reverse)
        self.assertRaises(ReadonlyError, field.default.sort)
        self.assertListEqual(field.default, [9, 1, 2, 3])

    def test_string_list(self):
        field = fields.ListField(default='a, b,   c,d, e   ')
        self.assertEqual(field.default, ['a', 'b', 'c', 'd', 'e'])
        field = fields.ListField(default='a; b;   c;d; e   ', separator=';')
        self.assertEqual(field.default, ['a', 'b', 'c', 'd', 'e'])


class SetFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.SetField()
        self.assertEqual(field.attr_type, set)

    def test_clean_value(self):
        field = fields.SetField()
        self.assertEqual(field.clean_value({0, 1}), {0, 1})
        self.assertEqual(field.clean_value(1), 1)
        self.assertEqual(field.clean_value({'a': 1}), {'a': 1})

    def test_max_size_default(self):
        # https://stackoverflow.com/questions/855191/how-big-can-a-python-list-get#comment112727918_15739630
        field = fields.SetField()
        self.assertEqual(field.max_size, max_int / 8)

    def test_max_size(self):
        field = fields.SetField(min_size=1, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The attribute 'banana' is not within the specified set range. min_size: 1 max_size: 2",
            field.validate,
            attr_name='banana',
            value={1, 2, 3}
        )

    def test_min_size(self):
        field = fields.SetField(min_size=2, max_size=3)
        self.assertRaisesRegex(
            FieldValueError,
            "The attribute 'banana' is not within the specified set range. min_size: 2 max_size: 3",
            field.validate,
            attr_name='banana',
            value={1}
        )

    def test_min_size_negative(self):
        self.assertRaisesRegex(
            FieldValueError,
            'Set min_size cloud not be a negative number.',
            fields.SetField,
            min_size=-1,
            max_size=3
        )

    def test_validate(self):
        field = fields.SetField()
        self.assertRaisesRegex(
            FieldValueError,
            "Key banana must be <class 'set'>.",
            field.validate,
            attr_name='banana',
            value=1234
        )

    def test_readonly(self):
        field = fields.SetField(default={9, 1, 2, 3}, readonly=True)
        self.assertRaises(ReadonlyError, field.default.__setitem__, 0, 1)
        self.assertRaises(ReadonlyError, field.default.__delitem__, 0)
        self.assertRaises(ReadonlyError, field.default.add, 4)
        self.assertRaises(ReadonlyError, field.default.clear)
        self.assertRaises(ReadonlyError, field.default.discard, 1)
        self.assertRaises(ReadonlyError, field.default.pop)
        self.assertRaises(ReadonlyError, field.default.remove, 1)
        self.assertRaises(ReadonlyError, field.default.update, {1, 4})
        self.assertSetEqual(field.default, {9, 1, 2, 3})

    def test_default_choices(self):
        fields.SetField(default={'a'}, choices={'a', 'b'})

    def test_default_choices_raise_error(self):
        with self.assertRaises(FieldValueError) as error:
            fields.SetField(default={'c'}, choices={'a'})
        self.assertEqual(error.exception.msg, "The default value '{'c'}' must be in this list {'a'}.")

    def test_choices(self):
        field = fields.SetField(choices={'a', 'b'})
        field.validate(attr_name='banana', value={'a'})

    def test_choices_raise_error(self):
        field = fields.SetField(choices={'a'})
        with self.assertRaises(FieldValueError) as error:
            field.validate(attr_name='banana', value={'c'})
        self.assertEqual(error.exception.msg, "The value '{'c'}' for field 'banana' must be in this list {'a'}.")


class StrFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.StrField()
        self.assertEqual(field.attr_type, str)

    def test_max_size(self):
        field = fields.StrField(min_size=1, max_size=2)
        self.assertRaisesRegex(
            FieldValueError,
            "The length '3' for attribute 'banana' must be between '1' and '2'.",
            field.validate,
            attr_name='banana',
            value='abc'
        )

    def test_min_size(self):
        field = fields.StrField(min_size=2, max_size=3)
        self.assertRaisesRegex(
            FieldValueError,
            "The length '1' for attribute 'banana' must be between '2' and '3'.",
            field.validate,
            attr_name='banana',
            value='a'
        )

    def test_min_size_negative(self):
        self.assertRaisesRegex(
            FieldValueError,
            'String min_size cloud not be a negative number.',
            fields.StrField,
            min_size=-1,
            max_size=3
        )

    def test_validate(self):
        field = fields.StrField()
        self.assertRaisesRegex(
            FieldValueError,
            "Key banana must be <class 'str'>.",
            field.validate,
            attr_name='banana',
            value=1234
        )

        field.regex = re.compile('[a-z]')
        with self.assertRaises(FieldValueError) as e:
            field.validate(attr_name='banana', value='1234')
        self.assertEqual("The value '1234' for field 'banana' must match with this regex: [a-z].", e.exception.msg)


class TupleFieldTestCase(TestCase):

    def test_attr_type(self):
        field = fields.TupleField()
        self.assertEqual(field.attr_type, tuple)


class FieldUndefinedClass(BaseObject):
    f01 = fields.BoolField(default=Undefined)
    f02 = fields.ChoiceField(default=Undefined, choices=[Undefined, None])
    f03 = fields.DateField(default=Undefined)
    f04 = fields.DateTimeField(default=Undefined)
    f05 = fields.FloatField(default=Undefined)
    f06 = fields.IntField(default=Undefined)
    f07 = fields.IteratorField(default=Undefined)
    f08 = fields.ListField(default=Undefined)
    f09 = fields.StrField(default=Undefined)
    f10 = fields.TupleField(default=Undefined)


class FieldUndefinedTestCase(TestCase):

    def test_bool_field(self):
        obj = FieldUndefinedClass(f01=Undefined)
        obj.f01 = Undefined

    def test_choice_field(self):
        obj = FieldUndefinedClass(f02=Undefined)
        obj.f02 = Undefined

    def test_date_field(self):
        obj = FieldUndefinedClass(f03=Undefined)
        obj.f03 = Undefined

    def test_datetime_field(self):
        obj = FieldUndefinedClass(f04=Undefined)
        obj.f04 = Undefined

    def test_float_field(self):
        obj = FieldUndefinedClass(f05=Undefined)
        obj.f05 = Undefined

    def test_int_field(self):
        obj = FieldUndefinedClass(f06=Undefined)
        obj.f06 = Undefined

    def test_iterator_field(self):
        obj = FieldUndefinedClass(f07=Undefined)
        obj.f07 = Undefined

    def test_list_field(self):
        obj = FieldUndefinedClass(f08=Undefined)
        obj.f08 = Undefined

    def test_str_field(self):
        obj = FieldUndefinedClass(f09=Undefined)
        obj.f09 = Undefined

    def test_tuple_field(self):
        obj = FieldUndefinedClass(f10=Undefined)
        obj.f10 = Undefined


## https://everysk.atlassian.net/browse/COD-3457
class BaseObjectPropertyInit(BaseObject):
    p1 = fields.IntField()

    @property
    def p2(self) -> int:
        return self.p1

    @p2.setter
    def p2(self, value: int) -> None:
        self.p1 = value

class BaseDictPropertyInit(BaseDict):
    p1 = fields.IntField()

    @property
    def p2(self) -> int:
        return self.p1

    @p2.setter
    def p2(self, value: int) -> None:
        self.p1 = value

class ObjectInitPropertyTestCase(TestCase):

    def test_base_object_normal_attribute(self):
        obj = BaseObjectPropertyInit(p1=1)
        self.assertEqual(obj.p1, 1)
        self.assertEqual(obj.p2, 1)

    def test_base_object_property_attribute(self):
        obj = BaseObjectPropertyInit(p2=2)
        self.assertEqual(obj.p1, 2)
        self.assertEqual(obj.p2, 2)

    def test_base_dict_normal_attribute(self):
        obj = BaseDictPropertyInit(p1=1)
        self.assertEqual(obj.p1, 1)
        self.assertEqual(obj.p2, 1)

    def test_base_dict_property_attribute(self):
        obj = BaseDictPropertyInit(p2=2)
        self.assertEqual(obj.p1, 2)
        self.assertEqual(obj.p2, 2)


# https://everysk.atlassian.net/browse/COD-3770
class COD3770(BaseObject):
    var = fields.DateField(default='2024-01-01')


class COD3770TestCase(TestCase):

    def setUp(self) -> None:
        self.date = Date(2024, 1, 1)

    def test_field_default(self):
        obj = fields.DateField(default='2024-01-01')
        self.assertEqual(obj.default, self.date)

    def test_class_var(self):
        self.assertEqual(COD3770.var, self.date)

    def test_class_var_attribution(self):
        # We create a specific class to not change other tests
        class VarTest(BaseObject):
            var = fields.DateField(default='2024-01-01')

        self.assertEqual(VarTest.var, self.date)
        VarTest.var = '2024-01-02'
        self.assertEqual(VarTest.var, Date(2024, 1, 2))

    def test_instance_var_default(self):
        obj = COD3770()
        self.assertEqual(obj.var, self.date)

    def test_instance_var_attribution(self):
        obj = COD3770()
        obj.var = '2024-01-02'
        self.assertEqual(obj.var, Date(2024, 1, 2))


class URLFieldTestCase(TestCase):

    class ObjectClass(BaseObject):
        url = fields.URLField()

    class DictClass(BaseDict):
        url = fields.URLField()

    def test_http_url(self):
        url = 'http://exampe.com/path?var=1&var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        obj.url = url
        dct['url'] = url
        self.assertEqual(obj.url, dct['url'])

    def test_https_url(self):
        url = 'https://exampe.com/path?var=1&var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        obj.url = url
        dct['url'] = url
        self.assertEqual(obj.url, dct['url'])

    def test_localhost_url(self):
        url = 'http://localhost:8080/path?var=1&var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        obj.url = url
        dct['url'] = url
        self.assertEqual(obj.url, dct['url'])

    def test_not_valid_scheme(self):
        url = 'ttp://localhost:8080/path?var=1&var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            obj.url = url
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            dct['url'] = url

    def test_not_valid_domain(self):
        url = 'http://localhost.host:/path?var=1&var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            obj.url = url
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            dct['url'] = url

    def test_not_valid_query(self):
        url = 'http://localhost:8080/path?var=1 var=2'
        obj = self.ObjectClass()
        dct = self.DictClass()
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            obj.url = url
        with self.assertRaisesRegex(FieldValueError, 'Key url must be an URL.'):
            dct['url'] = url
