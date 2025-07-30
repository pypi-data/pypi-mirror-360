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
from everysk.config import settings
from everysk.core.compress import compress
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.engines.compliance import Compliance


###############################################################################
#   Compliance Test Case Implementation
###############################################################################
class ComplianceTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        return super().setUp()

    ###############################################################################
    #   Check Method Test Case Implementation
    ###############################################################################
    def test_check_method_returns_expected_response(self):
        expected_content = compress({'class_name': 'Compliance', 'method_name': 'check', 'self_obj': None, 'params': {'rules': [{'rule': 'rule1'}, {'rule': 'rule2'}], 'datastore': [{'data': 'data1'}, {'data': 'data2'}], 'metadata': None}}, protocol='gzip', serialize='json')
        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            Compliance.check(rules=[{'rule': 'rule1'}, {'rule': 'rule2'}], datastore=[{'data': 'data1'}, {'data': 'data2'}])

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
