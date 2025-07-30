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
from everysk.api.api_resources import MarketData
from everysk.core.unittests import TestCase, mock


###############################################################################
#   Market Data TestCase Implementation
###############################################################################
class APIMarketDataTestCase(TestCase):

    def test_refresh(self):
        market_data = MarketData(retrieve_params={'params1': 'value1', 'params2': 'value2'}, params={'param_key1': 'param', 'param_key2': 'params3'})
        self.assertEqual(market_data.refresh(), market_data)

    def test_class_name(self):
        self.assertEqual(MarketData.class_name(), 'market_data')

    def test_class_url(self):
        self.assertEqual(MarketData.class_url(), '/market_data')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_market_data__call_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()

        expected_response = {'success': True}
        mock_api_requestor.post.return_value = expected_response
        mock_create_api_requestor.return_value = mock_api_requestor
        response = MarketData._MarketData__call_method('test_method', key='value')

        mock_create_api_requestor.assert_called_once()
        mock_api_requestor.post.assert_called_once_with('/market_data/test_method', {'key': 'value'})
        self.assertEqual(response, expected_response)

    def test_symbols_search_method(self):
        with mock.patch('everysk.api.api_resources.market_data.MarketData._MarketData__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = MarketData.symbolsSearch(key='value')

        mock_call_method.assert_called_once_with('symbols_search', key='value')
        self.assertEqual(result, 'expected result')

    def test_symbols_check_method(self):
        with mock.patch('everysk.api.api_resources.market_data.MarketData._MarketData__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = MarketData.symbolsCheck(key='value')

        mock_call_method.assert_called_once_with('symbols_check', key='value')
        self.assertEqual(result, 'expected result')

    def test_symbols_price_method(self):
        with mock.patch('everysk.api.api_resources.market_data.MarketData._MarketData__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = MarketData.symbolsPrice(key='value')

        mock_call_method.assert_called_once_with('symbols_price', key='value')
        self.assertEqual(result, 'expected result')

    def test_symbols_realtime_price_method(self):
        with mock.patch('everysk.api.api_resources.market_data.MarketData._MarketData__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = MarketData.symbolsRealtimePrice(key='value')

        mock_call_method.assert_called_once_with('symbols_real_time_prices', key='value')
        self.assertEqual(result, 'expected result')

    def test_symbols_historical_method(self):
        with mock.patch('everysk.api.api_resources.market_data.MarketData._MarketData__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = MarketData.symbolsHistorical(key='value')

        mock_call_method.assert_called_once_with('symbols_historical', key='value')
        self.assertEqual(result, 'expected result')
