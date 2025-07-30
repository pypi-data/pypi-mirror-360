###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.unittests import TestCase
from everysk.utils import bool_convert, search_key_on_dict


class SearchKeyTestCase(TestCase):

    def test_search_key(self):
        dct = {'key': 'value'}
        self.assertListEqual(list(search_key_on_dict('key', dct)), ['value'])

    def test_search_key_more_results(self):
        dct = {'key': 'value', 'key2': {'key': 'test'}, 'key1': 'not'}
        self.assertListEqual(list(search_key_on_dict('key', dct)), ['value', 'test'])

    def test_search_key_inside_another_dict(self):
        dct = {'key1': {'key2': {'key': 'test'}}}
        self.assertListEqual(list(search_key_on_dict('key', dct)), ['test'])

    def test_search_key_inside_list(self):
        dct = {'key3': [{'key1': {'key2': {'key': 'test'}}}]}
        self.assertListEqual(list(search_key_on_dict('key', dct)), ['test'])


class BoolConverterTestCase(TestCase):

    def test_clean_value_true(self):
        self.assertTrue(bool_convert(1))
        self.assertTrue(bool_convert(True))
        self.assertTrue(bool_convert('y'))
        self.assertTrue(bool_convert('yes'))
        self.assertTrue(bool_convert('on'))

    def test_clean_value_false(self):
        self.assertFalse(bool_convert(0))
        self.assertFalse(bool_convert(False))
        self.assertFalse(bool_convert('n'))
        self.assertFalse(bool_convert('no'))
        self.assertFalse(bool_convert('off'))
