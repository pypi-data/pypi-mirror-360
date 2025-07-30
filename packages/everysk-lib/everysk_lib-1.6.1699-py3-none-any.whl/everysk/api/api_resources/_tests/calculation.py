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
from everysk.api.api_resources.calculation import Calculation
from everysk.core.unittests import TestCase, mock

###############################################################################
#   Calculation TestCase Implementation
###############################################################################
class APICalculationTestCase(TestCase):

    def test_refresh_test_case(self):
        params = {'some': 'params'}
        retrieve_params = {'params1', 'params2'}
        calculation = Calculation(retrieve_params, params)
        refreshed_calculation = calculation.refresh()

        self.assertIsInstance(refreshed_calculation, Calculation)

    def test_class_name(self):
        self.assertEqual(Calculation.class_name(), 'calculations')

    def test_class_url(self):
        self.assertEqual(Calculation.class_url(), f'/{Calculation.class_name()}')

    @mock.patch('everysk.api.utils.create_api_requestor')
    def test_calculation__call_method(self, mock_create_api_requestor):
        mock_api_requestor = mock.Mock()

        expected_response = {'success': True}
        mock_api_requestor.post.return_value = expected_response
        mock_create_api_requestor.return_value = mock_api_requestor
        response = Calculation._Calculation__call_method('test_method', key='value')

        mock_create_api_requestor.assert_called_once()
        mock_api_requestor.post.assert_called_once_with('/calculations/test_method', {'key': 'value'})
        self.assertEqual(response, expected_response)

    def test_risk_attribution_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.riskAttribution(key='value')

        mock_call_method.assert_called_once_with('risk_attribution', key='value')
        self.assertEqual(result, 'expected result')

    def test_parametric_risk_attribution_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.parametricRiskAttribution(key='value')

        mock_call_method.assert_called_once_with('parametric_risk_attribution', key='value')
        self.assertEqual(result, 'expected result')

    def test_stress_test_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.stressTest(key='value')

        mock_call_method.assert_called_once_with('stress_test', key='value')
        self.assertEqual(result, 'expected result')

    def test_exposure_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.exposure(key='value')

        mock_call_method.assert_called_once_with('exposure', key='value')
        self.assertEqual(result, 'expected result')

    def test_properties_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.properties(key='value')

        mock_call_method.assert_called_once_with('properties', key='value')
        self.assertEqual(result, 'expected result')

    def test_backtest_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.backtest(key='value')

        mock_call_method.assert_called_once_with('backtest', key='value')
        self.assertEqual(result, 'expected result')

    def test_backtest_statistics_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.backtestStatistics(key='value')

        mock_call_method.assert_called_once_with('backtest_statistics', key='value')
        self.assertEqual(result, 'expected result')

    def test_aggregations_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.aggregations(key='value')

        mock_call_method.assert_called_once_with('aggregations', key='value')
        self.assertEqual(result, 'expected result')

    def test_fundamentals_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.fundamentals(key='value')

        mock_call_method.assert_called_once_with('fundamentals', key='value')
        self.assertEqual(result, 'expected result')

    def test_days_to_unwind_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.daysToUnwind(key='value')

        mock_call_method.assert_called_once_with('days_to_unwind', key='value')
        self.assertEqual(result, 'expected result')

    def test_sensitivity_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.sensitivity(key='value')

        mock_call_method.assert_called_once_with('sensitivity', key='value')
        self.assertEqual(result, 'expected result')

    def test_underlying_stress_sensitivity_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.underlying_stress_sensitivity(key='value')

        mock_call_method.assert_called_once_with('underlying_stress_sensitivity', key='value')
        self.assertEqual(result, 'expected result')

    def test_optimize_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.optimize(key='value')

        mock_call_method.assert_called_once_with('optimize', key='value')
        self.assertEqual(result, 'expected result')

    def test_bond_pricer_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.bondPricer(key='value')

        mock_call_method.assert_called_once_with('bond_pricer', key='value')
        self.assertEqual(result, 'expected result')

    def test_marginal_tracking_error_method(self):
        with mock.patch('everysk.api.api_resources.calculation.Calculation._Calculation__call_method') as mock_call_method:
            mock_call_method.return_value = 'expected result'
            result = Calculation.marginalTrackingError(key='value')

        mock_call_method.assert_called_once_with('marginal_tracking_error', key='value')
        self.assertEqual(result, 'expected result')
