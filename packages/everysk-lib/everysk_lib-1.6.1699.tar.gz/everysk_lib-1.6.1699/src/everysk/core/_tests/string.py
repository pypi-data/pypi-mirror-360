###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.object import BaseObject
from everysk.core.string import import_from_string, is_string_object, to_string, normalize_string, normalize_string_to_search, is_isin_string_regex
from everysk.core.unittests import TestCase


class FakeClass(BaseObject):
    pass

class StringTestCase(TestCase):

    def test_import_from_string(self):
        obj = FakeClass()
        cls = import_from_string(obj.get_full_doted_class_path())
        self.assertEqual(cls, FakeClass)

    def test_import_from_string_import_error(self):
        self.assertRaisesRegex(
            ImportError,
            "banana doesn't look like a module path.",
            import_from_string,
            'banana'
        )

    def test_import_from_string__error(self):
        self.assertRaisesRegex(
            ImportError,
            'Module "everysk.core._tests.utils" does not define a "FakeClassError" class.',
            import_from_string,
            'everysk.core._tests.utils.FakeClassError'
        )

    def test_is_string_object(self):
        self.assertTrue(is_string_object('Teste'))
        self.assertTrue(is_string_object("Teste"))
        self.assertFalse(is_string_object({}))
        self.assertFalse(is_string_object(126))

    def test_to_string(self):
        self.assertEqual(to_string('teste'), 'teste')
        self.assertEqual(to_string(123), '123')

    def test_basic_normalization(self):
        self.assertEqual(normalize_string('café'), 'café')  # Note: 'e' and the combining accent as separate characters

    def test_special_characters_remain(self):
        self.assertEqual(normalize_string('!@#$%^&*()'), '!@#$%^&*()')

    def test_spaces_remain(self):
        self.assertEqual(normalize_string('Hello World'), 'Hello World')

    def test_empty_string(self):
        self.assertEqual(normalize_string(''), '')

    def test_no_change(self):
        self.assertEqual(normalize_string('abc'), 'abc')

    def test_normalization_with_combining_characters(self):
        # 'a' followed by a combining tilde
        self.assertEqual(normalize_string('a\u0303'), 'ã')

    def test_normalize_to_search_basic(self):
        self.assertEqual(normalize_string_to_search('   Café  '), 'café')

    def test_valid_isin(self):
        self.assertTrue(is_isin_string_regex('US0378331005'))  # Apple Inc. ISIN

    def test_invalid_isin_wrong_length(self):
        self.assertFalse(is_isin_string_regex('US03783310055'))

    def test_invalid_isin_wrong_characters(self):
        self.assertFalse(is_isin_string_regex('US0@3Z8331005'))

    def test_invalid_isin_starts_with_number(self):
        self.assertFalse(is_isin_string_regex('1US037833100'))

    def test_invalid_isin_starts_with_space(self):
        self.assertFalse(is_isin_string_regex(' US037833100'))

    def test_invalid_isin_ends_with_space(self):
        self.assertFalse(is_isin_string_regex('US037833100 '))

    def test_isin_with_non_string_input(self):
        self.assertFalse(is_isin_string_regex(123456789012))
