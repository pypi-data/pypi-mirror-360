###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.core.unittests import TestCase

from everysk.sdk.engines import __getattr__

###############################################################################
#   Init Test Case Implementation
###############################################################################
# pylint: disable=import-outside-toplevel
# pylint: disable=no-name-in-module
# pylint: disable=unused-import
class EnginesInitTestCase(TestCase):

    def test_get_attribute_imports_expression(self):
        from everysk.sdk.engines.expression import Expression as expected
        from everysk.sdk.engines import Expression
        self.assertEqual(expected, Expression)

    def test_get_attribute_imports_compliance(self):
        from everysk.sdk.engines.compliance import Compliance as expected
        from everysk.sdk.engines import Compliance
        self.assertEqual(expected, Compliance)

    def test_get_attribute_imports_cache(self):
        from everysk.sdk.engines.cache import UserCache as expected
        from everysk.sdk.engines import UserCache
        self.assertEqual(expected, UserCache)

    def test_get_attribute_imports_non_existent_module_raises_attribute_error(self):
        with self.assertRaises(ImportError) as context:
            from everysk.sdk.engines import non_existent_module
        self.assertEqual(str(context.exception), "cannot import name 'non_existent_module' from 'everysk.sdk.engines' (/var/app/src/everysk/sdk/engines/__init__.py)")

    def test_get_attribute_imports_all_modules_path(self):
        from everysk.config import settings
        modules = settings.EVERYSK_SDK_ENGINES_MODULES_PATH.keys()
        self.assertListEqual(list(modules), ['Expression', 'Compliance', 'UserCache', 'MarketData'])
