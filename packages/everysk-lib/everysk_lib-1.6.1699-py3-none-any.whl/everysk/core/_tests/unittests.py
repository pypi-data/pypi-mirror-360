###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.config import settings
from everysk.core.unittests import TestCase, mock


class SDKUnittestTestCase(TestCase):

    def setUp(self) -> None:
        self.mock_method = mock.MagicMock()
        self.mock_method.return_value = 'different than None'

    def test_obj_different_than_none(self):
        obj = TestCase()

        with self.assertWarns(DeprecationWarning) as context:
            obj._callTestMethod(self.mock_method) # pylint: disable=protected-access

        self.assertEqual(str(context.warning), f"It is deprecated to return a value that is not None from a test case ({self.mock_method})")

    def test_assert_dict_equal_when_dicts_are_different(self):
        first_dict = {'key': 'value'}
        second_dict = {'chave': 'valor'}
        with self.assertRaises(AssertionError) as context:
            self.assertDictEqual(d1=first_dict, d2=second_dict)

        self.assertEqual(str(context.exception), "{'key': 'value'} != {'chave': 'valor'}\n- {'key': 'value'}\n+ {'chave': 'valor'}")

    def test_serialize_convert_method(self):
        obj = mock.MagicMock()
        self.assertFalse(hasattr(obj, settings.SERIALIZE_CONVERT_METHOD_NAME))

    def test_serialize_convert_method_chain(self):
        obj = mock.MagicMock()
        self.assertFalse(hasattr(obj.obj.obj, settings.SERIALIZE_CONVERT_METHOD_NAME))

    @mock.patch('datetime.datetime')
    def test_serialize_convert_method_decorator(self, datetime: mock.MagicMock):
        obj = datetime.now()
        self.assertFalse(hasattr(obj, settings.SERIALIZE_CONVERT_METHOD_NAME))
