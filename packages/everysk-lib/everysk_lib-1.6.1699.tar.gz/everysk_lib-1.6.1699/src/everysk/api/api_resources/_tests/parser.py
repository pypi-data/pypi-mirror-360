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
from everysk.api.api_resources import Parser
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Parser TestCase Implementations
###############################################################################
class APIParserTestCase(TestCase):

    def test_class_name(self):
        self.assertEqual(Parser.class_name(), 'parser')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_parser__call_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()

        expected_response = {'success': True}
        mock_api_requestor.post.return_value = expected_response
        mock_create_api_requestor.return_value = mock_api_requestor
        response = Parser._Parser__call_method('test_method', key='value')

        mock_create_api_requestor.assert_called_once()
        mock_api_requestor.post.assert_called_once_with('/parsers/test_method', {'key': 'value'})
        self.assertEqual(response, expected_response)

    def test_parse_method(self):
        with mock.patch('everysk.api.api_resources.parser.Parser._Parser__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected_result'
            result = Parser.parse('test_method', key='value')

        mock_call_method.assert_called_once_with('test_method/parse', key='value')
        self.assertEqual(result, 'expected_result')
