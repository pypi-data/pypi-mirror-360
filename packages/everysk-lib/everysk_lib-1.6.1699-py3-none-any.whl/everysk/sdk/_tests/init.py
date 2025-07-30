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


###############################################################################
#   SDK Init Test Case Implementation
###############################################################################
# pylint: disable=import-outside-toplevel
# pylint: disable=no-name-in-module
# pylint: disable=unused-import
class SDKInitTestCase(TestCase):

    def test_get_attribute_imports_all_modules(self):
        from everysk.config import settings
        modules = settings.EVERYSK_SDK_MODULES_PATH.keys()
        self.assertEqual(list(modules), ['WorkerBase'])

    def test_get_attribute_raises_error_with_non_existent_module(self):
        with self.assertRaises(ImportError) as context:
            from everysk.sdk import non_existent_module
        self.assertEqual(str(context.exception), "cannot import name 'non_existent_module' from 'everysk.sdk' (/var/app/src/everysk/sdk/__init__.py)")

    def test_get_attribute_imports_worker_base(self):
        from everysk.sdk.worker_base import WorkerBase as expected
        from everysk.sdk import WorkerBase
        self.assertEqual(expected, WorkerBase)
