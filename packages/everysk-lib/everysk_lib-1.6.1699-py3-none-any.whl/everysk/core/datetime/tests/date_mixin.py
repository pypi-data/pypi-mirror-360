###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.datetime import calendar, date_mixin
from everysk.core.unittests import TestCase, mock


@mock.patch.object(calendar, 'get_holidays')
class GetHolidaysTestCase(TestCase):

    def test_get_holidays(self, get_holidays: mock.MagicMock):
        result = date_mixin.get_holidays('BR', [2023, 2024])
        self.assertEqual(result, get_holidays.return_value)
        get_holidays.assert_called_once_with(calendar='BR', years=[2023, 2024])

    def test_empty_years(self, get_holidays: mock.MagicMock):
        result = date_mixin.get_holidays('BR')
        self.assertEqual(result, get_holidays.return_value)
        get_holidays.assert_called_once_with(calendar='BR')

    def test_empty_calendar(self, get_holidays: mock.MagicMock):
        result = date_mixin.get_holidays(None)
        self.assertDictEqual(result, {})
        get_holidays.assert_not_called()
