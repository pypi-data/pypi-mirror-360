###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
from copy import copy, deepcopy
from everysk.core.undefined import UndefinedType
from everysk.core.unittests import TestCase


class UndefinedTestCase(TestCase):

    def test_sitecustomize_file(self):
        # If Undefined exists the src/sitecustomize.py is working
        Undefined # pylint: disable=pointless-statement

    def test_init(self):
        msg = 'Do not use this class, use the constant Undefined.'
        self.assertRaisesRegex(
            NotImplementedError,
            msg,
            UndefinedType
        )

    def test_bool(self):
        self.assertFalse(Undefined)

    def test_copy(self):
        self.assertEqual(copy(Undefined), Undefined)

    def test_deepcopy(self):
        self.assertEqual(deepcopy(Undefined), Undefined)

    def test_delattr(self):
        with self.assertRaisesRegex(AttributeError, UndefinedType.default_error_message):
            del Undefined._block

    def test_equal(self):
        new_undefined = Undefined
        copy_undefined = copy(Undefined)
        deepcopy_undefined = deepcopy(Undefined)
        self.assertEqual(new_undefined, Undefined)
        self.assertEqual(copy_undefined, Undefined)
        self.assertEqual(deepcopy_undefined, Undefined)
        self.assertTrue(new_undefined is Undefined)
        self.assertTrue(copy_undefined is Undefined)
        self.assertTrue(deepcopy_undefined is Undefined)

    def test_getattr(self):
        with self.assertRaisesRegex(AttributeError, UndefinedType.default_error_message):
            getattr(Undefined, 'banana')

    def test_repr(self):
        self.assertEqual(repr(Undefined), '<Undefined value>')

    def test_setattr(self):
        with self.assertRaisesRegex(AttributeError, UndefinedType.default_error_message):
            setattr(Undefined, 'banana', 'amarela')

    def test_str(self):
        self.assertEqual(str(Undefined), '<Undefined value>')

    def test_hash(self):
        hash(Undefined)
        self.assertSetEqual({Undefined}, {Undefined})
