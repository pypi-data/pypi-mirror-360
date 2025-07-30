###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
# pylint: disable=protected-access, attribute-defined-outside-init
import pickle
from copy import copy, deepcopy
from typing import Any, Self, Union
from _collections_abc import dict_items, dict_keys, dict_values

from everysk.core.datetime import DateTime, Date
from everysk.core.exceptions import DefaultError, FieldValueError, RequiredError
from everysk.core.fields import BoolField
from everysk.core.object import (
    BaseField, BaseDict, BaseObject, BaseObjectConfig,
    BaseDictConfig, _required, _validate, MetaClass, CLASS_KEY
)
from everysk.core.unittests import TestCase


###############################################################################
#   Required Class Test Case
###############################################################################
class RequiredTestCase(TestCase):

    def test_required(self):
        self.assertRaises(RequiredError, _required, attr_name='Test', value=None)
        self.assertRaises(RequiredError, _required, attr_name='Test', value='')
        self.assertRaises(RequiredError, _required, attr_name='Test', value=())
        self.assertRaises(RequiredError, _required, attr_name='Test', value=[])
        self.assertRaises(RequiredError, _required, attr_name='Test', value={})

###############################################################################
#   Validate Class Test Case
###############################################################################
class ValidateTestCase(TestCase):

    def test_none(self):
        _validate(attr_name='test', value=None, attr_type=Date)
        _validate(attr_name='test', value=None, attr_type=DateTime)
        _validate(attr_name='test', value=None, attr_type=dict)
        _validate(attr_name='test', value=None, attr_type=float)
        _validate(attr_name='test', value=None, attr_type=int)
        _validate(attr_name='test', value=None, attr_type=list)
        _validate(attr_name='test', value=None, attr_type=str)

    def test_undefined(self):
        _validate(attr_name='test', value=Undefined, attr_type=Date)
        _validate(attr_name='test', value=Undefined, attr_type=DateTime)
        _validate(attr_name='test', value=Undefined, attr_type=dict)
        _validate(attr_name='test', value=Undefined, attr_type=float)
        _validate(attr_name='test', value=Undefined, attr_type=int)
        _validate(attr_name='test', value=Undefined, attr_type=list)
        _validate(attr_name='test', value=Undefined, attr_type=str)

    def test_date(self):
        _validate(attr_name='test', value=Date.today(), attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=Date)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=Date)

    def test_datetime(self):
        _validate(attr_name='test', value=DateTime.now(), attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=DateTime)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=DateTime)

    def test_dict(self):
        _validate(attr_name='test', value={}, attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=dict)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=dict)

    def test_float(self):
        _validate(attr_name='test', value=1.0, attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=float)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=float)

    def test_int(self):
        _validate(attr_name='test', value=1, attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=int)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=int)

    def test_list(self):
        _validate(attr_name='test', value=[], attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value='1', attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=list)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=list)

    def test_str(self):
        _validate(attr_name='test', value='1', attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=DateTime.now(), attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=Date.today(), attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1, attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=1.0, attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value=[], attr_type=str)
        self.assertRaises(FieldValueError, _validate, attr_name='test', value={}, attr_type=str)

    def test_any(self):
        _validate(attr_name='test', value=None, attr_type=Any)
        _validate(attr_name='test', value={}, attr_type=Any)
        _validate(attr_name='test', value=[], attr_type=Any)
        _validate(attr_name='test', value=123, attr_type=Any)
        _validate(attr_name='test', value='123', attr_type=Any)
        _validate(attr_name='test', value=callable, attr_type=Any)
        _validate(attr_name='test', value=Undefined, attr_type=Any)
        _validate(attr_name='test', value=Undefined.default_parse_string, attr_type=Any)

    def test_callable(self):
        _validate(attr_name='test', value=lambda x: x, attr_type=callable)
        with self.assertRaisesRegex(FieldValueError, 'Key test must be <built-in function callable>.'):
            _validate(attr_name='test', value='func', attr_type=callable)

    def test_annotation_string(self):
        _validate(attr_name='test', value=object(), attr_type='object')
        with self.assertRaisesRegex(FieldValueError, 'Key test must be object.'):
            _validate(attr_name='test', value=str(), attr_type='object')

    def test_generic_alias(self):
        _validate(attr_name='test', value=[], attr_type=list[str])
        with self.assertRaisesRegex(FieldValueError, r'Key test must be list\[str\].'):
            _validate(attr_name='test', value='a', attr_type=list[str])

    def test_union_type(self):
        _validate(attr_name='test', value=1, attr_type=int | str)
        _validate(attr_name='test', value='1', attr_type=int | str)
        with self.assertRaisesRegex(FieldValueError, 'Key test must be int | str.'):
            _validate(attr_name='test', value=1.0, attr_type=int | str)


###############################################################################
#   BaseField Class Test Case
###############################################################################
class BaseFieldTestCase(TestCase):

    def test_init(self):
        field = BaseField(attr_type=str, default='default', required=True, readonly=True, other='Test')
        self.assertEqual(field.attr_type, str)
        self.assertEqual(field.default, 'default')
        self.assertTrue(field.required)
        self.assertTrue(field.readonly)
        self.assertEqual(field.other, 'Test') # pylint: disable=no-member

    def test_init_default_empty(self):
        self.assertRaises(DefaultError, BaseField, attr_type=str, default=[])
        self.assertRaises(DefaultError, BaseField, attr_type=str, default={})

    def test_init_default_not_empty(self):
        BaseField(attr_type=str, default=[1, 2, 3])
        BaseField(attr_type=str, default={'a': 1, 'b': 2})

    def test_init_readonly_default(self):
        self.assertRaises(RequiredError, BaseField, attr_type=str, readonly=True)

    def test_clean(self):
        field = BaseField(attr_type=str)
        self.assertEqual(field.clean_value('Test'), 'Test')

    def test_transform_to_none(self):
        field = BaseField(attr_type=str, empty_is_none=False)
        self.assertEqual(field.transform_to_none(''), '')
        field = BaseField(attr_type=str, empty_is_none=True)
        self.assertEqual(field.transform_to_none(''), None)

    def test_validate_attr_type(self):
        field = BaseField(attr_type=str)
        self.assertRaises(FieldValueError, field.validate, attr_name='test', value=True)
        self.assertRaises(FieldValueError, field.validate, attr_name='test', value='1', attr_type=int)

    def test_validate_readonly(self):
        field = BaseField(attr_type=str, readonly=True, default='Teste')
        self.assertRaises(FieldValueError, field.validate, attr_name='test', value='new')

    def test_validate_required(self):
        field = BaseField(attr_type=str, required=True)
        self.assertRaises(RequiredError, field.validate, attr_name='test', value=None)
        field = BaseField(default=Undefined, attr_type=int, required=True)
        self.assertRaises(RequiredError, field.validate, attr_name='test', value=None)
        field = BaseField(default=Undefined.default_parse_string, attr_type=int, required=True)
        self.assertRaises(RequiredError, field.validate, attr_name='test', value=None)

    def test_validate_required_lazy(self):
        field = BaseField(attr_type=str, required=False, required_lazy=True)
        field.validate(attr_name='test', value=None)
        field = BaseField(attr_type=int, required=False, required_lazy=True)
        field.validate(attr_name='test', value=Undefined)

    def test_repr(self):
        field = BaseField(attr_type=str)
        self.assertEqual(repr(field), 'BaseField')

    def test_get_value(self):
        def func():
            return 'Test'
        field = BaseField(attr_type=callable)
        self.assertEqual(field.get_value(func), 'Test')

    def test_required_and_required_lazy_error(self):
        self.assertRaisesRegex(
            FieldValueError,
            "Required and required_lazy can't be booth True.",
            BaseField,
            attr_type=str,
            required=True,
            required_lazy=True
        )

    def test_equal(self):
        self.assertEqual(
            BaseField(attr_type=str, default='field'),
            BaseField(attr_type=str, default='field')
        )

    def test_not_equal(self):
        self.assertNotEqual(
            BaseField(attr_type=str, default='field1'),
            BaseField(attr_type=str, default='field2')
        )

    def test_getattr_method(self):
        field = BaseField(attr_type=str)
        self.assertTrue(field.startswith)

    def test_getattr_method_error(self):
        field = BaseField(attr_type=str)
        with self.assertRaisesRegex(AttributeError, "type object 'str' has no attribute 'real'"):
            field.real # pylint: disable=pointless-statement

    def test_getattr_method_union_type(self):
        field = BaseField(attr_type=int | str)
        self.assertTrue(hasattr(field, 'startswith'))
        self.assertTrue(hasattr(field, 'real'))

    def test_getattr_method_union_type_error(self):
        field = BaseField(attr_type=int | str)
        with self.assertRaisesRegex(AttributeError, "type object 'int | str' has no attribute 'update'"):
            field.update # pylint: disable=pointless-statement


###############################################################################
#   Fake class for BaseObject tests.
###############################################################################
class BaseObjectTestClass(BaseObject):
    attr: int = None

###############################################################################
#   BaseObjectFields Test Case
###############################################################################
class BaseObjectFieldsTestClass(BaseObject):
    _private: str = 'Private'
    normal_attr = 'Normal'
    field1 = BaseField(attr_type=int)
    field_default = BaseField(attr_type=int, default=100)
    field_readonly = BaseField(attr_type=str, default='default_value', readonly=True)

###############################################################################
#   Fake class for BaseObject tests.
###############################################################################
class BaseObjectAttributeInheritanceTestClass(BaseObjectFieldsTestClass):
    local_attr = BaseField(attr_type=str, default='Local Field')

class BaseObjectInheritanceTestClass(BaseObjectTestClass):
    attr_other: str = None

class BaseObjectRequiredTestClass(BaseObject):
    required = BaseField(attr_type=int, required=True)
    required1 = BaseField(attr_type=int, required=True)

class BaseObjectRequiredInheritanceTestClass(BaseObjectRequiredTestClass):
    required1 = 1

class BaseObjectRequiredLazyTestClass(BaseObject):
    required = BaseField(attr_type=int, required_lazy=True)
    required1 = BaseField(attr_type=int, required_lazy=True)

class BaseObjectRequiredLazyInheritanceTestClass(BaseObjectRequiredLazyTestClass):
    required1 = 1

class BaseObjectAttributeReplace(BaseObject):
    is_parent = BaseField(attr_type=bool, default=True)

class BaseObjectAttributeReplaceChild(BaseObjectAttributeReplace):
    is_parent = False

class BaseFieldClean(BaseField):

    def clean_value(self, value: Any) -> Any:
        if value not in (None, int):
            raise FieldValueError('Error')

class BaseObjectCleanValueError(BaseObject):
    field1 = BaseFieldClean(attr_type=int)

# Fake class for BaseObject
class BaseObjectTestInitClass(BaseObject):
    def __init__(self, **kwargs: dict) -> None:
        raise AttributeError

###############################################################################
#   BaseObject Test Case
###############################################################################
class BaseObjectTestCase(TestCase):

    def test_init(self):
        obj = BaseObjectTestClass()
        self.assertIsNone(obj.attr)

    def test_init_error_handler(self):
        obj = BaseObjectTestInitClass(silent=True)

        self.assertIsInstance(obj, BaseObject)
        self.assertIsNone(obj._errors['after_init'])
        self.assertIsNone(obj._errors['before_init'])
        self.assertIsInstance(obj._errors['init'], AttributeError)

    def test_attr_creation(self):
        obj = BaseObjectTestClass()
        obj.attr = 1
        self.assertEqual(obj.attr, 1)

    def test_fields(self):
        obj = BaseObjectFieldsTestClass()
        self.assertEqual(obj._private, 'Private')
        self.assertEqual(obj.normal_attr, 'Normal')
        self.assertIsNone(obj.field1)
        self.assertEqual(obj.field_default, 100)
        self.assertEqual(obj.field_readonly, 'default_value')
        self.assertRaises(FieldValueError, BaseObjectFieldsTestClass, field_readonly='Changed')
        with self.assertRaisesRegex(FieldValueError, "The field 'field_readonly' value cannot be changed."):
            obj.field_readonly = 'Changed'

    def test_required(self):
        self.assertRaises(RequiredError, BaseObjectRequiredTestClass)

    def test_required_inheritance(self):
        self.assertRaisesRegex(RequiredError, 'The required attribute is required.', BaseObjectRequiredInheritanceTestClass)
        obj = BaseObjectRequiredInheritanceTestClass(required=2)
        self.assertEqual(obj.required, 2)
        self.assertEqual(obj.required1, 1)

    def test_required_lazy(self):
        obj = BaseObjectRequiredLazyTestClass()
        self.assertRaisesRegex(
            RequiredError,
            'The required attribute is required.',
            obj.validate_required_fields
        )

    def test_required_lazy_inheritance(self):
        obj = BaseObjectRequiredLazyInheritanceTestClass()
        self.assertRaisesRegex(
            RequiredError,
            'The required attribute is required.',
            obj.validate_required_fields
        )
        obj.required = 2
        obj.validate_required_fields()
        self.assertEqual(obj.required, 2)
        self.assertEqual(obj.required1, 1)

    def test_default_receive_none(self):
        obj = BaseObjectFieldsTestClass(field_default=None)
        self.assertEqual(obj.field_default, None)

    def test_attribute_change_bool_type(self):
        parent = BaseObjectAttributeReplace()
        self.assertTrue(parent.is_parent)
        child = BaseObjectAttributeReplaceChild()
        self.assertFalse(child.is_parent)

    def test_get_attribute_class(self):
        self.assertEqual(BaseObjectFieldsTestClass.field_default, 100)

    def test_get_attribute_inheritance_class(self):
        self.assertEqual(BaseObjectAttributeInheritanceTestClass.local_attr, 'Local Field')
        self.assertEqual(BaseObjectAttributeInheritanceTestClass.field_readonly, 'default_value')

    def test_get_attribute_class_error(self):
        with self.assertRaisesRegex(AttributeError, "type object 'BaseObjectFieldsTestClass' has no attribute 'field_default_erro'"):
            BaseObjectFieldsTestClass.field_default_erro # pylint: disable=pointless-statement, no-member

    def test_get_clean_value(self):
        obj = BaseObjectFieldsTestClass()
        self.assertIsNone(obj.field1)
        obj.field1 = 21
        self.assertEqual(obj.field1, 21)

    def test_get_clean_value_error(self):
        with self.assertRaisesRegex(FieldValueError, 'field1: Error'):
            BaseObjectCleanValueError(field1='21')

    def test_del_attribute(self):
        obj = BaseObject(attr1=1)
        self.assertEqual(obj.attr1, 1)
        del obj.attr1
        with self.assertRaisesRegex(AttributeError, "'BaseObject' object has no attribute 'attr1'"):
            obj.attr1 # pylint: disable=pointless-statement

    def test_del_private_attribute(self):
        obj = BaseObject(_attr1=1)
        self.assertEqual(obj._attr1, 1)
        del obj._attr1
        with self.assertRaisesRegex(AttributeError, "'BaseObject' object has no attribute '_attr1'"):
            obj._attr1 # pylint: disable=pointless-statement

    def test_copy(self):
        obj1 = BaseObject(_private=1, public=2)
        obj2 = copy(obj1)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertEqual(obj1.public, obj2.public)

    def test_copy_config(self):
        obj1 = BaseObject()
        obj1._config = deepcopy(obj1._config)
        obj1._config.new_field = 'string'
        obj2 = copy(obj1)
        self.assertEqual(BaseObject._config, obj2._config)

    def test_deepcopy(self):
        obj1 = BaseObject(_private=1, public=2)
        obj2 = deepcopy(obj1)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertEqual(obj1.public, obj2.public)

    def test_deepcopy_config(self):
        obj1 = BaseObject()
        obj1._config = deepcopy(obj1._config)
        obj1._config.new_field = 'string'
        obj2 = deepcopy(obj1)
        self.assertEqual(BaseObject._config, obj2._config)

    def test_replace(self):
        obj1 = BaseObject(_private=1, public=2)
        obj2 = obj1.replace(_private=3, public=4)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj2._private, 3)
        self.assertEqual(obj2.public, 4)

    def test_replace_config(self):
        obj1 = BaseObject(_private=1, public=2)
        obj1._config = deepcopy(obj1._config)
        obj1._config.new_field = 'string'
        obj2 = obj1.replace(_private=3, public=4)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj2._private, 3)
        self.assertEqual(obj2.public, 4)

    def test_get_state(self):
        obj1 = BaseObject(date=Date(2024, 1, 1))
        obj1._config = deepcopy(obj1._config)
        the_pickle = pickle.loads(pickle.dumps(obj1))

        self.assertEqual(the_pickle.__dict__, {'_errors': None, '_is_frozen': False, '_silent': False, 'date': Date(2024, 1, 1)})

    def test_get_state_raises_key_error_pass(self):
        obj = BaseObject(public={'key': 'value'})
        pickle_element = pickle.loads(pickle.dumps(obj))

        self.assertDictEqual(pickle_element.__dict__['public'], {'key': 'value'})
        self.assertDictEqual(obj.__dict__, {'public': {'key': 'value'}})

    def test_pickle_with_data(self):
        obj = FakeObjectWithAttr(var1="test1", var2="test2")
        ret = pickle.loads(pickle.dumps(obj))

        self.assertIsInstance(obj, type(ret))
        for key in obj.__get_attributes__().keys():
            self.assertTrue(hasattr(ret, key))
            self.assertIsInstance(getattr(obj, key), type(getattr(ret, key)))
            self.assertEqual(getattr(obj, key), getattr(ret, key))

    def test_pickle_empty(self):
        obj = FakeObjectWithAttr()
        ret = pickle.loads(pickle.dumps(obj))

        self.assertIsInstance(obj, type(ret))
        for key in obj.__get_attributes__().keys():
            self.assertTrue(hasattr(ret, key))
            self.assertIsInstance(getattr(obj, key), type(getattr(ret, key)))
            self.assertEqual(getattr(obj, key), getattr(ret, key))

    def test_pickle_private(self):
        obj = FakeObjectWithAttr(_private=1)
        ret = pickle.loads(pickle.dumps(obj))

        self.assertIsInstance(obj, type(ret))
        for key in obj.__get_attributes__().keys():
            self.assertTrue(hasattr(ret, key))
            self.assertIsInstance(getattr(obj, key), type(getattr(ret, key)))
            self.assertEqual(getattr(obj, key), getattr(ret, key))

    def test_to_dict(self):
        obj = BaseObject(_private=1, public=2, obj=BaseObject(attr=1))
        self.assertDictEqual(obj.to_dict(), {'_private': 1, 'public': 2, 'obj': obj.obj})

    def test_to_dict_recursive(self):
        obj = BaseObject(_private=1, public=2, obj=BaseObject(attr=1))
        self.assertDictEqual(obj.to_dict(recursion=True), {'_private': 1, 'public': 2, 'obj': {'attr': 1}})

    def test_to_dict_class(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(
            obj.to_dict(add_class_path=True),
            {
                CLASS_KEY: 'everysk.core.object.BaseDict',
                '_errors': None,
                '_is_frozen': False,
                '_silent': False,
                '_private': 1,
                'public': 2,
                'obj': obj.obj
            }
        )

    def test_to_dict_no_class(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(
            obj.to_dict(add_class_path=False),
            {
                '_private': 1,
                'public': 2,
                'obj': obj.obj
            }
        )

    def test_to_dict_class_defined(self):
        obj = BaseObjectTestClass(attr2=2)
        # The fields with default value does not need to go to the dictionary
        self.assertDictEqual(obj.to_dict(), {'attr2': 2})

    def test_to_dict_exclude_keys(self):
        class TestClass(BaseObject):
            class Config(BaseObjectConfig):
                exclude_keys: set = {'attr'}
            attr: int = 1
            var: str = 2

        obj = TestClass()
        self.assertDictEqual(
            obj.to_dict(add_class_path=True),
            {
                '__class_path__': 'everysk.core._tests.object.TestClass',
                '_errors': None,
                '_is_frozen': False,
                '_silent': False,
                'var': 2
            }
        )

    def test_to_dict_exclude_keys_readonly(self):
        class TestClass(BaseObject):
            attr = BaseField(attr_type=int, default=1, readonly=True)
            var: str = 2

        obj = TestClass()
        self.assertDictEqual(
            obj.to_dict(add_class_path=True),
            {
                '__class_path__': 'everysk.core._tests.object.TestClass',
                '_errors': None,
                '_is_frozen': False,
                '_silent': False,
                'var': 2
            }
        )


    def test_need_validation(self):
        obj = BaseObjectTestClass()
        with self.assertRaisesRegex(FieldValueError, "Key attr must be <class 'int'>."):
            obj.attr = 'a'
        obj._need_validation = False
        obj.attr = 'a'


## Fake class for BaseDict tests.
class BaseDictTestClass(BaseDict):
    attr: int = None
    field = BaseField(attr_type=str)

class BaseDictFieldsTestClass(BaseDict):
    _private: str = 'Private'
    normal_attr = 'Normal'
    field1 = BaseField(attr_type=int)
    field_default = BaseField(attr_type=int, default=100)
    field_readonly = BaseField(attr_type=str, default='default_value', readonly=True)

class BaseDictInheritanceTestClass(BaseDictTestClass):
    attr_other: str = None

class BaseDictRequiredTestClass(BaseDict):
    required = BaseField(attr_type=int, required=True)

class BaseDictRequiredLazyTestClass(BaseDict):
    normal: bool = True
    required = BaseField(attr_type=int, required_lazy=True)

class BaseDictBoolTestClass(BaseDict):
    attr = BoolField()

class FrozenBaseDict(BaseDict):
    class Config(BaseDictConfig):
        keys_blacklist: list = ['invalid']

class BaseDictUndefinedTestClass(BaseDict):
    attr = BaseField(default=Undefined, attr_type=str)

class FakeNPArray:
    def __eq__(self, obj: Any) -> bool:
        raise ValueError('The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()')

class BaseDictNpArrayTestCase(BaseDict):
    attr: FakeNPArray = None

class NpArrayTestCase(TestCase):

    def test_equal_raise(self):
        obj = FakeNPArray()
        with self.assertRaisesRegex(ValueError, r'The truth value of an array with more than one element is ambiguous. Use a.any\(\) or a.all\(\)'):
            assert obj == ''

    def test_set_value(self):
        fake_np_array = FakeNPArray()

        obj = BaseDictNpArrayTestCase()
        obj.attr = fake_np_array
        self.assertIsNotNone(obj.attr)
        self.assertIsNotNone(obj['attr'])

        obj = BaseDictNpArrayTestCase(attr=fake_np_array)
        self.assertIsNotNone(obj.attr)
        self.assertIsNotNone(obj['attr'])

###############################################################################
#   BaseDict Test Case Implementation
###############################################################################
class BaseDictTestCase(TestCase):

    def test_init(self):
        obj = BaseDictTestClass()
        self.assertIsNone(obj.attr)
        self.assertIsNone(obj['field'])

    def test_attr_creation(self):
        obj = BaseDictTestClass()
        obj.attr = 1
        self.assertEqual(obj.attr, 1)
        self.assertEqual(obj['attr'], 1)
        obj['attr2'] = 10
        self.assertEqual(obj.attr2, 10) # pylint: disable=no-member
        self.assertEqual(obj['attr2'], 10)

    def test_fields(self):
        obj = BaseDictFieldsTestClass()
        self.assertEqual(obj._private, 'Private')
        self.assertEqual(obj.normal_attr, 'Normal')
        self.assertIsNone(obj.field1)
        self.assertIsNone(obj['field1'])
        self.assertEqual(obj.field_default, 100)
        self.assertEqual(obj['field_default'], 100)
        self.assertEqual(obj.field_readonly, 'default_value')
        self.assertEqual(obj['field_readonly'], 'default_value')
        self.assertRaises(FieldValueError, BaseDictFieldsTestClass, field_readonly='Changed')
        with self.assertRaisesRegex(FieldValueError, "The field 'field_readonly' value cannot be changed."):
            obj.field_readonly = 'Changed'
        with self.assertRaisesRegex(FieldValueError, "The field 'field_readonly' value cannot be changed."):
            obj['field_readonly'] = 'Changed'

    def test_private_attr(self):
        obj = BaseDictFieldsTestClass()
        self.assertNotIn('_private', obj)
        obj._other = 1
        self.assertNotIn('_other', obj)
        self.assertEqual(obj._other, 1)
        with self.assertRaisesRegex(KeyError, "Keys can't start with '_'"):
            obj['_other'] = 1

    def test_update(self):
        obj = BaseDictTestClass()
        self.assertIsNone(obj.attr)
        self.assertIsNone(obj['field'])
        obj.update({'attr': 1, 'field': 'a', 'attr2': 2})
        self.assertEqual(obj.attr, 1)
        self.assertEqual(obj['attr'], 1)
        self.assertEqual(obj.attr2, 2) # pylint: disable=no-member
        self.assertEqual(obj['attr2'], 2)
        self.assertRaises(FieldValueError, obj.update, {'attr': '1', 'attr2': 2})

    def test_update_raises_key_error(self):
        with self.assertRaises(KeyError) as context:
            obj = BaseDictTestClass()
            obj.update({'_private': 1})

        self.assertEqual(str(context.exception), '\'The key cannot be called "_private".\'')

    def test_required(self):
        self.assertRaises(RequiredError, BaseDictRequiredTestClass)

    def test_required_lazy(self):
        obj = BaseDictRequiredLazyTestClass()
        self.assertRaisesRegex(
            RequiredError,
            'The required attribute is required.',
            obj.validate_required_fields
        )

    def test_default_receive_none(self):
        obj = BaseDictFieldsTestClass(field_default=None)
        self.assertEqual(obj.field_default, None)
        self.assertEqual(obj['field_default'], None)

    def test_value_persist_on_error(self):
        obj = BaseDictFieldsTestClass()
        try:
            obj['field_readonly'] = 'Changed'
        except FieldValueError:
            pass
        self.assertEqual(obj.field_readonly, 'default_value')
        self.assertEqual(obj['field_readonly'], 'default_value')

    def test_clean_value(self):
        base = BaseDictBoolTestClass(attr=1)
        # check clean value changed to bool True
        self.assertTrue(base.attr is True)
        self.assertTrue(base['attr'] is True)

        base = BaseDictBoolTestClass()
        base.attr = 1
        self.assertTrue(base.attr is True)
        self.assertTrue(base['attr'] is True)

        base = BaseDictBoolTestClass()
        base['attr'] = 1
        self.assertTrue(base.attr is True)
        self.assertTrue(base['attr'] is True)

    def test_del_attribute(self):
        obj = BaseDict(attr1=1)
        self.assertEqual(obj['attr1'], 1)
        self.assertEqual(obj.attr1, 1)
        del obj.attr1
        with self.assertRaisesRegex(KeyError, "'attr1'"):
            obj['attr1'] # pylint: disable=pointless-statement

        with self.assertRaisesRegex(AttributeError, "'BaseDict' object has no attribute 'attr1'"):
            obj.attr1 # pylint: disable=pointless-statement

    def test_del_private_attribute(self):
        obj = BaseDict(_attr1=1)
        # Private attributes don't turn into keys
        with self.assertRaisesRegex(KeyError, "'_attr1'"):
            obj['_attr1'] # pylint: disable=pointless-statement

        self.assertEqual(obj._attr1, 1)
        del obj._attr1
        with self.assertRaisesRegex(KeyError, "'_attr1'"):
            obj['_attr1'] # pylint: disable=pointless-statement

        with self.assertRaisesRegex(AttributeError, "'BaseDict' object has no attribute '_attr1'"):
            obj._attr1 # pylint: disable=pointless-statement

    def test_del_key(self):
        obj = BaseDict(attr1=1)
        self.assertEqual(obj['attr1'], 1)
        self.assertEqual(obj.attr1, 1)
        del obj['attr1']
        with self.assertRaisesRegex(KeyError, "'attr1'"):
            obj['attr1'] # pylint: disable=pointless-statement

        with self.assertRaisesRegex(AttributeError, "'BaseDict' object has no attribute 'attr1'"):
            obj.attr1 # pylint: disable=pointless-statement

    def test_get_attribute_raises_error(self):
        with self.assertRaises(AttributeError) as context:
            obj = BaseDict()
            obj.__getattr__('__data__') # pylint: disable=unnecessary-dunder-call

        self.assertEqual(str(context.exception), "'BaseDict' object has no attribute '__data__'.")

    def test_fromkeys(self):
        obj = BaseDict(_private=1, public=2, excluded=3)
        dct = obj.fromkeys(['public', 'new'], 4)
        self.assertEqual(obj._private, dct._private)
        self.assertEqual(obj.public, dct.public)
        self.assertEqual(obj['public'], dct['public'])
        self.assertEqual(dct.new, 4)
        self.assertEqual(dct['new'], 4)

    def test_clear(self):
        # pylint: disable=no-member
        obj = BaseDict(_private=1, public=2)
        self.assertDictEqual(obj.__dict__, {'_private': 1, 'public': 2})
        self.assertEqual(obj._private, 1)
        self.assertEqual(obj.public, 2)
        obj.clear()
        self.assertDictEqual(obj, {})
        self.assertEqual(obj._private, 1)
        self.assertFalse(hasattr(obj, 'public'))

    def test_self_copy(self):
        obj1 = BaseDict(_private=1, public=2)
        obj2 = obj1.copy()
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)

    def test_copy(self):
        obj1 = BaseDict(_private=1, public=2)
        obj2 = copy(obj1)
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)

    def test_deepcopy(self):
        obj1 = BaseDict(_private=1, public=2)
        obj2 = deepcopy(obj1)
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)

    def test_pop(self):
        obj = BaseDict(_private=1, public=2)
        self.assertEqual(obj.pop('public'), 2)
        self.assertEqual(obj.pop('public', 4), 4)
        with self.assertRaisesRegex(KeyError, 'public'):
            obj.pop('public')

    def test_popitem(self):
        obj = BaseDict(_private=1, public=2)
        self.assertEqual(obj.popitem(), ('public', 2))
        with self.assertRaisesRegex(KeyError, r'popitem\(\)\: dictionary is empty'):
            obj.popitem()

    def test_replace(self):
        obj1 = BaseDict(_private=1, public=2)
        obj2 = obj1.replace(_private=3, public=4)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj2._private, 3)
        self.assertEqual(obj2.public, 4)
        self.assertEqual(obj2['public'], 4)

    def test_init_with_undefined(self):
        obj = BaseDictUndefinedTestClass(attr='foo')
        self.assertEqual(obj.attr, 'foo')
        self.assertEqual(obj['attr'], 'foo')
        obj = BaseDictUndefinedTestClass(attr=Undefined.default_parse_string)
        self.assertEqual(obj.attr, Undefined)
        self.assertEqual(obj['attr'], Undefined)
        obj = BaseDictUndefinedTestClass(attr=Undefined)
        self.assertEqual(obj.attr, Undefined)
        self.assertEqual(obj['attr'], Undefined)
        obj = BaseDictUndefinedTestClass(attr=None)
        self.assertEqual(obj.attr, None)
        self.assertEqual(obj['attr'], None)

    def test_set_undefined(self):
        obj = BaseDictUndefinedTestClass()
        obj.attr = Undefined.default_parse_string
        self.assertEqual(obj.attr, Undefined)
        self.assertEqual(obj['attr'], Undefined)

        obj.attr = Undefined
        self.assertEqual(obj.attr, Undefined)
        self.assertEqual(obj['attr'], Undefined)

    def test_len(self):
        obj = BaseDict(_private=1, public=2)
        self.assertEqual(len(obj), 1)

    def test_getitem(self):
        obj = BaseDict(_private=1, public=2)
        self.assertEqual(obj['public'], 2)
        self.assertEqual(obj['public'], obj.public)
        self.assertRaisesRegex(KeyError, 'foo', obj.__getitem__, 'foo')
        self.assertRaisesRegex(KeyError, '_private', obj.__getitem__, '_private')

    def test_repr(self):
        obj = BaseDict(_private=1, public=2)
        self.assertEqual(repr(obj), "{'public': 2}")

    def test_or(self):
        # pylint: disable=unnecessary-dunder-call
        obj = BaseDict(_private=1, public=2)

        ret = obj | {'public': 3}
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 1, 'public': 3})

        ret = obj | {'public': 3, 'new': 4}
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 1, 'new': 4, 'public': 3, })

        ret = obj | BaseDict(_private=2, public=3, new=4)
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 2, 'public': 3, 'new': 4})

        self.assertEqual(obj.__or__(1), NotImplemented)

    def test_ror(self):
        # pylint: disable=protected-access, unnecessary-dunder-call
        obj = BaseDict(_private=1, public=2)

        ret = {'public': 3} | obj
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 1, 'public': 2})

        ret = {'public': 3, 'new': 4} | obj
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 1, 'public': 2, 'new': 4})

        ret = obj.__ror__(BaseDict(_private=2, public=3, new=4))
        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret.__dict__, {'_private': 1, 'public': 2, 'new': 4})

        self.assertEqual(obj.__ror__(1), NotImplemented)

    def test_ior(self):
        # pylint: disable=no-member
        obj = BaseDict(_private=1, public=2)

        obj |= {'public': 3}
        self.assertIsInstance(obj, BaseDict)
        self.assertDictEqual(obj.__dict__, {'_private': 1, 'public': 3})

        obj |= {'public': 3, 'new': 4}
        self.assertIsInstance(obj, BaseDict)
        self.assertDictEqual(obj.__dict__, {'_private': 1, 'public': 3, 'new': 4})

        obj |= BaseDict(_private=2, public=3, new=4)
        self.assertIsInstance(obj, BaseDict)
        self.assertDictEqual(obj.__dict__, {'_private': 2, 'public': 3, 'new': 4})

    def test_setstate(self):
        obj = BaseDict(_private=1, public=2)
        ret = pickle.loads(pickle.dumps(obj))

        self.assertIsInstance(ret, BaseDict)
        self.assertDictEqual(ret, obj)
        self.assertDictEqual(
            ret.__dict__,
            {'_errors': None, '_is_frozen': False, '_private': 1, '_silent': False, 'public': 2}
        )

    def test_setitem_raises_error_keys_blacklist(self):
        with self.assertRaises(KeyError) as context:
            a = FrozenBaseDict(invalid=1)
            a['invalid'] = 2

        self.assertEqual(str(context.exception), '\'The key cannot be called "invalid".\'')

    def test_attribute_before_init(self):
        class Test(BaseDict):
            def __init__(self, **kwargs) -> None:
                self.field = 1
                super().__init__(**kwargs)

        obj = Test()
        self.assertEqual(obj.field, 1)

    def test_iteration(self):
        obj = BaseDict(a=1, b=2)
        self.assertListEqual(list(obj), ['a', 'b'])

    def test_need_validation(self):
        obj = BaseDictTestClass()
        with self.assertRaisesRegex(FieldValueError, "Key attr must be <class 'int'>."):
            obj['attr'] = 'a'
        obj._need_validation = False
        obj['attr'] = 'a'

    def test_to_dict(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(obj.to_dict(), {'_private': 1, 'public': 2, 'obj': obj.obj})

    def test_to_dict_recursive(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(obj.to_dict(recursion=True), {'_private': 1, 'public': 2, 'obj': {'attr': 1}})

    def test_to_dict_class(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(
            obj.to_dict(add_class_path=True),
            {
                CLASS_KEY: 'everysk.core.object.BaseDict',
                '_errors': None,
                '_is_frozen': False,
                '_silent': False,
                '_private': 1,
                'public': 2,
                'obj': obj.obj
            }
        )

    def test_to_dict_no_class(self):
        obj = BaseDict(_private=1, public=2, obj=BaseDict(attr=1))
        self.assertDictEqual(
            obj.to_dict(add_class_path=False),
            {
                '_private': 1,
                'public': 2,
                'obj': obj.obj
            }
        )

    def test_to_dict_class_defined(self):
        obj = BaseDictTestClass(attr2=2)
        # The fields with default value that not are privates goes to the dictionary
        self.assertDictEqual(obj.to_dict(), {'attr': None, 'attr2': 2, 'field': None})


class BaseDictProperty(BaseDict):
    _to_date = BaseField(attr_type=str)

    @property
    def to_date(self):
        return self._to_date

    @to_date.setter
    def to_date(self, value):
        self._to_date = value

class BaseDictPropertyInherit(BaseDictProperty):
    pass


class BaseDictPropertyTestCase(TestCase):

    def test_property_setattr_init(self):
        obj = BaseDictProperty(to_date='Test')
        self.assertEqual(obj.to_date, 'Test')
        self.assertEqual(obj._to_date, 'Test')
        self.assertNotIn('to_date', obj)

    def test_property_setattr(self):
        obj = BaseDictProperty()
        obj.to_date = 'Test'
        self.assertEqual(obj.to_date, 'Test')
        self.assertEqual(obj._to_date, 'Test')
        self.assertNotIn('to_date', obj)

    def test_property_setitem(self):
        obj = BaseDictProperty()
        obj['to_date'] = 'Test'
        self.assertEqual(obj.to_date, 'Test')
        self.assertEqual(obj._to_date, 'Test')
        self.assertNotIn('to_date', obj)


class TestBaseObjectConfig(BaseObject):
    class Config:
        value: int = 1

class TestBaseDictConfig(BaseDict):
    class Config(BaseDictConfig):
        value: int = 1

    _config: Config = None

class TestConfigClass1(BaseObject):
    class Config:
        pass

class TestConfigClass2(TestConfigClass1):
    pass

class MetaClassConfigTestCase(TestCase):

    def setUp(self) -> None:
        # pylint: disable=no-member
        TestBaseObjectConfig._config.value = 1
        TestBaseDictConfig._config.value = 1

    def test_object_config_attribute(self):
        # pylint: disable=no-member
        self.assertEqual(TestBaseObjectConfig._config.value, 1)
        obj = TestBaseObjectConfig()
        self.assertEqual(obj._config.value, TestBaseObjectConfig._config.value)

    def test_object_config_singleton(self):
        # pylint: disable=no-member
        obj = TestBaseObjectConfig()
        obj._config.value = 3
        self.assertEqual(TestBaseObjectConfig._config.value, 3)
        self.assertEqual(obj._config.value, TestBaseObjectConfig._config.value)

    def test_object_config_delete(self):
        obj = TestBaseObjectConfig()
        with self.assertRaisesRegex(AttributeError, "type object 'TestBaseObjectConfig' has no attribute 'Config'"):
            TestBaseObjectConfig.Config # pylint: disable=pointless-statement

        with self.assertRaisesRegex(AttributeError, "'TestBaseObjectConfig' object has no attribute 'Config'"):
            obj.Config # pylint: disable=pointless-statement

    def test_dict_config_attribute(self):
        self.assertEqual(TestBaseDictConfig._config.value, 1)
        obj = TestBaseDictConfig()
        self.assertEqual(obj._config.value, TestBaseDictConfig._config.value)

    def test_dict_config_singleton(self):
        obj = TestBaseDictConfig()
        obj._config.value = 3
        self.assertEqual(TestBaseDictConfig._config.value, 3)
        self.assertEqual(obj._config.value, TestBaseDictConfig._config.value)

    def test_dict_config_delete(self):
        obj = TestBaseDictConfig()
        with self.assertRaisesRegex(AttributeError, "type object 'TestBaseDictConfig' has no attribute 'Config'"):
            TestBaseDictConfig.Config # pylint: disable=pointless-statement

        with self.assertRaisesRegex(AttributeError, "'TestBaseDictConfig' object has no attribute 'Config'"):
            obj.Config # pylint: disable=pointless-statement

    def test_dict_config_no_key(self):
        obj = TestBaseDictConfig()
        with self.assertRaisesRegex(KeyError, 'config'):
            obj['config'] # pylint: disable=pointless-statement

    def test_dict_config_attribute_copy(self):
        obj1 = TestBaseDictConfig()
        obj1._config = copy(obj1._config)
        obj1._config.value = 2
        obj2 = TestBaseDictConfig()
        obj3 = TestBaseDictConfig(**obj1)
        self.assertNotEqual(obj1._config, obj2._config)
        self.assertNotEqual(obj1._config, obj3._config)
        self.assertEqual(obj1._config.value, 2)
        self.assertEqual(obj2._config.value, 1)
        self.assertEqual(obj3._config.value, 1)

    def test_return_self(self):
        self.assertDictEqual(
            MetaClass.__call__.__annotations__,
            {'args': tuple, 'kwargs': dict, 'return': Self}
        )

        self.assertDictEqual(
            MetaClass.__new__.__annotations__,
            {'name': str, 'bases': tuple, 'attrs': dict, 'return': Self}
        )

    def test_config_inheritance(self):
        self.assertNotEqual(TestConfigClass1._config, TestConfigClass2._config)


class FrozenObject(BaseObject):
    class Config:
        frozen: bool = True


class FrozenObjectTestCase(TestCase):
    # pylint: disable=no-member
    def setUp(self) -> None:
        self.message = 'Class everysk.core._tests.object.FrozenObject is frozen and cannot be modified.'

    def test_create(self):
        obj = FrozenObject(attr=1, attr2='Banana')
        self.assertEqual(obj.attr, 1)
        self.assertEqual(obj.attr2, 'Banana')

    def test_delete(self):
        obj = FrozenObject(attr=1)
        with self.assertRaisesRegex(AttributeError, self.message):
            del obj.attr

    def test_create_new_attribute(self):
        obj = FrozenObject(attr=1)
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.attr2 = 2

    def test_create_update_attribute(self):
        obj = FrozenObject(attr=1)
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.attr = 2

    def test_copy(self):
        obj1 = FrozenObject(_private=1, public=2)
        obj2 = copy(obj1)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertEqual(obj1.public, obj2.public)
        self.assertTrue(obj1._is_frozen)
        self.assertTrue(obj2._is_frozen)

    def test_deepcopy(self):
        obj1 = FrozenObject(_private=1, public=2)
        obj2 = deepcopy(obj1)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertEqual(obj1.public, obj2.public)
        self.assertTrue(obj1._is_frozen)
        self.assertTrue(obj2._is_frozen)

    def test_replace(self):
        obj1 = FrozenObject(_private=1, public=2)
        obj2 = obj1.replace(_private=3, public=4)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj2._private, 3)
        self.assertEqual(obj2.public, 4)
        self.assertTrue(obj2._is_frozen)


class FrozenDict(BaseDict):
    class Config(BaseDictConfig):
        frozen: bool = True


class FrozenDictTestCase(TestCase):
    def setUp(self) -> None:
        self.message = 'Class everysk.core._tests.object.FrozenDict is frozen and cannot be modified.'

    def test_create(self):
        obj = FrozenDict(attr=1, attr2='Banana')
        self.assertEqual(obj.attr, 1)
        self.assertEqual(obj.attr2, 'Banana')
        self.assertEqual(obj['attr'], 1)
        self.assertEqual(obj['attr2'], 'Banana')

    def test_delete(self):
        obj = FrozenDict(attr=1, attr2='Banana')
        with self.assertRaisesRegex(AttributeError, self.message):
            del obj.attr

        with self.assertRaisesRegex(AttributeError, self.message):
            del obj['attr2']

    def test_create_new_attribute(self):
        obj = FrozenDict()
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.attr = 2

        with self.assertRaisesRegex(AttributeError, self.message):
            obj['attr'] = 2

    def test_create_update_attribute(self):
        obj = FrozenDict(attr=1, attr2='Banana')
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.attr = 2

        with self.assertRaisesRegex(AttributeError, self.message):
            obj['attr'] = 2

    def test_clear(self):
        obj = FrozenDict(attr=1, attr2='Banana')
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.clear()

    def test_self_copy(self):
        obj1 = FrozenDict(_private=1, public=2)
        obj2 = obj1.copy()
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertTrue(obj2.__dict__['_is_frozen'])
        self.assertTrue(obj1._is_frozen)
        self.assertTrue(obj2._is_frozen)

    def test_copy(self):
        obj1 = FrozenDict(_private=1, public=2)
        obj2 = copy(obj1)
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertTrue(obj2.__dict__['_is_frozen'])
        self.assertTrue(obj1._is_frozen)
        self.assertTrue(obj2._is_frozen)

    def test_deepcopy(self):
        obj1 = FrozenDict(_private=1, public=2)
        obj2 = deepcopy(obj1)
        self.assertDictEqual(obj1, obj2)
        self.assertEqual(obj1._private, obj2._private)
        self.assertTrue(obj2.__dict__['_is_frozen'])
        self.assertTrue(obj1._is_frozen)
        self.assertTrue(obj2._is_frozen)

    def test_pop(self):
        obj = FrozenDict(_private=1, public=2)
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.pop('public')

    def test_popitem(self):
        obj = FrozenDict(_private=1, public=2)
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.popitem()

    def test_update(self):
        obj = FrozenDict(_private=1, public=2)
        with self.assertRaisesRegex(AttributeError, self.message):
            obj.update({'attr': 1})

    def test_replace(self):
        obj1 = FrozenDict(_private=1, public=2)
        obj2 = obj1.replace(_private=3, public=4)
        self.assertNotEqual(obj1, obj2)
        self.assertEqual(obj2._private, 3)
        self.assertEqual(obj2.public, 4)
        self.assertEqual(obj2['public'], 4)
        self.assertTrue(obj2._is_frozen)


class FakeBaseObject(BaseObject):
    class Config(BaseObject):
        f1: str = 'FakeBaseObject'
        f2 =  BaseField(attr_type=str, default='FakeBaseObject')

class FakeObjectWithAttr(BaseObject):
    var1: str = None
    var2: str = None

class FakeBaseDict(BaseDict):
    class Config(BaseObject):
        f1: str = 'FakeBaseDict'
        f2 = BaseField(attr_type=str, default='FakeBaseDict')

class Fake01PythonClass:
    class Config:
        pass

class Fake02PythonClass:
    class Config:
        pass

class ConfigHashTestCase(TestCase):
    # https://everysk.atlassian.net/browse/COD-2746

    def test_different_values(self):
        # pylint: disable=no-member
        self.assertEqual(FakeBaseObject._config.f1, 'FakeBaseObject')
        self.assertEqual(FakeBaseObject._config.f2, 'FakeBaseObject')
        self.assertEqual(FakeBaseDict._config.f1, 'FakeBaseDict')
        self.assertEqual(FakeBaseDict._config.f2, 'FakeBaseDict')

    def test_python_qualname(self):
        self.assertEqual(Fake01PythonClass.Config.__name__, 'Config')
        self.assertEqual(Fake01PythonClass.Config.__qualname__, 'Fake01PythonClass.Config')
        self.assertEqual(Fake02PythonClass.Config.__name__, 'Config')
        self.assertEqual(Fake02PythonClass.Config.__qualname__, 'Fake02PythonClass.Config')


class MetaClassParent(BaseObject):
    p01 = BaseField(attr_type=str, default='Parent field')
    p02: str = '1'
    p03 = 1
    p04: float

    @property
    def prop(self):
        return self.p01

    @prop.setter
    def prop(self, value: str) -> None:
        self.p01 = value

    def func(self):
        pass


class MetaClassChild(MetaClassParent):
    p01 = BaseField(attr_type=str, default='Child field')
    c02: str = '1'
    c03 = 1
    c04: float


class MetaClassAttributesTestCase(TestCase):

    def test_class_attributes(self):
        attrs = getattr(MetaClassParent, MetaClass._attr_name)
        self.assertDictEqual(
            attrs,
            {
                '_errors': dict,
                '_is_frozen': bool,
                '_silent': bool,
                'p01': BaseField(attr_type=str, default='Parent field'),
                'p02': str,
                'p03': int,
                'p04': float
            }
        )

    def test_class_annotations(self):
        self.assertDictEqual(
            MetaClassParent.__annotations__,
            {
                'p01': str,
                'p02': str,
                'p03': int,
                'p04': float
            }
        )

    def test_class_inheritance_attributes(self):
        attrs = getattr(MetaClassChild, MetaClass._attr_name)
        self.assertDictEqual(
            attrs,
            {
                '_errors': dict,
                '_is_frozen': bool,
                '_silent': bool,
                'p01': BaseField(attr_type=str, default='Child field'),
                'p02': str,
                'p03': int,
                'p04': float,
                'c02': str,
                'c03': int,
                'c04': float
            }
        )

    def test_class_inheritance_annotations(self):
        self.assertDictEqual(
            MetaClassChild.__annotations__,
            {
                'p01': str,
                'c02': str,
                'c03': int,
                'c04': float
            }
        )

    def test_class_inheritance_default_value(self):
        self.assertEqual(MetaClassChild.p01, 'Child field')
        self.assertEqual(MetaClassChild.p02, '1')
        self.assertEqual(MetaClassChild.p03, 1)
        self.assertIsNone(MetaClassChild.p04)
        self.assertIsNone(MetaClassChild().func())

    def test_class_inheritance_changed_value(self):
        old_parent_p02 = MetaClassParent.p02
        old_child_p02 = MetaClassChild.p02
        MetaClassParent.p02 = 'First'
        self.assertEqual(MetaClassParent.p02, 'First')
        self.assertEqual(MetaClassChild.p02, 'First')
        MetaClassChild.p02 = 'Second'
        self.assertEqual(MetaClassParent.p02, 'First')
        self.assertEqual(MetaClassChild.p02, 'Second')
        MetaClassParent.p02 = old_parent_p02
        MetaClassChild.p02 = old_child_p02

    def test_obj_attributes(self):
        obj = MetaClassParent()
        attrs = getattr(obj, MetaClass._attr_name)
        self.assertDictEqual(
            attrs,
            {
                '_errors': dict,
                '_is_frozen': bool,
                '_silent': bool,
                'p01': BaseField(attr_type=str, default='Parent field'),
                'p02': str,
                'p03': int,
                'p04': float
            }
        )

    def test_obj_annotations(self):
        # pylint: disable=no-member
        obj = MetaClassParent()
        self.assertDictEqual(
            obj.__annotations__,
            {
                'p01': str,
                'p02': str,
                'p03': int,
                'p04': float
            }
        )

    def test_obj_inheritance_attributes(self):
        obj = MetaClassChild()
        attrs = getattr(obj, MetaClass._attr_name)
        self.assertDictEqual(
            attrs,
            {
                '_errors': dict,
                '_is_frozen': bool,
                '_silent': bool,
                'p01': BaseField(attr_type=str, default='Child field'),
                'p02': str,
                'p03': int,
                'p04': float,
                'c02': str,
                'c03': int,
                'c04': float
            }
        )

    def test_obj_inheritance_annotations(self):
        # pylint: disable=no-member
        obj = MetaClassChild()
        self.assertDictEqual(
            obj.__annotations__,
            {
                'p01': str,
                'c02': str,
                'c03': int,
                'c04': float
            }
        )

    def test_obj_inheritance_default_value(self):
        obj = MetaClassChild()
        self.assertEqual(obj.p01, 'Child field')
        self.assertEqual(obj.p02, '1')
        self.assertEqual(obj.p03, 1)
        self.assertIsNone(obj.p04)

    def test_obj_inheritance_changed_value(self):
        parent = MetaClassParent()
        child = MetaClassChild()
        parent.p02 = 'First'
        self.assertEqual(parent.p02, 'First')
        self.assertEqual(child.p02, '1')
        child.p02 = 'Second'
        self.assertEqual(parent.p02, 'First')
        self.assertEqual(child.p02, 'Second')

    def test_property_value(self):
        # https://everysk.atlassian.net/browse/COD-3457
        obj = MetaClassParent(p01='01')
        self.assertEqual(obj.p01, '01')
        self.assertEqual(obj.prop, '01')

        obj = MetaClassParent(prop='02')
        self.assertEqual(obj.p01, '02')
        self.assertEqual(obj.prop, '02')


class BeforeInitTestCase(TestCase):

    class BeforeInitBaseObject(BaseObject):
        key: str = None

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            return {'key': 'before'}

    class BeforeInitBaseDict(BaseDict):
        key: str = None

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            return {'key': 'before'}

    class BeforeInitBaseObjectNone(BaseObject):
        key: str = None

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            return None

    class BeforeInitBaseDictNone(BaseDict):
        key: str = None

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            return None

    class BeforeInitBaseObjectRemoveKey(BaseObject):

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            if 'key' in kwargs:
                del kwargs['key']
            return kwargs

    class BeforeInitBaseDictRemoveKey(BaseDict):

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            if 'key' in kwargs:
                del kwargs['key']
            return kwargs

    def test_base_object(self):
        obj = BeforeInitTestCase.BeforeInitBaseObject(key='test')
        self.assertEqual(obj.key, 'before')

    def test_base_object_none(self):
        obj = BeforeInitTestCase.BeforeInitBaseObjectNone(key='test')
        self.assertEqual(obj.key, 'test')

    def test_base_dict(self):
        obj = BeforeInitTestCase.BeforeInitBaseDict(key='test')
        self.assertEqual(obj.key, 'before')
        self.assertEqual(obj['key'], 'before')

    def test_base_dict_none(self):
        obj = BeforeInitTestCase.BeforeInitBaseDictNone(key='test')
        self.assertEqual(obj.key, 'test')
        self.assertEqual(obj['key'], 'test')

    def test_base_object_remove_key(self):
        obj = BeforeInitTestCase.BeforeInitBaseObjectRemoveKey(key='test')
        with self.assertRaisesRegex(AttributeError, "'BeforeInitBaseObjectRemoveKey' object has no attribute 'key'"):
            obj.key

    def test_base_dict_remove_key(self):
        obj = BeforeInitTestCase.BeforeInitBaseDictRemoveKey(key='test')
        with self.assertRaisesRegex(AttributeError, "'BeforeInitBaseDictRemoveKey' object has no attribute 'key'"):
            obj.key

        with self.assertRaisesRegex(KeyError, 'key'):
            obj['key']


class AfterInitTestCase(TestCase):

    class AfterInitBaseObject(BaseObject):
        key: str = None
        def __after_init__(self) -> None:
            self.key = 'after'

    class AfterInitBaseDict(BaseDict):
        key: str = None
        def __after_init__(self) -> None:
            self.key = 'after'

    def test_after_base_object(self):
        # pylint: disable=no-member
        obj = BaseObject(key='test')
        self.assertEqual(obj.key, 'test')

        obj = AfterInitTestCase.AfterInitBaseObject(key='test')
        self.assertEqual(obj.key, 'after')

    def test_after_base_dict(self):
        obj = BaseDict(key='test')
        self.assertEqual(obj.key, 'test')
        self.assertEqual(obj['key'], 'test')

        obj = AfterInitTestCase.AfterInitBaseDict(key='test')
        self.assertEqual(obj.key, 'after')
        self.assertEqual(obj['key'], 'after')


class SilentTestCase(TestCase):

    class SilentBaseObject(BaseObject):
        f1: bool = False

        @classmethod
        def __before_init__(cls, **kwargs: dict) -> dict:
            if 'before' in kwargs:
                raise ValueError('before')
            return kwargs

        def __after_init__(self) -> None:
            if hasattr(self, 'after'):
                raise ValueError('after')

        def _init_error_handler(self, kwargs: dict, errors: dict[str, Exception]) -> None:
            for key, error in errors.items():
                if error:
                    self.error_found = f'{key}: {error}'

    class SilentInheritance(SilentBaseObject):
        def __after_init__(self) -> None:
            if hasattr(self, 'after'):
                raise ValueError('after')

    def test_init_error(self):
        self.assertRaisesRegex(FieldValueError, "Key f1 must be <class 'bool'>.", SilentTestCase.SilentBaseObject, f1=2)

    def test_init_inheritance_error(self):
        self.assertRaisesRegex(FieldValueError, "Key f1 must be <class 'bool'>.", SilentTestCase.SilentInheritance, f1=2)

    def test_init_error_silent(self):
        obj = SilentTestCase.SilentBaseObject(f1=2, silent=True)
        self.assertEqual(obj.error_found, "init: Key f1 must be <class 'bool'>.")

    def test_init_error_inheritance_silent(self):
        obj = SilentTestCase.SilentInheritance(f1=2, silent=True)
        self.assertEqual(obj.error_found, "init: Key f1 must be <class 'bool'>.")

    def test_before_init_error(self):
        self.assertRaisesRegex(ValueError, "before", SilentTestCase.SilentBaseObject, before=2)

    def test_before_init_inheritance_error(self):
        self.assertRaisesRegex(ValueError, "before", SilentTestCase.SilentInheritance, before=2)

    def test_before_init_error_silent(self):
        obj = SilentTestCase.SilentBaseObject(before=2, silent=True)
        self.assertEqual(obj.error_found, "before_init: before")

    def test_before_init_error_inheritance_silent(self):
        obj = SilentTestCase.SilentInheritance(before=2, silent=True)
        self.assertEqual(obj.error_found, "before_init: before")

    def test_after_init_error(self):
        self.assertRaisesRegex(ValueError, "after", SilentTestCase.SilentBaseObject, after=2)

    def test_after_init_inheritance_error(self):
        self.assertRaisesRegex(ValueError, "after", SilentTestCase.SilentInheritance, after=2)

    def test_after_init_error_silent(self):
        obj = SilentTestCase.SilentBaseObject(after=2, silent=True)
        self.assertEqual(obj.error_found, "after_init: after")

    def test_after_init_error_inheritance_silent(self):
        obj = SilentTestCase.SilentInheritance(after=2, silent=True)
        self.assertEqual(obj.error_found, "after_init: after")


class TypingCheckingTestCase(TestCase):
    ## Internal classes for testing typing.
    class MultiType(BaseObject):
        field: str | int = None

    class MultiTypeUnion(BaseObject):
        field: Union[str, int] = None

    class SubscriptableType(BaseObject):
        field01: list[int] = None
        field02: tuple[int] = None
        field03: dict[str, int] = None

    ## Testes for typing.
    def test_multi_type_int(self):
        obj = TypingCheckingTestCase.MultiType(field=1)
        self.assertEqual(obj.field, 1)

    def test_multi_type_union_int(self):
        obj = TypingCheckingTestCase.MultiTypeUnion(field=1)
        self.assertEqual(obj.field, 1)

    def test_multi_type_str(self):
        obj = TypingCheckingTestCase.MultiType(field='a')
        self.assertEqual(obj.field, 'a')

    def test_multi_type_union_str(self):
        obj = TypingCheckingTestCase.MultiTypeUnion(field='a')
        self.assertEqual(obj.field, 'a')

    def test_multi_type_error(self):
        with self.assertRaisesRegex(FieldValueError, "Key field must be str | int."):
            TypingCheckingTestCase.MultiType(field=1.0)

    def test_multi_type_union_error(self):
        with self.assertRaisesRegex(FieldValueError, "Key field must be str | int."):
            TypingCheckingTestCase.MultiTypeUnion(field=1.0)

    def test_subscriptable_type_list(self):
        obj = TypingCheckingTestCase.SubscriptableType(field01=[1])
        self.assertListEqual(obj.field01, [1])

    def test_subscriptable_type_tuple(self):
        obj = TypingCheckingTestCase.SubscriptableType(field02=(1,))
        self.assertTupleEqual(obj.field02, (1,))

    def test_subscriptable_type_dict(self):
        obj = TypingCheckingTestCase.SubscriptableType(field03={'a': 1})
        self.assertDictEqual(obj.field03, {'a': 1})

    def test_subscriptable_type_list_error(self):
        with self.assertRaisesRegex(FieldValueError, r'Key field01 must be list\[int\].'):
            TypingCheckingTestCase.SubscriptableType(field01='a')

    def test_subscriptable_type_tuple_error(self):
        with self.assertRaisesRegex(FieldValueError, r'Key field02 must be tuple\[int\].'):
            TypingCheckingTestCase.SubscriptableType(field02='a')

    def test_subscriptable_type_dict_error(self):
        with self.assertRaisesRegex(FieldValueError, r'Key field03 must be dict\[str, int\].'):
            TypingCheckingTestCase.SubscriptableType(field03='a')


class BaseDictSuperTestCase(TestCase):
    # pylint: disable=useless-parent-delegation
    # These tests are only to see if super is supported in BaseDict.
    class Test(BaseDict):

        def clear(self) -> None:
            return super().clear()

        def copy(self) -> dict:
            return super().copy()

        def fromkeys(self, keys: list, default: Any = None) -> dict:
            return super().fromkeys(keys, default)

        def get(self, key: str, default: Any = None) -> Any:
            return super().get(key, default)

        def items(self) -> dict_items:
            return super().items()

        def keys(self) -> dict_keys:
            return super().keys()

        def pop(self, *args) -> Any:
            return super().pop(*args)

        def popitem(self) -> tuple:
            return super().popitem()

        def update(self, *args, **kwargs) -> None:
            return super().update(*args, **kwargs)

        def values(self) -> dict_values:
            return super().values()

    def test_clear(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        obj.clear()
        self.assertEqual(obj, BaseDictSuperTestCase.Test())

    def test_copy(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertDictEqual(obj.copy(), obj)

    def test_fromkeys(self):
        obj = BaseDictSuperTestCase.Test()
        self.assertDictEqual(obj.fromkeys(['a', 'b'], 1), {'a': 1, 'b': 1})

    def test_get(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertEqual(obj.get('a'), 1)
        self.assertEqual(obj.get('b'), None)
        self.assertEqual(obj.get('b', 2), 2)

    def test_items(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertListEqual(list(obj.items()), [('a', 1)])

    def test_keys(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertListEqual(list(obj.keys()), ['a'])

    def test_pop(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertEqual(obj.pop('a'), 1)
        self.assertEqual(obj, BaseDictSuperTestCase.Test())

    def test_popitem(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertEqual(obj.popitem(), ('a', 1))
        self.assertEqual(obj, BaseDictSuperTestCase.Test())

    def test_update(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        obj.update(b=2)
        self.assertEqual(obj, BaseDictSuperTestCase.Test(a=1, b=2))

    def test_values(self):
        obj = BaseDictSuperTestCase.Test(a=1)
        self.assertListEqual(list(obj.values()), [1])
