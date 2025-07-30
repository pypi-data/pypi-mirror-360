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
from everysk.api.api_resources import Datastore
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Datastore TestCase Implementation
###############################################################################
class APIDatastoreTestCase(TestCase):

    def test_datastore_class_name(self):
        self.assertEqual(Datastore.class_name(), 'datastore')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_datastore_explore_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.MagicMock()
        mock_create_api_requestor.return_value = mock_api_requestor
        mock_response = mock.MagicMock()

        mock_api_requestor.post.return_value = mock_response
        mock_kwargs = {
            'api_entry': 'https://example.com',
            'api_version': 'v2',
            'api_sid': 'abc',
            'api_token': 'token_example123',
            'verify_ssl_certs': True
        }
        expected_url = f"/{Datastore.class_name_list()}/explore"
        result = Datastore.explore(**mock_kwargs)

        mock_create_api_requestor.assert_called_once_with(mock_kwargs)
        mock_api_requestor.post.assert_called_once_with(expected_url, mock_kwargs)
        self.assertEqual(result, mock_response)
