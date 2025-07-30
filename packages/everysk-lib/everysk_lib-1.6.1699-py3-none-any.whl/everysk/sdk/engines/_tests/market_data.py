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
from everysk.core.datetime import Date
from everysk.core.http import HttpSDKPOSTConnection, httpx
from everysk.core.unittests import TestCase, mock

from everysk.sdk.engines.market_data import MarketData


###############################################################################
#   Market Data Test Case Implementation
###############################################################################
class MarketDataTestCase(TestCase):

    def setUp(self) -> None:
        self.headers = HttpSDKPOSTConnection().get_headers()
        self.api_url = HttpSDKPOSTConnection().get_url()
        return super().setUp()

    ###############################################################################
    #  Get Security Test Case Implementation
    ###############################################################################
    def test_get_security_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({'class_name': 'MarketData', 'method_name': 'get_security', 'self_obj': market_data.to_dict(add_class_path=True), 'params': {'date': '123', 'ticker_list': ['test'], 'ticker_type': ['choice1', 'choice2'], 'projection': 'test_projection', 'nearest': True}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_security(date='123', ticker_list=['test'], ticker_type=['choice1', 'choice2'], projection='test_projection', nearest=True)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Get Historical Test Case Implementation
    ###############################################################################
    def test_get_historical_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({'class_name': 'MarketData', 'method_name': 'get_historical', 'self_obj': market_data.to_dict(add_class_path=True), 'params': {'date': '2023-08-14', 'start_date': '2022-05-14', 'end_date': '2024-07-17', 'ticker_list': ['test'], 'ticker_type': ['choice1', 'choice2'], 'projection': 'test_projection', 'nearest': True, 'real_time': True}}, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_historical(date='2023-08-14', start_date='2022-05-14', end_date='2024-07-17', ticker_list=['test'], ticker_type=['choice1', 'choice2'], projection='test_projection', nearest=True, real_time=True)

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Search Test Case Implementation
    ###############################################################################
    def test_search_is_called(self):
        market_data = MarketData(date=Date(2023, 7, 31))
        expected_content = compress({
            'class_name': 'MarketData',
            'method_name': 'search',
            'self_obj': market_data.to_dict(add_class_path=True),
            'params': {
                'conditions': [['asset', '=', 'test']],
                'fields': ['everysk_id', 'asset'],
                'order_by': '-everysk_id',
                'limit': 10,
                'date': '2023-08-14',
                'path': ''
            }
        }, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.search(
                conditions=[['asset', '=', 'test']],
                fields=['everysk_id', 'asset'],
                order_by='-everysk_id',
                limit=10,
                date='2023-08-14'
            )

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )

    ###############################################################################
    #  Get Currencies Test Case Implementation
    ###############################################################################
    def test_get_currencies_is_called(self):
        market_data = MarketData()
        expected_content = compress({
            'class_name': 'MarketData',
            'method_name': 'get_currencies',
            'self_obj': market_data.to_dict(add_class_path=True),
            'params': {}
        }, protocol='gzip', serialize='json')

        with mock.patch('httpx.Client.post') as mock_post:
            mock_post.return_value.content = '{}'
            mock_post.return_value.status_code = 200
            market_data.get_currencies()

        mock_post.assert_called_with(
            url=self.api_url,
            headers=self.headers,
            timeout=httpx.Timeout(timeout=30, read=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT),
            content=expected_content
        )
