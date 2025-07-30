###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
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
from everysk.core.datetime import DateTime
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.entities.portfolio.base import SecuritiesField, Portfolio
from everysk.sdk.entities.portfolio.securities import Securities


###############################################################################
#   Securities Field TestCase Implementation
###############################################################################
class TestSecuritiesField(TestCase):

    def setUp(self):
        self.securities_field = SecuritiesField()

    def test_clean_value_with_list(self):
        test_value = [{'symbol': 'AAPL', 'name': 'Apple Inc.'}]
        cleaned_value = self.securities_field.clean_value(test_value)

        # Ensure the cleaned value is of type `Securities`
        self.assertIsInstance(cleaned_value, Securities)

    def test_clean_value_without_list(self):
        test_value = 'Some value'
        cleaned_value = self.securities_field.clean_value(test_value)

        # Ensure the cleaned value is not modified
        self.assertEqual(cleaned_value, [test_value])

###############################################################################
#   Portfolio TestCase Implementation
###############################################################################
class TestPortfolio(TestCase):

    def setUp(self):
        self.sample_data = {
            'id': 'port_1234567891011211234567890',
            'workspace': 'SampleWorkspace',
            'name': 'SamplePortfolio',
            'tags': ['tag1', 'tag2'],
            'link_uid': 'ABC',
            'description': 'Description',
            'nlv': 1000.0,
            'base_currency': 'USD',
            'date': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'securities': Securities([{'symbol': 'AAPL'}]),
            'version': '1.0',
            'created_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'updated_on': DateTime(2023, 9, 9, 9, 9, 9, 9),
            'level': 'v1',
            'outstanding_shares': 1000,
            'source_hash': 'XYZ',
            'status': 'OK',
            'portfolio_uid': 'UID123',
            'check_securities': False
        }
        self.portfolio = Portfolio(**self.sample_data)
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()

    def test_static_methods(self):
        self.assertEqual(Portfolio.get_id_prefix(), settings.PORTFOLIO_ID_PREFIX)

    def test_validate(self):
        portfolio: Portfolio = self.portfolio.copy()
        portfolio.check_securities = True
        portfolio.securities = []
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'validate', 'self_obj': portfolio.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            portfolio.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_validate_with_negative_nlv(self):
        portfolio: Portfolio = self.portfolio.copy()
        portfolio.check_securities = True
        portfolio.securities = []
        portfolio.nlv = -1000.0
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'validate', 'self_obj': portfolio.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            portfolio.validate()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_check(self):
        entity_dict = self.sample_data
        entity_dict['check_securities'] = True
        entity_dict['securities'] = []

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            result = Portfolio.check(entity_dict=entity_dict)

        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'validate', 'self_obj': result.to_dict(add_class_path=True), 'params': {}}, protocol='gzip', serialize='json')
        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_to_csv(self):
        out_csv = self.portfolio.to_csv()
        self.assertIsInstance(out_csv, str)

    def test_query_load_with_id(self):
        portfolio = Portfolio(id='port_1234567891011211234567890', workspace='SampleWorkspace')
        expected_content = compress({'class_name': 'Portfolio', 'method_name': 'retrieve', 'self_obj': None, 'params': {'entity_id': 'port_1234567891011211234567890', 'projection': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            portfolio.load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    def test_query_load(self):
        portfolio = Portfolio(link_uid='SampleLinkUID', workspace='SampleWorkspace')
        expected_content = compress({'class_name': 'Query', 'method_name': 'load', 'self_obj': portfolio.to_query().to_dict(add_class_path=True), 'params': {'offset': None}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            portfolio.load()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
