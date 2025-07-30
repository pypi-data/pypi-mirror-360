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
#   Init Test Case Implementation
###############################################################################
# pylint: disable=import-outside-toplevel
# pylint: disable=no-name-in-module
# pylint: disable=unused-import
class InitTestCase(TestCase):

    def test_sdk_modules_path(self):
        from everysk.config import settings
        modules = settings.EVERYSK_SDK_ENTITIES_MODULES_PATH.keys()
        self.assertListEqual(list(modules), ['CustomIndex', 'Datastore', 'File', 'Portfolio', 'PrivateSecurity', 'Query', 'Report', 'Script', 'Securities', 'Security','WorkerExecution', 'WorkflowExecution', 'Workspace'])

    def test_import_inexistent_module(self):
        with self.assertRaisesRegex(ImportError, "cannot import name 'inexistent_module' from 'everysk.sdk.entities'"):
            from everysk.sdk.entities import inexistent_module

    def test_import_portfolio(self):
        from everysk.sdk.entities.portfolio.base import Portfolio as TopLevelPortfolio
        from everysk.sdk.entities import Portfolio
        self.assertEqual(Portfolio, TopLevelPortfolio)

    def test_import_security(self):
        from everysk.sdk.entities.portfolio.security import Security as TopLevelSecurity
        from everysk.sdk.entities import Security
        self.assertEqual(Security, TopLevelSecurity)

    def test_import_securities(self):
        from everysk.sdk.entities.portfolio.securities import Securities as TopLevelSecurities
        from everysk.sdk.entities import Securities
        self.assertEqual(Securities, TopLevelSecurities)

    def test_import_datastore(self):
        from everysk.sdk.entities.datastore.base import Datastore as TopLevelDatastore
        from everysk.sdk.entities import Datastore
        self.assertEqual(Datastore, TopLevelDatastore)

    def test_import_custom_index(self):
        from everysk.sdk.entities.custom_index.base import CustomIndex as TopLevelCustomIndex
        from everysk.sdk.entities import CustomIndex
        self.assertEqual(CustomIndex, TopLevelCustomIndex)

    def test_import_file(self):
        from everysk.sdk.entities.file.base import File as TopLevelFile
        from everysk.sdk.entities import File
        self.assertEqual(File, TopLevelFile)

    def test_import_private_security(self):
        from everysk.sdk.entities.private_security.base import PrivateSecurity as TopLevelPrivateSecurity
        from everysk.sdk.entities import PrivateSecurity
        self.assertEqual(PrivateSecurity, TopLevelPrivateSecurity)

    def test_import_report(self):
        from everysk.sdk.entities.report.base import Report as TopLevelReport
        from everysk.sdk.entities import Report
        self.assertEqual(Report, TopLevelReport)

    def test_import_query(self):
        from everysk.sdk.entities.query import Query as TopLevelQuery
        from everysk.sdk.entities import Query
        self.assertEqual(Query, TopLevelQuery)

    def test_import_script(self):
        from everysk.sdk.entities.script import Script as TopLevelScript
        from everysk.sdk.entities import Script
        self.assertEqual(Script, TopLevelScript)
