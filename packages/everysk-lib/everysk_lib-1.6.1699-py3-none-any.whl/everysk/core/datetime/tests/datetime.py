###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from datetime import timezone
from zoneinfo import ZoneInfo
from everysk.core.datetime.date import date, Date
from everysk.core.datetime.datetime import datetime, DateTime
from everysk.core.unittests import TestCase, SkipTest


####################################################################################
#                                    Date tests                                    #
####################################################################################
class DateTimeTestCase(TestCase):

    def test_ensure_datetime(self):
        ret = DateTime.ensure(datetime(2023, 1, 1, 13, 59, 59))
        self.assertEqual(ret.__class__, DateTime)
        self.assertEqual(ret, DateTime(2023, 1, 1, 13, 59, 59, tzinfo=ZoneInfo('UTC')))

    def test_ensure_with_zone_info_datetime(self):
        ret = DateTime.ensure(datetime(2023, 1, 1, 13, 57, 58, 59, ZoneInfo('America/New_York')))
        self.assertEqual(ret.__class__, DateTime)
        self.assertEqual(ret, DateTime(2023, 1, 1, 13, 57, 58, 59, ZoneInfo('America/New_York')))

    def test_ensure_datetime_with_nanoseconds(self):
        try:
            from proto.datetime_helpers import DatetimeWithNanoseconds # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise SkipTest(str(error)) from error

        ret = DateTime.ensure(DatetimeWithNanoseconds(2023, 1, 1, 13, 59, 59, 1234))
        self.assertEqual(ret.__class__, DateTime)
        self.assertEqual(ret, DateTime(2023, 1, 1, 13, 59, 59, 1234))

    def test_ensure_datetime_invalid(self):
        with self.assertRaisesRegex(ValueError, "Invalid instantiation of class 'DateTime' from 'date'"):
            DateTime.ensure(date(2023, 1, 1))

    def test_is_datetime(self):
        self.assertTrue(DateTime.is_datetime(DateTime.now()))
        self.assertTrue(DateTime.is_datetime(DateTime(2023, 1, 1)))
        self.assertTrue(DateTime.is_datetime(DateTime(2023, 1, 1)))
        self.assertFalse(DateTime.is_datetime(Date.today()))
        self.assertFalse(DateTime.is_datetime('date'))
        self.assertFalse(DateTime.is_datetime(2022))

    def test_datetime_instance(self):
        ret = DateTime(year=b'\x07\xe7\t\x0e\x12:\x07\x0b\xca\t', month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None)
        self.assertEqual(ret, DateTime(2023, 9, 14, 18, 58, 7, 772617))

    def test_now_default_time_zone(self):
        now = DateTime.now()
        cmp = datetime.now(timezone.utc)
        self.assertEqual(now.__class__, DateTime)
        self.assertEqual(now.tzinfo, ZoneInfo('UTC'))
        self.assertEqual(now.strftime('%Y%m%d%H%M%S'), cmp.strftime('%Y%m%d%H%M%S'))

    def test_now_custom_time_zone(self):
        now = DateTime.now(ZoneInfo('America/New_York'))
        cmp = datetime.now(ZoneInfo('America/New_York'))
        self.assertEqual(now.__class__, DateTime)
        self.assertEqual(now.tzinfo, ZoneInfo('America/New_York'))
        self.assertEqual(now.strftime('%Y%m%d%H%M%S'), cmp.strftime('%Y%m%d%H%M%S'))

    def test_now_str_time_zone(self):
        now = DateTime.now('UTC')
        cmp = datetime.now(timezone.utc)
        self.assertEqual(now.__class__, DateTime)
        self.assertEqual(now.tzinfo, ZoneInfo('UTC'))
        self.assertEqual(now.strftime('%Y%m%d%H%M%S'), cmp.strftime('%Y%m%d%H%M%S'))

    def test_string_date_to_datetime_with_midday(self):
        result = DateTime(2023, 8, 15).force_time('MIDDAY')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 8, 15, 12, 0))

    def test_string_date_to_datetime_with_first_minute(self):
        result = DateTime(2023, 8, 15).force_time('FIRST_MINUTE')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 8, 15, 0, 0))

    def test_string_date_to_datetime_with_now(self):
        date_string = '20230815 ' + datetime.utcnow().strftime('%H:%M:%S.%f')
        expected_result = DateTime.strptime(date_string, '%Y%m%d %H:%M:%S.%f')
        result = DateTime(2023, 8, 15).force_time('NOW').replace(microsecond=expected_result.microsecond)
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, expected_result)

    def test_string_date_to_datetime_with_last_minute(self):
        result = DateTime(2023, 8, 15).force_time('LAST_MINUTE')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 8, 15, 23, 59, 59, 999999))

    def test_string_date_to_datetime_default_force_time(self):
        result = DateTime(2023, 8, 15).force_time()
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 8, 15, 12, 0))

    def test_string_date_to_datetime_invalid_force_time(self):
        with self.assertRaisesRegex(ValueError, "Invalid force_time. Please choose one of the following: NOW, MIDDAY, FIRST_MINUTE, LAST_MINUTE."):
            DateTime(2023, 8, 15).force_time('INVALID')

    def test_strptime_valid_datetime_string(self):
        result = DateTime.strptime('20230731 15:30:45')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 7, 31, 15, 30, 45))

    def test_strptime_or_null_valid_datetime_string(self):
        result = DateTime.strptime_or_null('20230731 15:30:45')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 7, 31, 15, 30, 45))

    def test_strptime_or_null_invalid_datetime_string(self):
        result = DateTime.strptime_or_null('invalid')
        self.assertEqual(result, None)

    def test_string_date_to_datetime_midday(self):
        obj = DateTime.string_date_to_date_time('20230101')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj, DateTime(2023, 1, 1, 12, 0))

    def test_string_date_to_datetime_now(self):
        datetime_now = DateTime.now()
        obj = DateTime.string_date_to_date_time('20230101', 'NOW')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj, DateTime(2023, 1, 1, datetime_now.hour, datetime_now.minute, datetime_now.second))

    def test_string_date_to_datetime_first_minute(self):
        obj = DateTime.string_date_to_date_time('20230101', 'FIRST_MINUTE')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj, DateTime(2023, 1, 1, 0, 0, 0))

    def test_string_date_to_datetime_last_minute(self):
        obj = DateTime.string_date_to_date_time('20230101', 'LAST_MINUTE')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj, DateTime(2023, 1, 1, 23, 59, 59))

    def test_fromisoformat_date(self):
        obj = DateTime.fromisoformat('2023-01-01')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')
        obj = DateTime.fromisoformat('20230101')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')

    def test_fromisoformat_utc(self):
        obj = DateTime.fromisoformat('2023-01-01T00:00:00+00:00')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')
        obj = DateTime.fromisoformat('2023-01-01 00:00:00+00:00')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')

    def test_fromisoformat_brt(self):
        obj = DateTime.fromisoformat('2023-01-01T00:00:00-03:00')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T03:00:00+00:00')
        obj = DateTime.fromisoformat('2023-01-01 00:00:00-03:00')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T03:00:00+00:00')

    def test_fromisoformat_z(self):
        obj = DateTime.fromisoformat('2023-01-01T00:00:00.000000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')
        obj = DateTime.fromisoformat('2023-01-01 00:00:00.000000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')

    def test_fromisoformat_z_with_more(self):
        obj = DateTime.fromisoformat('2023-01-01T00:00:00.0000000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')
        obj = DateTime.fromisoformat('2023-01-01 00:00:00.0000000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')

    def test_fromisoformat_z_with_less(self):
        obj = DateTime.fromisoformat('2023-01-01T00:00:00.00000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')
        obj = DateTime.fromisoformat('2023-01-01 00:00:00.00000Z')
        self.assertEqual(obj.__class__, DateTime)
        self.assertEqual(obj.astimezone(tz='UTC').isoformat(), '2023-01-01T00:00:00+00:00')

    def test_to_isoformat_standard_datetime(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).isoformat()
        self.assertEqual(result, '2023-07-31T12:34:56+00:00')

    def test_to_isoformat_microseconds(self):
        result = DateTime(2023, 1, 1, 0, 0, 0, microsecond=123456).isoformat()
        self.assertEqual(result, '2023-01-01T00:00:00.123456+00:00')

    def test_datetime_to_timestamp_standard_datetime(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).timestamp()
        self.assertEqual(result, 1690806896)

    def test_datetime_to_timestamp_zero_seconds(self):
        result = DateTime(2023, 1, 1, 0, 0, 0).timestamp()
        self.assertEqual(result, 1672531200)

    def test_timestamp_to_datetime_standard(self):
        result = DateTime.fromtimestamp(1699247696)
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 11, 6, 5, 14, 56))

    def test_timestamp_to_datetime_zero_seconds(self):
        result = DateTime.fromtimestamp(1672531200)
        self.assertEqual(result, DateTime(2023, 1, 1, 0, 0))

    def test_datetime_to_datetime_default_time(self):
        result = DateTime.date_to_date_time(Date(2023, 7, 31))
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 7, 31, 12, 0))

    def test_datetime_to_datetime_custom_time(self):
        result = DateTime.date_to_date_time(Date(2023, 1, 1), frc_time='LAST_MINUTE')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, DateTime(2023, 1, 1, 23, 59, 59, 999999))

    def test_adjust_time_zone_america_new_york(self):
        date_time_obj = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        expected_result = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('America/New_York'))
        result = date_time_obj.adjust_time_zone(time_zone='America/New_York')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, expected_result)

    def test_adjust_time_zone_default_time_zone(self):
        date_time_obj = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        default_result = date_time_obj.adjust_time_zone()
        expected_result = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        self.assertEqual(default_result, expected_result)

    def test_astimezone_america_new_york(self):
        date_time_obj = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        expected_result = DateTime(2023, 7, 31, 8, 34, 56, tzinfo=ZoneInfo('America/New_York'))
        result = date_time_obj.astimezone(tz='America/New_York')
        self.assertEqual(result.__class__, DateTime)
        self.assertEqual(result, expected_result)

    def test_astimezone_default_time_zone(self):
        date_time_obj = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        default_result = date_time_obj.astimezone()
        expected_result = DateTime(2023, 7, 31, 12, 34, 56, tzinfo=ZoneInfo('UTC'))
        self.assertEqual(default_result, expected_result)

    def test_datetime_to_pretty(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).strftime_pretty()
        self.assertEqual(result, 'Jul. 31, 2023, 12:34:56 p.m.')

    def test_datetime_to_pretty_time_only(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).strftime_pretty(just_time=True)
        self.assertEqual(result, '12:34 p.m.')

    def test_datetime_to_pretty_date_only(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).strftime_pretty(just_date=True)
        self.assertEqual(result, 'Jul. 31, 2023')

    def test_datetime_to_pretty_time_pm(self):
        result = DateTime(2023, 7, 31, 12, 34, 56).strftime_pretty(just_time=True)
        self.assertEqual(result, '12:34 p.m.')

    def test_datetime_to_pretty_time_am(self):
        result = DateTime(2023, 1, 1, 0, 0, 0).strftime_pretty(just_time=True)
        self.assertEqual(result, '12:00 a.m.')

    def test_datetime_to_pretty_raise_exception(self):
        with self.assertRaisesRegex(ValueError, 'Both "just_date" and "just_time" flags cannot be true'):
            DateTime(2023, 1, 1, 0, 0, 0).strftime_pretty(just_time=True, just_date=True)

    def test_datetime_to_string_default_format(self):
        result = DateTime(2023, 7, 31, 15, 30, 45).strftime()
        self.assertEqual(result, '20230731 15:30:45')  # Date string in the default format
        self.assertEqual(result, datetime(2023, 7, 31, 15, 30, 45).strftime('%Y%m%d %H:%M:%S'))

    def test_datetime_to_string_custom_format(self):
        custom_format = '%d/%m/%Y %H:%M:%S'
        result = DateTime(2023, 7, 31, 15, 30, 45).strftime(format=custom_format)
        self.assertEqual(result, '31/07/2023 15:30:45')  # Date string using custom format

    def test_date_strftime_or_null(self):
        self.assertEqual(DateTime.strftime_or_null(DateTime(2023, 7, 31, 13, 30, 0)), '20230731 13:30:00')
        self.assertEqual(DateTime.strftime_or_null(DateTime(2023, 7, 31, 13, 30, 0), format='%Y%m%d'), '20230731')
        self.assertEqual(DateTime.strftime_or_null(DateTime(2023, 7, 31, 13, 30, 0), format='%Y-%m-%d'), '2023-07-31')

        self.assertEqual(DateTime.strftime_or_null(datetime(2023, 7, 31, 13, 30, 0)), '20230731 13:30:00')
        self.assertEqual(DateTime.strftime_or_null(datetime(2023, 7, 31, 13, 30, 0), format='%Y%m%d'), '20230731')
        self.assertEqual(DateTime.strftime_or_null(datetime(2023, 7, 31, 13, 30, 0), format='%Y-%m-%d'), '2023-07-31')

        self.assertEqual(DateTime.strftime_or_null(Date(2023, 7, 31)), '20230731 00:00:00')
        self.assertEqual(DateTime.strftime_or_null(Date(2023, 7, 31), format='%Y%m%d'), '20230731')
        self.assertEqual(DateTime.strftime_or_null(Date(2023, 7, 31), format='%Y-%m-%d'), '2023-07-31')

        self.assertEqual(DateTime.strftime_or_null(date(2023, 7, 31)), '20230731 00:00:00')
        self.assertEqual(DateTime.strftime_or_null(date(2023, 7, 31), format='%Y%m%d'), '20230731')
        self.assertEqual(DateTime.strftime_or_null(date(2023, 7, 31), format='%Y-%m-%d'), '2023-07-31')

        self.assertIsNone(DateTime.strftime_or_null('2023-07-31'))
        self.assertIsNone(DateTime.strftime_or_null('2023-07-31', format='%Y%m%d'))
        self.assertIsNone(DateTime.strftime_or_null(None))
        self.assertIsNone(DateTime.strftime_or_null(None, format='%Y-%m-%d'))

    def test_get_hour_standard(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 34, 56).hour, 12)

    def test_get_hour_midnight(self):
        self.assertEqual(DateTime(2023, 1, 1, 0, 0, 0).hour, 0)

    def test_get_minute_standard(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 34, 56).minute, 34)

    def test_get_minute_midnight(self):
        self.assertEqual(DateTime(2023, 1, 1, 0, 0, 0).minute, 0)

    def test_get_second_standard(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 34, 56).second, 56)

    def test_get_second_midnight(self):
        self.assertEqual(DateTime(2023, 1, 1, 0, 0, 0).second, 0)

    def test_is_realtime_portfolio_date_false(self):
        self.assertFalse(DateTime(2023, 1, 1).is_today())

    def test_is_realtime_portfolio_date_true(self):
        self.assertTrue(Date.today().is_today())

    def test_datetime_quarter(self):
        self.assertEqual(DateTime(2023, 1, 1).quarter, 1)
        self.assertEqual(DateTime(2023, 3, 31).quarter, 1)
        self.assertEqual(DateTime(2023, 4, 1).quarter, 2)
        self.assertEqual(DateTime(2023, 6, 30).quarter, 2)
        self.assertEqual(DateTime(2023, 7, 1).quarter, 3)
        self.assertEqual(DateTime(2023, 9, 30).quarter, 3)
        self.assertEqual(DateTime(2023, 10, 1).quarter, 4)
        self.assertEqual(DateTime(2023, 12, 31).quarter, 4)

    def test_datetime_month_name(self):
        self.assertEqual(DateTime(2023, 1, 1).month_name, 'January')
        self.assertEqual(DateTime(2023, 2, 1).month_name, 'February')
        self.assertEqual(DateTime(2023, 3, 1).month_name, 'March')
        self.assertEqual(DateTime(2023, 4, 1).month_name, 'April')
        self.assertEqual(DateTime(2023, 5, 1).month_name, 'May')
        self.assertEqual(DateTime(2023, 6, 1).month_name, 'June')
        self.assertEqual(DateTime(2023, 7, 1).month_name, 'July')
        self.assertEqual(DateTime(2023, 8, 1).month_name, 'August')
        self.assertEqual(DateTime(2023, 9, 1).month_name, 'September')
        self.assertEqual(DateTime(2023, 10, 1).month_name, 'October')
        self.assertEqual(DateTime(2023, 11, 1).month_name, 'November')
        self.assertEqual(DateTime(2023, 12, 1).month_name, 'December')

    def test_datetime_week_of_year(self):
        self.assertEqual(DateTime(2023, 1, 1).week_of_year, 1)
        self.assertEqual(DateTime(2023, 6, 30).week_of_year, 26)
        self.assertEqual(DateTime(2023, 9, 30).week_of_year, 39)
        self.assertEqual(DateTime(2023, 12, 31).week_of_year, 53)

    def test_datetime_week_of_month(self):
        self.assertEqual(DateTime(2023, 1, 1).week_of_month, 1)
        self.assertEqual(DateTime(2023, 6, 8).week_of_month, 2)
        self.assertEqual(DateTime(2023, 9, 15).week_of_month, 3)
        self.assertEqual(DateTime(2023, 12, 31).week_of_month, 5)

    def test_datetime_day_name(self):
        self.assertEqual(DateTime(2023, 1, 1).day_name, 'Sunday')
        self.assertEqual(DateTime(2023, 1, 2).day_name, 'Monday')
        self.assertEqual(DateTime(2023, 1, 3).day_name, 'Tuesday')
        self.assertEqual(DateTime(2023, 1, 4).day_name, 'Wednesday')
        self.assertEqual(DateTime(2023, 1, 5).day_name, 'Thursday')
        self.assertEqual(DateTime(2023, 1, 6).day_name, 'Friday')
        self.assertEqual(DateTime(2023, 1, 7).day_name, 'Saturday')

    def test_datetime_day_of_year(self):
        self.assertEqual(DateTime(2023, 1, 1).day_of_year, 1)
        self.assertEqual(DateTime(2023, 6, 30).day_of_year, 181)
        self.assertEqual(DateTime(2023, 9, 30).day_of_year, 273)
        self.assertEqual(DateTime(2023, 12, 31).day_of_year, 365)

    def test_datetime_toordinal(self):
        self.assertEqual(DateTime(1, 1, 1, 12, 0).toordinal(), 1)
        self.assertEqual(DateTime(1, 12, 31, 12, 0).toordinal(start_date=Date(1, 1, 1)), 365)
        self.assertEqual(DateTime(2134, 12, 28, 12, 0).toordinal(start_date=Date(2020, 1, 1)), 42000)

    def test_datetime_get_last_day_of_week(self):
        ret = DateTime(2023, 1, 1, 12, 0).get_last_day_of_week()
        self.assertEqual(ret, DateTime(2023, 1, 7, 12, 0))
        self.assertEqual(ret.__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 7, 12, 0).get_last_day_of_week(), DateTime(2023, 1, 7, 12, 0))
        self.assertEqual(DateTime(2023, 1, 7, 12, 0).get_last_day_of_week(bizdays=True), DateTime(2023, 1, 6, 12, 0))
        self.assertEqual(DateTime(2023, 1, 1, 12, 0).get_last_day_of_week(bizdays=True, calendar='ANBIMA'), DateTime(2023, 1, 6, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_last_day_of_week(), DateTime(2023, 4, 8, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_last_day_of_week(bizdays=True), DateTime(2023, 4, 7, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_last_day_of_week(bizdays=True, calendar='ANBIMA'), DateTime(2023, 4, 6, 12, 0))

    def test_datetime_get_last_day_of_month(self):
        self.assertEqual(DateTime(2018, 5, 15, 12, 0).get_last_day_of_month().__class__, DateTime)
        self.assertEqual(DateTime(2018, 5, 15, 12, 0).get_last_day_of_month(), DateTime(2018, 5, 31, 12, 0))
        self.assertEqual(DateTime(2018, 5, 15, 12, 0).get_last_day_of_month(bizdays=True), DateTime(2018, 5, 31, 12, 0))
        self.assertEqual(DateTime(2018, 5, 15, 12, 0).get_last_day_of_month(bizdays=True, calendar='ANBIMA'), DateTime(2018, 5, 30, 12, 0))

    def test_datetime_get_last_day_of_quarter(self):
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_last_day_of_quarter().__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_last_day_of_quarter(), DateTime(2023, 3, 31, 12, 0))
        self.assertEqual(DateTime(2024, 5, 31, 12, 0).get_last_day_of_quarter(), DateTime(2024, 6, 30, 12, 0))
        self.assertEqual(DateTime(2023, 4, 15, 12, 0).get_last_day_of_quarter(), DateTime(2023, 6, 30, 12, 0))
        self.assertEqual(DateTime(2023, 7, 15, 12, 0).get_last_day_of_quarter(bizdays=True), DateTime(2023, 9, 29, 12, 0))
        self.assertEqual(DateTime(2023, 11, 15, 12, 0).get_last_day_of_quarter(bizdays=True, calendar='ANBIMA'), DateTime(2023, 12, 29, 12, 0))

    def test_datetime_get_last_day_of_year(self):
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_last_day_of_year().__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_last_day_of_year(), DateTime(2023, 12, 31, 12, 0))
        self.assertEqual(DateTime(2023, 7, 15, 12, 0).get_last_day_of_year(bizdays=True), DateTime(2023, 12, 29, 12, 0))
        self.assertEqual(DateTime(2023, 11, 15, 12, 0).get_last_day_of_year(bizdays=True, calendar='ANBIMA'), DateTime(2023, 12, 29, 12, 0))

    def test_datetime_is_last_day_of_week(self):
        self.assertTrue(DateTime(2023, 4, 8, 12, 0).is_last_day_of_week())
        self.assertFalse(DateTime(2023, 4, 7, 12, 0).is_last_day_of_week())
        self.assertFalse(DateTime(2023, 4, 6, 12, 0).is_last_day_of_week())
        self.assertFalse(DateTime(2023, 4, 8, 12, 0).is_last_day_of_week(bizdays=True))
        self.assertTrue(DateTime(2023, 4, 7, 12, 0).is_last_day_of_week(bizdays=True))
        self.assertTrue(DateTime(2023, 4, 6, 12, 0).is_last_day_of_week(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_last_day_of_month(self):
        self.assertTrue(DateTime(2023, 1, 31, 12, 0).is_last_day_of_month())
        self.assertFalse(DateTime(2023, 2, 27, 12, 0).is_last_day_of_month())
        self.assertTrue(DateTime(2023, 12, 31, 12, 0).is_last_day_of_month())
        self.assertTrue(DateTime(2023, 4, 28, 12, 0).is_last_day_of_month(bizdays=True))
        self.assertFalse(DateTime(2023, 4, 30, 12, 0).is_last_day_of_month(bizdays=True))
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_last_day_of_month(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_last_day_of_quarter(self):
        self.assertFalse(DateTime(2023, 1, 1, 12, 0).is_last_day_of_quarter())
        self.assertTrue(DateTime(2023, 3, 31, 12, 0).is_last_day_of_quarter())
        self.assertFalse(DateTime(2023, 4, 1, 12, 0).is_last_day_of_quarter())
        self.assertTrue(DateTime(2023, 6, 30, 12, 0).is_last_day_of_quarter())
        self.assertFalse(DateTime(2023, 7, 1, 12, 0).is_last_day_of_quarter())
        self.assertTrue(DateTime(2023, 9, 30, 12, 0).is_last_day_of_quarter())
        self.assertFalse(DateTime(2023, 10, 1, 12, 0).is_last_day_of_quarter())
        self.assertTrue(DateTime(2023, 12, 31, 12, 0).is_last_day_of_quarter())
        self.assertTrue(DateTime(2023, 12, 29, 12, 0).is_last_day_of_quarter(bizdays=True))
        self.assertTrue(DateTime(2023, 12, 29, 12, 0).is_last_day_of_quarter(bizdays=True, calendar='ANBIMA'))
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_last_day_of_quarter(bizdays=True))
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_last_day_of_quarter(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_last_day_of_year(self):
        self.assertFalse(DateTime(2023, 1, 1, 12, 0).is_last_day_of_year())
        self.assertFalse(DateTime(2023, 1, 31, 12, 0).is_last_day_of_year())
        self.assertTrue(DateTime(2023, 12, 31, 12, 0).is_last_day_of_year())
        self.assertTrue(DateTime(2023, 12, 29, 12, 0).is_last_day_of_year(bizdays=True))
        self.assertTrue(DateTime(2023, 12, 29, 12, 0).is_last_day_of_year(bizdays=True, calendar='ANBIMA'))
        self.assertFalse(DateTime(2023, 12, 30, 12, 0).is_last_day_of_year(bizdays=True))
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_last_day_of_year(bizdays=True, calendar='ANBIMA'))

    def test_datetime_get_first_day_of_week(self):
        self.assertEqual(DateTime(2023, 1, 1, 12, 0).get_first_day_of_week().__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 1, 12, 0).get_first_day_of_week(), DateTime(2023, 1, 1, 12, 0))
        self.assertEqual(DateTime(2023, 1, 5, 12, 0).get_first_day_of_week(), DateTime(2023, 1, 1, 12, 0))
        self.assertEqual(DateTime(2023, 1, 7, 12, 0).get_first_day_of_week(bizdays=True), DateTime(2023, 1, 2, 12, 0))
        self.assertEqual(DateTime(2023, 1, 1, 12, 0).get_first_day_of_week(bizdays=True, calendar='ANBIMA'), DateTime(2023, 1, 2, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_first_day_of_week(), DateTime(2023, 4, 2, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_first_day_of_week(bizdays=True), DateTime(2023, 4, 3, 12, 0))
        self.assertEqual(DateTime(2023, 4, 3, 12, 0).get_first_day_of_week(bizdays=True, calendar='ANBIMA'), DateTime(2023, 4, 3, 12, 0))
        self.assertEqual(DateTime(2023, 5, 4, 12, 0).get_first_day_of_week(bizdays=True, calendar='ANBIMA'), DateTime(2023, 5, 2, 12, 0))

    def test_datetime_get_first_day_of_month(self):
        self.assertEqual(DateTime(2023, 5, 15, 12, 0).get_first_day_of_month().__class__, DateTime)
        self.assertEqual(DateTime(2023, 5, 15, 12, 0).get_first_day_of_month(), DateTime(2023, 5, 1, 12, 0))
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_first_day_of_month(bizdays=True), DateTime(2023, 1, 2, 12, 0))
        self.assertEqual(DateTime(2023, 5, 15, 12, 0).get_first_day_of_month(bizdays=True, calendar='ANBIMA'), DateTime(2023, 5, 2, 12, 0))

    def test_datetime_get_first_day_of_quarter(self):
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_first_day_of_quarter().__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_first_day_of_quarter(), DateTime(2023, 1, 1, 12, 0))
        self.assertEqual(DateTime(2023, 4, 15, 12, 0).get_first_day_of_quarter(), DateTime(2023, 4, 1, 12, 0))
        self.assertEqual(DateTime(2023, 4, 15, 12, 0).get_first_day_of_quarter(bizdays=True), DateTime(2023, 4, 3, 12, 0))
        self.assertEqual(DateTime(2023, 11, 15, 12, 0).get_first_day_of_quarter(bizdays=True, calendar='ANBIMA'), DateTime(2023, 10, 2, 12, 0))

    def test_datetime_get_first_day_of_year(self):
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_first_day_of_year().__class__, DateTime)
        self.assertEqual(DateTime(2023, 1, 15, 12, 0).get_first_day_of_year(), DateTime(2023, 1, 1, 12, 0))
        self.assertEqual(DateTime(2023, 7, 15, 12, 0).get_first_day_of_year(bizdays=True), DateTime(2023, 1, 2, 12, 0))
        self.assertEqual(DateTime(2018, 11, 15, 12, 0).get_first_day_of_year(bizdays=True, calendar='ANBIMA'), DateTime(2018, 1, 2, 12, 0))

    def test_datetime_is_first_day_of_week(self):
        self.assertTrue(DateTime(2023, 1, 1, 12, 0).is_first_day_of_week())
        self.assertTrue(DateTime(2023, 4, 2, 12, 0).is_first_day_of_week())
        self.assertFalse(DateTime(2023, 1, 1, 12, 0).is_first_day_of_week(bizdays=True))
        self.assertTrue(DateTime(2018, 1, 2, 12, 0).is_first_day_of_week(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_first_day_of_month(self):
        self.assertTrue(DateTime(2023, 1, 1, 12, 0).is_first_day_of_month())
        self.assertTrue(DateTime(2023, 12, 1, 12, 0).is_first_day_of_month())
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_first_day_of_month())
        self.assertTrue(DateTime(2023, 1, 2, 12, 0).is_first_day_of_month(bizdays=True))
        self.assertFalse(DateTime(2023, 1, 1, 12, 0).is_first_day_of_month(bizdays=True))
        self.assertTrue(DateTime(2018, 1, 2, 12, 0).is_first_day_of_month(bizdays=True, calendar='ANBIMA'))
        self.assertFalse(DateTime(2018, 1, 1, 12, 0).is_first_day_of_month(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_first_day_of_quarter(self):
        self.assertTrue(DateTime(2023, 1, 1, 12, 0).is_first_day_of_quarter())
        self.assertFalse(DateTime(2023, 3, 31, 12, 0).is_first_day_of_quarter())
        self.assertTrue(DateTime(2023, 4, 1, 12, 0).is_first_day_of_quarter())
        self.assertFalse(DateTime(2023, 6, 30, 12, 0).is_first_day_of_quarter())
        self.assertTrue(DateTime(2023, 7, 1, 12, 0).is_first_day_of_quarter())
        self.assertFalse(DateTime(2023, 9, 30, 12, 0).is_first_day_of_quarter())
        self.assertTrue(DateTime(2023, 10, 1, 12, 0).is_first_day_of_quarter())
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_first_day_of_quarter())
        self.assertTrue(DateTime(2023, 1, 2, 12, 0).is_first_day_of_quarter(bizdays=True))
        self.assertTrue(DateTime(2018, 7, 2, 12, 0).is_first_day_of_quarter(bizdays=True))
        self.assertTrue(DateTime(2018, 1, 2, 12, 0).is_first_day_of_quarter(bizdays=True, calendar='ANBIMA'))

    def test_datetime_is_first_day_of_year(self):
        self.assertTrue(DateTime(2023, 1, 1, 12, 0).is_first_day_of_year())
        self.assertTrue(DateTime(2023, 1, 2, 12, 0).is_first_day_of_year(bizdays=True))
        self.assertTrue(DateTime(2018, 1, 2, 12, 0).is_first_day_of_year(bizdays=True, calendar='ANBIMA'))
        self.assertFalse(DateTime(2023, 12, 30, 12, 0).is_first_day_of_year(bizdays=True))
        self.assertFalse(DateTime(2023, 12, 31, 12, 0).is_first_day_of_year(bizdays=True, calendar='ANBIMA'))

    def test_datetime_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=5, periodicity='D').__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=5, periodicity='D'), DateTime(2023, 8, 5, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=2, periodicity='W'), DateTime(2023, 8, 14, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=1, periodicity='M'), DateTime(2023, 8, 31, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=2, periodicity='Y'), DateTime(2025, 7, 31, 12, 0))
        self.assertEqual(DateTime(2023, 4, 30, 12, 0).delta(period=1, periodicity='B', calendar='ANBIMA'), DateTime(2023, 5, 2, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=5.5, periodicity='D'), DateTime(2023, 8, 6, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=2.5, periodicity='W'), DateTime(2023, 8, 18, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=1.5, periodicity='M'), DateTime(2023, 8, 31, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=2.5, periodicity='Y'), DateTime(2025, 7, 31, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 4, 30, 12, 0).delta(period=1.5, periodicity='B', calendar='ANBIMA'), DateTime(2023, 5, 3, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=-5.5, periodicity='D'), DateTime(2023, 7, 26, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=-2.5, periodicity='W'), DateTime(2023, 7, 14, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=-1.5, periodicity='M'), DateTime(2023, 6, 30, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=-2.5, periodicity='Y'), DateTime(2021, 7, 31, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 4, 30, 12, 0).delta(period=-1.5, periodicity='B', calendar='ANBIMA'), DateTime(2023, 4, 27, 12, 0))

        with self.assertRaisesRegex(ValueError, "Invalid periodicity. Please choose one of the following: D, B, W, M, Y."):
            self.assertEqual(DateTime(2023, 7, 31, 12, 0).delta(period=5, periodicity='INVALID'), DateTime(2023, 8, 5, 12, 0))

        with self.assertRaisesRegex(ValueError, "Value out of range"):
            self.assertEqual(Date(2023, 7, 31).days_delta(50001), Date(2023, 8, 5))

    def test_datetime_days_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(5).__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(5), DateTime(2023, 8, 5, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(-5), DateTime(2023, 7, 26, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(5.5), DateTime(2023, 8, 6, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(-5.5), DateTime(2023, 7, 26, 0, 0))

        with self.assertRaisesRegex(ValueError, "Value out of range"):
            self.assertEqual(DateTime(2023, 7, 31, 12, 0).days_delta(50001), DateTime(2023, 8, 5, 12, 0))

    def test_datetime_bizdays_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(5).__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(5), DateTime(2023, 8, 7, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(-5), DateTime(2023, 7, 24, 12, 0))
        self.assertEqual(DateTime(2023, 4, 30, 12, 0).bizdays_delta(1, calendar='ANBIMA'), DateTime(2023, 5, 2, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(5.5), DateTime(2023, 8, 8, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(-5.5), DateTime(2023, 7, 21, 12, 0))
        self.assertEqual(DateTime(2023, 4, 30, 12, 0).bizdays_delta(1.5, calendar='ANBIMA'), DateTime(2023, 5, 3, 12, 0))

        with self.assertRaisesRegex(ValueError, "Value out of range"):
            self.assertEqual(DateTime(2023, 7, 31, 12, 0).bizdays_delta(50001), DateTime(2023, 8, 5, 12, 0))

    def test_datetime_weeks_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).weeks_delta(5).__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).weeks_delta(5), DateTime(2023, 9, 4, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).weeks_delta(-5), DateTime(2023, 6, 26, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).weeks_delta(5.5), DateTime(2023, 9, 8, 0, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).weeks_delta(-5.5), DateTime(2023, 6, 23, 0, 0))

    def test_datetime_months_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).months_delta(5).__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).months_delta(5), DateTime(2023, 12, 31, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).months_delta(-5), DateTime(2023, 2, 28, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).months_delta(5.5), DateTime(2023, 12, 31, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).months_delta(-5.5), DateTime(2023, 2, 28, 12, 0)) # ignoring float

    def test_datetime_months_delta_with_leap_year(self):
        self.assertEqual(DateTime(2020, 3, 31, 12, 0).months_delta(1), DateTime(2020, 4, 30, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).months_delta(1), DateTime(2020, 3, 29, 12, 0))
        self.assertEqual(DateTime(2020, 3, 31, 12, 0).months_delta(-1), DateTime(2020, 2, 29, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).months_delta(12), DateTime(2021, 2, 28, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).months_delta(-12), DateTime(2019, 2, 28, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).months_delta(12.5), DateTime(2021, 2, 28, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).months_delta(-12.5), DateTime(2019, 2, 28, 12, 0)) # ignoring float

    def test_datetime_years_delta(self):
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).years_delta(5).__class__, DateTime)
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).years_delta(5), DateTime(2028, 7, 31, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).years_delta(-5), DateTime(2018, 7, 31, 12, 0))
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).years_delta(5.5), DateTime(2028, 7, 31, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2023, 7, 31, 12, 0).years_delta(-5.5), DateTime(2018, 7, 31, 12, 0)) # ignoring float

    def test_datetime_years_delta_with_leap_year(self):
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(1), DateTime(2021, 2, 28, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(-1), DateTime(2019, 2, 28, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(4), DateTime(2024, 2, 29, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(-4), DateTime(2016, 2, 29, 12, 0))
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(4.5), DateTime(2024, 2, 29, 12, 0)) # ignoring float
        self.assertEqual(DateTime(2020, 2, 29, 12, 0).years_delta(-4.5), DateTime(2016, 2, 29, 12, 0)) # ignoring float

    def test_date_is_business_day(self):
        self.assertEqual(Date(2025, 1, 1).is_business_day(), True)
        self.assertEqual(Date(2025, 1, 1).is_business_day(calendar='ANBIMA'), False)
        self.assertEqual(Date(2025, 1, 20).is_business_day(calendar='NYSE'), False)

    def test_date_nearest_business_day(self):
        self.assertEqual(Date(2025, 1, 1).nearest_business_day(), Date(2025, 1, 1))
        self.assertEqual(Date(2025, 1, 1).nearest_business_day(direction='preceding'), Date(2025, 1, 1))
        self.assertEqual(Date(2025, 1, 1).nearest_business_day(calendar='ANBIMA'), Date(2025, 1, 2))
        self.assertEqual(Date(2025, 1, 20).nearest_business_day(calendar='NYSE'), Date(2025, 1, 21))
        self.assertEqual(Date(2025, 1, 1).nearest_business_day(direction='preceding', calendar='BVMF'), Date(2024, 12, 31))
        self.assertEqual(Date(2025, 4, 21).nearest_business_day(direction='preceding', calendar='BR'), Date(2025, 4, 17))
        self.assertEqual(Date(2025, 4, 18).nearest_business_day(direction='following', calendar='BR'), Date(2025, 4, 22))

        with self.assertRaisesRegex(ValueError, "Invalid direction. Choose 'following' or 'preceding'."):
            self.assertEqual(Date(2025, 1, 1).nearest_business_day(direction='INVALID'), "Invalid direction. Choose 'following' or 'preceding'.")

    def test_datetime_diff(self):
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0), periodicity='D'), 0)
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 5, 12, 0), periodicity='D'), 5)
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 14, 12, 0), periodicity='W'), 2)
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 31, 12, 0), periodicity='M'), 1)
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2025, 7, 31, 12, 0), periodicity='Y'), 2)
        self.assertEqual(DateTime.diff(start_date=DateTime(2023, 4, 30, 12, 0), end_date=DateTime(2023, 5, 2, 12, 0), periodicity='B', calendar='ANBIMA'), 1)
        self.assertEqual(DateTime.diff(start_date=datetime(2023, 4, 30, 12, 0), end_date=datetime(2023, 5, 2, 12, 0), periodicity='B', calendar='ANBIMA'), 1)

        with self.assertRaisesRegex(ValueError, "Invalid periodicity. Please choose one of the following: D, B, W, M, Y."):
            self.assertEqual(DateTime.diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 5, 12, 0), periodicity='INVALID'), 5)

    def test_datetime_days_diff(self):
        self.assertEqual(DateTime.days_diff(start_date=DateTime(2023, 8, 5, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0)), -5)
        self.assertEqual(DateTime.days_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 5, 12, 0)), 5)
        self.assertEqual(DateTime.days_diff(start_date=datetime(2023, 7, 31, 12, 0), end_date=datetime(2023, 8, 5, 12, 0)), 5)
        self.assertEqual(DateTime.days_diff(start_date=DateTime(2024, 2, 19, 12, 0), end_date=DateTime(2024, 2, 20, 12, 0)), 1)
        self.assertEqual(DateTime.days_diff(start_date=DateTime(2023, 5, 2, 12, 0), end_date=DateTime(2023, 4, 30, 12, 0)), -2)

    def test_datetime_bizdays_diff(self):
        self.assertEqual(DateTime.bizdays_diff(start_date=DateTime(2023, 8, 7, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0)), -5)
        self.assertEqual(DateTime.bizdays_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 8, 7, 12, 0)), 5)
        self.assertEqual(DateTime.bizdays_diff(start_date=DateTime(2023, 5, 2, 12, 0), end_date=DateTime(2023, 4, 30, 12, 0), calendar='ANBIMA'), -1)
        self.assertEqual(DateTime.bizdays_diff(start_date=datetime(2023, 5, 2, 12, 0), end_date=datetime(2023, 4, 30, 12, 0), calendar='ANBIMA'), -1)
        self.assertEqual(DateTime.bizdays_diff(start_date=DateTime(2024, 2, 19, 12, 0), end_date=DateTime(2024, 2, 20, 12, 0), calendar='ANBIMA'), 1)
        self.assertEqual(DateTime.bizdays_diff(start_date=DateTime(2023, 5, 2, 12, 0), end_date=DateTime(2023, 4, 30, 12, 0), calendar='ANBIMA'), -1)

    def test_datetime_weeks_diff(self):
        self.assertEqual(DateTime.weeks_diff(start_date=DateTime(2023, 9, 4, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0)), -5)
        self.assertEqual(DateTime.weeks_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 9, 4, 12, 0)), 5)
        self.assertEqual(DateTime.weeks_diff(start_date=datetime(2023, 7, 31, 12, 0), end_date=datetime(2023, 9, 4, 12, 0)), 5)

    def test_datetime_months_diff(self):
        self.assertEqual(DateTime.months_diff(start_date=DateTime(2023, 12, 31, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0)), -5)
        self.assertEqual(DateTime.months_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 12, 31, 12, 0)), 5)
        self.assertEqual(DateTime.months_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2023, 12, 29, 12, 0)), 4)
        self.assertEqual(DateTime.months_diff(start_date=datetime(2023, 7, 31, 12, 0), end_date=datetime(2023, 12, 29, 12, 0)), 4)

    def test_datetime_years_diff(self):
        self.assertEqual(DateTime.years_diff(start_date=DateTime(2028, 7, 31, 12, 0), end_date=DateTime(2023, 7, 31, 12, 0)), -5)
        self.assertEqual(DateTime.years_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2028, 7, 31, 12, 0)), 5)
        self.assertEqual(DateTime.years_diff(start_date=DateTime(2023, 7, 31, 12, 0), end_date=DateTime(2028, 7, 29, 12, 0)), 4)
        self.assertEqual(DateTime.years_diff(start_date=datetime(2023, 7, 31, 12, 0), end_date=datetime(2028, 7, 29, 12, 0)), 4)

    def test_datetime_range(self):
        self.assertEqual(DateTime.range(DateTime(2023, 1, 1), DateTime(2023, 1, 1)), [])
        self.assertListEqual(
            DateTime.range(DateTime(2021, 12, 23, 12, 0), DateTime(2022, 1, 2, 12, 0)),
            [
                DateTime(2021, 12, 23, 12, 0),
                DateTime(2021, 12, 24, 12, 0),
                DateTime(2021, 12, 25, 12, 0),
                DateTime(2021, 12, 26, 12, 0),
                DateTime(2021, 12, 27, 12, 0),
                DateTime(2021, 12, 28, 12, 0),
                DateTime(2021, 12, 29, 12, 0),
                DateTime(2021, 12, 30, 12, 0),
                DateTime(2021, 12, 31, 12, 0),
                DateTime(2022, 1, 1, 12, 0)
            ]
        )

        self.assertEqual(
            DateTime.range(datetime(2021, 12, 23, 12, 0), datetime(2022, 1, 2, 12, 0)),
            [
                DateTime(2021, 12, 23, 12, 0),
                DateTime(2021, 12, 24, 12, 0),
                DateTime(2021, 12, 25, 12, 0),
                DateTime(2021, 12, 26, 12, 0),
                DateTime(2021, 12, 27, 12, 0),
                DateTime(2021, 12, 28, 12, 0),
                DateTime(2021, 12, 29, 12, 0),
                DateTime(2021, 12, 30, 12, 0),
                DateTime(2021, 12, 31, 12, 0),
                DateTime(2022, 1, 1, 12, 0)
            ]
        )

        self.assertEqual(
            DateTime.range(DateTime(2023, 4, 18, 12, 0), DateTime(2023, 5, 3, 12, 0), periodicity='B', calendar='ANBIMA'),
            [
                DateTime(2023, 4, 18, 12, 0),
                DateTime(2023, 4, 19, 12, 0),
                DateTime(2023, 4, 20, 12, 0),
                DateTime(2023, 4, 24, 12, 0),
                DateTime(2023, 4, 25, 12, 0),
                DateTime(2023, 4, 26, 12, 0),
                DateTime(2023, 4, 27, 12, 0),
                DateTime(2023, 4, 28, 12, 0),
                DateTime(2023, 5, 2, 12, 0)]
        )

    def test_datetime_range_invalid_periodicity(self):
        with self.assertRaisesRegex(ValueError, 'Invalid periodicity. Please choose one of the following: D, B.'):
            DateTime.range(DateTime(2021, 12, 23, 12, 0), DateTime(2022, 1, 2, 12, 0), periodicity='invalid')

    def test_datetime_range_out_of_range_date(self):
        with self.assertRaisesRegex(ValueError, 'Value out of range'):
            DateTime.range(DateTime(2000, 1, 1, 12, 0), DateTime(2300, 1, 1, 12, 0))

    def test_datetime_days_range(self):
        self.assertEqual(DateTime.days_range(DateTime(2023, 1, 1, 12, 0), DateTime(2023, 1, 1, 12, 0)), [])
        self.assertListEqual(
            DateTime.days_range(DateTime(2021, 12, 23, 12, 0), DateTime(2022, 1, 2, 12, 0)),
            [
                DateTime(2021, 12, 23, 12, 0),
                DateTime(2021, 12, 24, 12, 0),
                DateTime(2021, 12, 25, 12, 0),
                DateTime(2021, 12, 26, 12, 0),
                DateTime(2021, 12, 27, 12, 0),
                DateTime(2021, 12, 28, 12, 0),
                DateTime(2021, 12, 29, 12, 0),
                DateTime(2021, 12, 30, 12, 0),
                DateTime(2021, 12, 31, 12, 0),
                DateTime(2022, 1, 1, 12, 0)
            ]
        )

        self.assertListEqual(
            DateTime.days_range(datetime(2021, 12, 23, 12, 0), datetime(2022, 1, 2, 12, 0)),
            [
                DateTime(2021, 12, 23, 12, 0),
                DateTime(2021, 12, 24, 12, 0),
                DateTime(2021, 12, 25, 12, 0),
                DateTime(2021, 12, 26, 12, 0),
                DateTime(2021, 12, 27, 12, 0),
                DateTime(2021, 12, 28, 12, 0),
                DateTime(2021, 12, 29, 12, 0),
                DateTime(2021, 12, 30, 12, 0),
                DateTime(2021, 12, 31, 12, 0),
                DateTime(2022, 1, 1, 12, 0)
            ]
        )

    def test_datetime_bizdays_range_with_calendar(self):
        self.assertListEqual(
            DateTime.bizdays_range(DateTime(2023, 4, 18, 12, 0), DateTime(2023, 5, 3, 12, 0), calendar='ANBIMA'),
            [
                DateTime(2023, 4, 18, 12, 0),
                DateTime(2023, 4, 19, 12, 0),
                DateTime(2023, 4, 20, 12, 0),
                DateTime(2023, 4, 24, 12, 0),
                DateTime(2023, 4, 25, 12, 0),
                DateTime(2023, 4, 26, 12, 0),
                DateTime(2023, 4, 27, 12, 0),
                DateTime(2023, 4, 28, 12, 0),
                DateTime(2023, 5, 2, 12, 0)]
        )

        self.assertListEqual(
            DateTime.bizdays_range(datetime(2023, 4, 18, 12, 0, tzinfo=ZoneInfo('UTC')), datetime(2023, 5, 3, 12, 0, tzinfo=ZoneInfo('UTC')), calendar='ANBIMA'),
            [
                DateTime(2023, 4, 18, 12, 0),
                DateTime(2023, 4, 19, 12, 0),
                DateTime(2023, 4, 20, 12, 0),
                DateTime(2023, 4, 24, 12, 0),
                DateTime(2023, 4, 25, 12, 0),
                DateTime(2023, 4, 26, 12, 0),
                DateTime(2023, 4, 27, 12, 0),
                DateTime(2023, 4, 28, 12, 0),
                DateTime(2023, 5, 2, 12, 0)]
        )

    def test_datetime_bizdays_range_without_calendar(self):
        self.assertEqual(
            DateTime.bizdays_range(DateTime(2023, 4, 18, 12, 0), DateTime(2023, 5, 3, 12, 0)),
            [
                DateTime(2023, 4, 18, 12, 0),
                DateTime(2023, 4, 19, 12, 0),
                DateTime(2023, 4, 20, 12, 0),
                DateTime(2023, 4, 21, 12, 0),
                DateTime(2023, 4, 24, 12, 0),
                DateTime(2023, 4, 25, 12, 0),
                DateTime(2023, 4, 26, 12, 0),
                DateTime(2023, 4, 27, 12, 0),
                DateTime(2023, 4, 28, 12, 0),
                DateTime(2023, 5, 1, 12, 0),
                DateTime(2023, 5, 2, 12, 0)]
        )
