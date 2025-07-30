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
from everysk.core.datetime import Date
from everysk.core.exceptions import FieldValueError, SDKError, HttpError, RequiredError
from everysk.core.unittests import TestCase, mock

from everysk.sdk.base import HttpSDKPOSTConnection
from everysk.sdk.entities.portfolio.securities import Securities
from everysk.sdk.entities.portfolio.security import Security


###############################################################################
#   Securities TestCase Implementation
###############################################################################
class TestSecurities(TestCase):

    def setUp(self):
        self.valid_security_data = {
            'status': 'OK',
            'symbol': 'AAPL',
            'id': 'unique123',
            'quantity': 100.0,
            'instrument_class': 'Equity',
            'maturity_date': Date(2025, 5, 1),
            'issue_date': Date(2020, 1, 1),
            'return_date': Date(2025, 12, 31),
            'settlement': Date(2020, 1, 2),
            'display': 'Apple Inc.',
            'comparable': 'Yes',
            'previous_quantity': 50.0,
            'extra_field1': 'extra_value1',  # This should be placed in `extra_data`
            'extra_field2': 'extra_value2'   # This should also be placed in `extra_data`
        }

        self.security_1 = Security(**self.valid_security_data)
        self.security_2 = Security(**self.valid_security_data)
        self.securities_list = [self.security_1, self.security_2]

    def test_validate(self):
        securities = Securities(self.securities_list)
        self.assertTrue(securities.validate())

    def test_validate_with_len_equal_to_zero(self):
        with self.assertRaisesRegex(FieldValueError, 'The quantity of securities cannot be zero.'):
            Securities().validate()

    def test_invalid_validate_with_list(self):
        securities = Securities([self.valid_security_data])
        self.assertTrue(securities.validate())

    def test_invalid_validate(self):
        invalid_security_data = {'id': 'unique123', 'quantity': 100.0}
        with self.assertRaises(RequiredError):
            securities = Securities([invalid_security_data])
            securities.validate()

    def test_invalid_validate_not_dict(self):
        with self.assertRaisesRegex(FieldValueError, 'Security: The value must be a dict.'):
            Securities("AAPL")

    def test_from_lists(self):
        header = list(self.valid_security_data.keys())
        security_data_list = [list(self.valid_security_data.values())]
        securities_list = [header] + security_data_list
        securities = Securities.from_lists(securities_list)
        self.assertEqual(len(securities), 1)
        self.assertIsInstance(securities[0], Security)

    def test_diff(self):
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', return_value={}):
            result = Securities.diff(self.securities_list, [self.security_1])
            self.assertIsInstance(result, dict)  # Adjust this depending on your expected diff response format

    def test_diff_raises_sdk_error(self):
        securities_a = [{}]
        securities_b = [{}]
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', side_effect=HttpError("Test HTTP Error")):
            with self.assertRaises(SDKError) as context:
                Securities.diff(securities_a, securities_b)
            self.assertEqual(str(context.exception), "Test HTTP Error")

    def test_consolidate(self):
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', return_value={}):
            securities = Securities(self.securities_list)
            consolidation_keys = ['symbol', 'exchange']
            result = securities.consolidate(consolidation_keys)
            self.assertIsInstance(result, Securities)  # Adjust this depending on your expected consolidate response format

    def test_consolidate_raises_sdk_error(self):
        with mock.patch.object(HttpSDKPOSTConnection, 'get_response', side_effect=HttpError("Test HTTP Error")):
            with self.assertRaises(SDKError) as context:
                securities = Securities(self.securities_list)
                consolidation_keys = ['symbol', 'exchange']
                securities.consolidate(consolidation_keys)
            self.assertEqual(str(context.exception), "Test HTTP Error")

    def test_remove_errors(self):
        invalid_security_data = self.valid_security_data.copy()
        invalid_security_data['status'] = 'ERROR'
        invalid_security = Security(**invalid_security_data)
        securities_list = Securities([self.security_1, self.security_2, invalid_security])
        ret = securities_list.remove_errors()
        self.assertIsInstance(ret, list)
        self.assertEqual(len(ret), 2)
        self.assertIsInstance(ret[0], Security)
        self.assertIsInstance(ret[1], Security)

    def test_to_list_securities(self):
        security_data = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.0},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 2800.0}
        ]
        securities = Securities(security_data).to_list()

        self.assertIsInstance(securities, list)
        self.assertIsInstance(securities[0], dict)
        self.assertIsInstance(securities[1], dict)
        self.assertEqual(len(securities), 2)
        self.assertEqual(securities[0]['symbol'], 'AAPL')
        self.assertEqual(securities[1]['symbol'], 'GOOGL')
