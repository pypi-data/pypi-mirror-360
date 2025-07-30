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
from everysk.api.api_resources.report_template import ReportTemplate
from everysk.core.unittests import TestCase


###############################################################################
#   Report Template TestCase Implementation
###############################################################################
class APIReportTemplateTestCase(TestCase):

    def test_report_template_class_name(self):
        self.assertEqual(ReportTemplate.class_name(), 'report_template')
