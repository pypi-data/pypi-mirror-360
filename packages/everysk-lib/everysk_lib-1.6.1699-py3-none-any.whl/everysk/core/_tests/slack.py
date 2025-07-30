###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
from everysk.core.exceptions import FieldValueError, ReadonlyError, RequiredError
from everysk.core import slack
from everysk.core.unittests import TestCase, mock


class SlackTestCase(TestCase):

    def setUp(self):
        slack.Slack._cache.flush_all()

    def tearDown(self) -> None:
        slack.Slack._cache.flush_all()

    def test_is_json(self):
        message = "The field 'is_json' value cannot be changed."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            is_json=False
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj.is_json = False

    def test_title(self):
        message = 'The title attribute is required.'
        self.assertRaisesRegex(RequiredError, message, slack.Slack, message='Message')

    def test_message(self):
        message = 'The message attribute is required.'
        self.assertRaisesRegex(RequiredError, message, slack.Slack, title='Title')

    def test_choices(self):
        message = r"The value 'banana' for field 'color' must be in this list \(None, 'danger', 'success', 'warning'\)."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            color='banana'
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj.color = 'banana'

    def test_color_map(self):
        message = "The field '_color_map' value cannot be changed."
        self.assertRaisesRegex(
            FieldValueError,
            message,
            slack.Slack,
            title='Test',
            message='Message',
            _color_map={'banana': '#f3f3f3'}
        )
        with self.assertRaisesRegex(FieldValueError, message):
            obj = slack.Slack(title='Test', message='Message')
            obj._color_map = {'banana': '#f3f3f3'}

        with self.assertRaisesRegex(ReadonlyError, 'This field value cannot be changed.'):
            obj = slack.Slack(title='Test', message='Message')
            obj._color_map['banana'] = '#f3f3f3'

    def test_get_payload(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertDictEqual(
            obj.get_payload(),
            {
                'attachments': [{
                    'color': '#000000',
                    'blocks': [
                        {
                            'text': {'emoji': True, 'text': 'Test', 'type': 'plain_text'},
                            'type': 'header'
                        },
                        {'type': 'divider'},
                        {
                            'text': {'text': 'Message', 'type': 'mrkdwn'},
                            'type': 'section'
                        },
                        {'type': 'divider'}
                    ],
                }]
            }
        )

    @mock.patch.object(slack.Slack, 'get_response')
    def test_send(self, get_response: mock.MagicMock):
        slack.Slack(title='Test', message='Message').send()
        get_response.assert_called_once_with()

    @mock.patch.object(slack.Slack, 'get_response')
    def test_send_twice(self, get_response: mock.MagicMock):
        slack.Slack(title='Test', message='Message').send()
        slack.Slack(title='Test', message='Message').send()
        get_response.assert_called_once_with()

    def test_is_title_cached(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertFalse(obj.is_title_cached())
        self.assertTrue(obj.is_title_cached())

    def test_is_message_cached(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertFalse(obj.is_message_cached())
        self.assertTrue(obj.is_message_cached())

    def test_make_title_key(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertEqual(obj.make_title_key(), 'everysk-core-slack-640ab2bae07bedc4c163f679a746f7ab7fb5d1fa')

    def test_make_message_key(self):
        obj = slack.Slack(title='Test', message='Message')
        self.assertEqual(obj.make_message_key(), 'everysk-core-slack-68f4145fee7dde76afceb910165924ad14cf0d00')

    def test_can_send_title(self):
        obj = slack.Slack(title='Test', message='Message01')
        self.assertTrue(obj.can_send())

        obj = slack.Slack(title='Test', message='Message02')
        self.assertFalse(obj.can_send())

    def test_can_send_message(self):
        obj = slack.Slack(title='Test01', message='Message')
        self.assertTrue(obj.can_send())

        obj = slack.Slack(title='Test02', message='Message')
        self.assertFalse(obj.can_send())
