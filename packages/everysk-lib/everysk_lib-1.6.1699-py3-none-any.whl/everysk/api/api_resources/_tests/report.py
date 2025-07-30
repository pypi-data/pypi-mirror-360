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
from everysk.api.api_resources import Report
from everysk.core.unittests import TestCase, mock

###############################################################################
#   Report TestCase Implementation
###############################################################################
class APIReportTestCase(TestCase):

    def test_class_name_method(self):
        self.assertEqual(Report.class_name(), 'report')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_share_method(self, mock_create_api_requestor):
        mock_api_req = mock.Mock()
        mock_create_api_requestor.return_value = mock_api_req

        mock_response_data = {'id': 'report_id', 'other_data': 'example'}
        mock_api_req.post.return_value = {'report': mock_response_data}
        report = Report(retrieve_params={'key1': 'value1'}, params={'key2': 'value2'})
        report['id'] = 'report_id'
        result = report.share(param1='value1', param2='value2')
        expected_url = '/reports/report_id/share'

        mock_api_req.post.assert_called_once_with(expected_url, {'param1': 'value1', 'param2': 'value2'})
        self.assertEqual(report['id'], 'report_id')
        self.assertEqual(report['other_data'], 'example')
        self.assertNotIn('param1', report)
        self.assertNotIn('param2', report)
        self.assertEqual(result, report)
