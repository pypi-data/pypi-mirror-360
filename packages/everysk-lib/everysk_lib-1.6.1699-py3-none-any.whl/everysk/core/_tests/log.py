###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# pylint: disable=protected-access
import json
import logging
import traceback
import sys
from logging import Logger as PythonLogger, DEBUG, StreamHandler
from time import sleep
from everysk.config import settings
from everysk.core import log as log_module
from everysk.core.unittests import TestCase, mock


@mock.patch.dict('os.environ', {'LOGGING_JSON': '1'})
class LoggerJsonTestCase(TestCase):
    # The first TestCase so we don't need to change the line number in the tests
    # every time we add a new test or lines

    def test_info_as_json(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('info')
            stream.write.assert_called_once_with(
                '{"message": "info", '
                '"severity": "INFO", '
                '"logName": "everysk-log-json-test", '
                '"labels": {}, '
                '"traceback": "", '
                '"http": {"headers": {}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "", '
                '"logging.googleapis.com/spanId": "", '
                '"logging.googleapis.com/trace_sampled": false, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 30, "function": "test_info_as_json"}}\n'
            )

    def test_info_as_json_with_labels(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('info with labels', extra={'labels': {'key': 'value'}})
            stream.write.assert_called_once_with(
                '{"message": "info with labels", '
                '"severity": "INFO", '
                '"logName": "everysk-log-json-test", '
                '"labels": {"key": "value"}, '
                '"traceback": "", '
                '"http": {"headers": {}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "", '
                '"logging.googleapis.com/spanId": "", '
                '"logging.googleapis.com/trace_sampled": false, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 48, "function": "test_info_as_json_with_labels"}}\n'
            )

    def test_info_as_json_with_labels_as_bytes(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('info with labels as bytes', extra={'labels': b'text'})
            stream.write.assert_called_once_with(
                '{"message": "info with labels as bytes", '
                '"severity": "INFO", '
                '"logName": "everysk-log-json-test", '
                '"labels": "text", '
                '"traceback": "", '
                '"http": {"headers": {}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "", '
                '"logging.googleapis.com/spanId": "", '
                '"logging.googleapis.com/trace_sampled": false, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 66, "function": "test_info_as_json_with_labels_as_bytes"}}\n'
            )

    def test_info_as_json_with_labels_with_bytes(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('info with labels with bytes', extra={'labels': {'key': b'text'}})
            stream.write.assert_called_once_with(
                '{"message": "info with labels with bytes", '
                '"severity": "INFO", '
                '"logName": "everysk-log-json-test", '
                '"labels": {"key": "text"}, '
                '"traceback": "", '
                '"http": {"headers": {}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "", '
                '"logging.googleapis.com/spanId": "", '
                '"logging.googleapis.com/trace_sampled": false, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 84, "function": "test_info_as_json_with_labels_with_bytes"}}\n'
            )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_info_as_json_with_http_headers(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('info with http headers', extra={'http_headers': {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'}})
            stream.write.assert_called_once_with(
                '{"message": "info with http headers", '
                '"severity": "INFO", '
                '"logName": "everysk-log-json-test", '
                '"labels": {}, '
                '"traceback": "", '
                '"http": {"headers": {"traceparent": "00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01"}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df", '
                '"logging.googleapis.com/spanId": "1c6c592f9e46e3fb", '
                '"logging.googleapis.com/trace_sampled": true, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 103, "function": "test_info_as_json_with_http_headers"}}\n'
            )

    def test_error_as_json(self):
        log = log_module.Logger(name='everysk-log-json-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            trace = ''
            try:
                raise ValueError('test')
            except ValueError:
                trace = traceback.format_exc()
                log.error('error')
            stream.write.assert_called_once_with(
                '{"message": "error", '
                '"severity": "ERROR", '
                '"logName": "everysk-log-json-test", '
                '"labels": {}, '
                f'"traceback": {json.dumps(trace)}, '
                '"http": {"headers": {}, "payload": {}, "response": {}}, '
                '"logging.googleapis.com/trace": "", '
                '"logging.googleapis.com/spanId": "", '
                '"logging.googleapis.com/trace_sampled": false, '
                '"logging.googleapis.com/sourceLocation":'
                ' {"file": "/var/app/src/everysk/core/_tests/log.py", "line": 126, "function": "test_error_as_json"}}\n'
            )


class LoggerTraceTestCase(TestCase):

    def setUp(self) -> None:
        self.trace_parts = log_module.DEFAULT_TRACE_PARTS.copy()

    def test_traceparent(self):
        traceparent = '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'
        log_module._parse_traceparent(traceparent, self.trace_parts)
        self.assertDictEqual(
            self.trace_parts,
            {
                'span_id': '1c6c592f9e46e3fb',
                'trace_id': '4bfa9e049143840bef864a7859f2e5df',
                'trace_sample': True,
                'version': '00',
            }
        )

    def test_parse_traceparent_invalid(self):
        traceparent = 'invalid'
        log_module._parse_traceparent(traceparent, self.trace_parts)
        self.assertDictEqual(
            self.trace_parts,
            {
                'span_id': '',
                'trace_id': '',
                'trace_sample': False,
                'version': '',
            }
        )

    def test_parse_x_cloud_trace_context(self):
        trace_context = '4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1'
        log_module._parse_x_cloud_trace_context(trace_context, self.trace_parts)
        self.assertDictEqual(
            self.trace_parts,
            {
                'span_id': '2048109991600514043',
                'trace_id': '4bfa9e049143840bef864a7859f2e5df',
                'trace_sample': True,
                'version': '',
            }
        )

    def test_parse_x_cloud_trace_context_invalid(self):
        trace_context = 'invalid'
        log_module._parse_x_cloud_trace_context(trace_context, self.trace_parts)
        self.assertDictEqual(
            self.trace_parts,
            {'span_id': '', 'trace_id': '', 'trace_sample': False, 'version': ''}
        )

    def test_get_trace_data_no_headers(self):
        self.assertDictEqual(
            log_module._get_trace_data(headers={}),
            {'span_id': '', 'trace_id': '', 'trace_sample': False, 'version': ''}
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_trace_data_traceparent(self):
        self.assertDictEqual(
            log_module._get_trace_data(headers={'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'}),
            {
                'span_id': '1c6c592f9e46e3fb',
                'trace_id': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'trace_sample': True,
                'version': '00',
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_trace_data_x_cloud_trace_context(self):
        self.assertDictEqual(
            log_module._get_trace_data(headers={'x-cloud-trace-context': '4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1'}),
            {
                'span_id': '2048109991600514043',
                'trace_id': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'trace_sample': True,
                'version': '',
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_trace_data_both(self):
        self.assertDictEqual(
            log_module._get_trace_data(headers={
                'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01',
                'x-cloud-trace-context': '4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1'
            }),
            {
                'span_id': '1c6c592f9e46e3fb',
                'trace_id': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'trace_sample': True,
                'version': '00',
            }
        )

    def test_get_traceback(self):
        try:
            raise ValueError('test')
        except ValueError:
            self.assertEqual(log_module._get_traceback(), traceback.format_exc())

    def test_get_traceback_no_traceback(self):
        self.assertEqual(log_module._get_traceback(), '')


class LoggerManagerTestCase(TestCase):

    def test_http_headers(self):
        with log_module.LoggerManager(http_headers={'X-Request-ID': '123'}):
            self.assertEqual(log_module.LoggerManager._extra.get(), {'http_headers': {'X-Request-ID': '123'}})

    def test_http_payload(self):
        with log_module.LoggerManager(http_payload={'data': '123'}):
            self.assertEqual(log_module.LoggerManager._extra.get(), {'http_payload': {'data': '123'}})

    def test_labels(self):
        with log_module.LoggerManager(labels={'data': '123'}):
            self.assertEqual(log_module.LoggerManager._extra.get(), {'labels': {'data': '123'}})

    def test_stacklevel(self):
        with log_module.LoggerManager(stacklevel=1):
            self.assertEqual(log_module.LoggerManager._extra.get(), {'stacklevel': 1})

    def test_traceback(self):
        trace = ''
        try:
            raise ValueError('test')
        except ValueError:
            trace = traceback.format_exc()

        with log_module.LoggerManager(traceback=trace):
            self.assertEqual(log_module.LoggerManager._extra.get(), {'traceback': trace})

    def test_empty(self):
        with log_module.LoggerManager():
            self.assertEqual(log_module.LoggerManager._extra.get(), {})

    def test_chain_managers(self):
        with log_module.LoggerManager(http_headers={'X-Request-ID': '123'}):
            with log_module.LoggerManager(http_payload={'data': '123'}):
                with log_module.LoggerManager(labels={'data': '123'}):

                    self.assertEqual(
                        log_module.LoggerManager._extra.get(),
                        {'http_headers': {'X-Request-ID': '123'}, 'http_payload': {'data': '123'}, 'labels': {'data': '123'}}
                    )
                self.assertEqual(
                    log_module.LoggerManager._extra.get(),
                    {'http_headers': {'X-Request-ID': '123'}, 'http_payload': {'data': '123'}}
                )
            self.assertEqual(
                log_module.LoggerManager._extra.get(),
                {'http_headers': {'X-Request-ID': '123'}}
            )

        self.assertEqual(log_module.LoggerManager._extra.get(), {})

    def test_reset(self):
        with log_module.LoggerManager(http_headers={'X-Request-ID': '123'}):
            log_module.LoggerManager.reset()
            self.assertEqual(log_module.LoggerManager._extra.get(), {})


class LoggerTestCase(TestCase):

    def test_logger_return(self):
        log = log_module.Logger('everysk-log-stdout-test')
        self.assertIsInstance(log._log, PythonLogger)

    def test_log_level(self):
        log = log_module.Logger(name='everysk-log-stdout-test')
        self.assertEqual(log._log.level, DEBUG)

    def test_log_propagate(self):
        log = log_module.Logger('everysk-log-stdout-test')
        self.assertFalse(log._log.propagate)

    def test_stdout_handler(self):
        log = log_module.Logger('everysk-log-stdout-test')
        handler = log._log.handlers[0]
        self.assertEqual(type(handler), StreamHandler)

    def test_handler_level(self):
        log = log_module.Logger(name='everysk-log-stdout-test')
        handler = log._log.handlers[0]
        self.assertEqual(handler.level, DEBUG)

    @mock.patch.dict('os.environ', {'LOGGING_JSON': 'false'})
    def test_handler_format(self):
        log = log_module.Logger(name='everysk-log-stdout-test')
        handler = log._log.handlers[0]
        self.assertEqual(
            handler.formatter._fmt,
            '%(asctime)s - %(levelname)s - %(labels)s - %(message)s'
        )

    def test_default_root_name(self):
        # https://everysk.atlassian.net/browse/COD-3212
        with self.assertRaisesRegex(ValueError, 'The name of the log could not be "root".'):
            log_module.Logger(name='root')


class LoggerExtraDataTestCase(TestCase):

    def setUp(self) -> None:
        self.log = log_module.Logger('everysk-log-extra-test')

    def test_http_headers(self):
        self.assertDictEqual(
            self.log._get_extra_data({'http_headers': {'X-Request-ID': '123'}}),
            {'labels': {}}
        )

    def test_http_headers_traceparent(self):
        self.assertDictEqual(
            self.log._get_extra_data({'http_headers': {'traceparent': '123'}}),
            {'http_headers': {'traceparent': '123'}, 'labels': {}}
        )

    def test_http_headers_x_cloud_trace_context(self):
        self.assertDictEqual(
            self.log._get_extra_data({'http_headers': {'x-cloud-trace-context': '123'}}),
            {'http_headers': {'x-cloud-trace-context': '123'}, 'labels': {}}
        )

    def test_http_payload(self):
        self.assertDictEqual(
            self.log._get_extra_data({'http_payload': {'data': '123'}}),
            {'http_payload': {'data': '123'}, 'labels': {}}
        )

    def test_another_key(self):
        self.assertDictEqual(
            self.log._get_extra_data({'another_key': '123'}),
            {'another_key': '123', 'labels': {}}
        )

    def test_http_headers_as_param(self):
        func = mock.MagicMock(return_value={'traceparent': 'flask'})
        self.log._http_functions = {'flask': {'http_headers': func}}
        with log_module.LoggerManager(http_headers={'traceparent': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({'http_headers': {'traceparent': 'param'}}, logging.ERROR),
                {'http_headers': {'traceparent': 'param'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_http_headers_as_manager(self):
        func = mock.MagicMock(return_value={'traceparent': 'flask'})
        self.log._http_functions = {'flask': {'http_headers': func}}
        with log_module.LoggerManager(http_headers={'traceparent': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({}, logging.ERROR),
                {'http_headers': {'traceparent': 'manager'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_http_payload_as_param(self):
        func = mock.MagicMock(return_value={'data': 'flask'})
        self.log._http_functions = {'flask': {'http_payload': func}}
        with log_module.LoggerManager(http_payload={'data': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({'http_payload': {'data': 'param'}}, logging.ERROR),
                {'http_payload': {'data': 'param'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_http_payload_as_manager(self):
        func = mock.MagicMock(return_value={'data': 'flask'})
        self.log._http_functions = {'flask': {'http_payload': func}}
        with log_module.LoggerManager(http_payload={'data': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({}, logging.ERROR),
                {'http_payload': {'data': 'manager'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_http_response_as_param(self):
        func = mock.MagicMock(return_value={'data': 'flask'})
        self.log._http_functions = {'flask': {'http_response': func}}
        with log_module.LoggerManager(http_response={'data': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({'http_response': {'data': 'param'}}, logging.ERROR),
                {'http_response': {'data': 'param'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_http_response_as_manager(self):
        func = mock.MagicMock(return_value={'data': 'flask'})
        self.log._http_functions = {'flask': {'http_response': func}}
        with log_module.LoggerManager(http_response={'data': 'manager'}):
            self.assertDictEqual(
                self.log._get_extra_data({}, logging.ERROR),
                {'http_response': {'data': 'manager'}, 'labels': {}}
            )
        func.assert_not_called()

    def test_traceback_with_manager(self):
        trace = ''
        try:
            raise ValueError('test')
        except ValueError:
            trace = traceback.format_exc()

        try:
            a = 1 / 0 # pylint: disable=unused-variable
        except ZeroDivisionError:
            with log_module.LoggerManager(traceback=trace):
                self.assertDictEqual(
                    self.log._get_extra_data({}, logging.ERROR),
                    {'traceback': trace, 'labels': {}}
                )

    def test_traceback(self):
        try:
            raise ValueError('test')
        except ValueError:
            self.assertDictEqual(
                self.log._get_extra_data({}, logging.ERROR),
                {'traceback': traceback.format_exc(), 'labels': {}}
            )

    def test_traceback_as_param(self):
        try:
            raise ValueError('test')
        except ValueError:
            self.assertDictEqual(
                self.log._get_extra_data({'traceback': 'Teste'}, logging.ERROR),
                {'traceback': 'Teste', 'labels': {}}
            )

    def test_labels_with_manager(self):
        with log_module.LoggerManager(labels={'data': '123'}):
            self.assertDictEqual(
                self.log._get_extra_data({}, logging.ERROR),
                {'labels': {'data': '123'}}
            )

    def test_labels_method(self):
        self.assertDictEqual(
            self.log._get_extra_data({'labels': {'data': '123'}}, logging.ERROR),
            {'labels': {'data': '123'}}
        )


@mock.patch.object(log_module.Logger, '_log')
class LoggerMethodsTestCase(TestCase):

    def test_critical(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.critical('critical')
        log_mock.log.assert_called_once_with(logging.CRITICAL, 'critical', extra={'labels': {}}, stacklevel=3)

    def test_debug(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.debug('debug')
        log_mock.log.assert_called_once_with(logging.DEBUG, 'debug', extra={'labels': {}}, stacklevel=3)

    def test_error(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.error('error')
        log_mock.log.assert_called_once_with(logging.ERROR, 'error', extra={'labels': {}}, stacklevel=3)

    def test_exception(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.exception('error')
        log_mock.log.assert_called_once_with(logging.ERROR, 'error', extra={'labels': {}}, stacklevel=3)

    def test_info(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.info('info')
        log_mock.log.assert_called_once_with(logging.INFO, 'info', extra={'labels': {}}, stacklevel=3)

    def test_warning(self, log_mock: mock.MagicMock):
        log = log_module.Logger('everysk-log-methods-test')
        log.warning('warning')
        log_mock.log.assert_called_once_with(logging.WARNING, 'warning', extra={'labels': {}}, stacklevel=3)

    def test_deprecated(self, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-log-deprecated')
        log.deprecated('Teste')
        log_mock.log.assert_called_once_with(logging.WARNING, 'DeprecationWarning: Teste', extra={'labels': {}}, stacklevel=3)

    def test_deprecated_once(self, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-log-deprecated')
        log.deprecated('Teste 1', show_once=True)
        log.deprecated('Teste 1', show_once=True)
        log_mock.log.assert_called_once_with(logging.WARNING, 'DeprecationWarning: Teste 1', extra={'labels': {}}, stacklevel=3)

    def test_deprecated_twice(self, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-log-deprecated')
        log.deprecated('Teste 2', show_once=False)
        log.deprecated('Teste 2', show_once=False)
        log_mock.log.assert_has_calls([
            mock.call(logging.WARNING, 'DeprecationWarning: Teste 2', extra={'labels': {}}, stacklevel=3),
            mock.call(logging.WARNING, 'DeprecationWarning: Teste 2', extra={'labels': {}}, stacklevel=3),
        ])


@mock.patch.object(log_module.Logger, '_log')
@mock.patch('everysk.core.slack.Slack')
class LoggerSlackTestCase(TestCase):

    def setUp(self) -> None:
        self.old_profile = settings.PROFILE
        self.old_slack_url = settings.SLACK_URL
        settings.PROFILE = 'PROD'
        settings.SLACK_URL = 'http://localhost'
        # This removes the module from the cache
        sys.modules.pop('unittest')

    def tearDown(self) -> None:
        settings.PROFILE = self.old_profile
        settings.SLACK_URL = self.old_slack_url
        # Put back the module
        import unittest # pylint: disable=unused-import, import-outside-toplevel

    def test_danger(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger')
        log_mock.log.assert_called_once_with(logging.ERROR, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url=settings.SLACK_URL)

    def test_warning(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Warning', message='Warning message', color='warning')
        log_mock.log.assert_called_once_with(logging.WARNING, 'Slack message: Warning -> Warning message', extra={'labels': {}}, stacklevel=3)
        slack.assert_called_once_with(title='Warning', message='Warning message', color='warning', url=settings.SLACK_URL)

    def test_success(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Success', message='Success message', color='success')
        log_mock.log.assert_called_once_with(logging.INFO, 'Slack message: Success -> Success message', extra={'labels': {}}, stacklevel=3)
        slack.assert_called_once_with(title='Success', message='Success message', color='success', url=settings.SLACK_URL)

    def test_not_url(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        settings.SLACK_URL = None
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger')
        log_mock.log.assert_called_once_with(logging.ERROR, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        slack.assert_not_called()

    def test_not_prod(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        settings.PROFILE = 'DEV'
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger')
        log_mock.log.assert_called_once_with(logging.ERROR, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        slack.assert_not_called()

    def test_in_tests(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        import unittest # pylint: disable=unused-import, import-outside-toplevel
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger')
        log_mock.log.assert_called_once_with(logging.ERROR, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        slack.assert_not_called()

    def test_method_url(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        log_mock.log.assert_called_once_with(logging.ERROR, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url='http://google.com')

    def test_slack_time_check(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        slack.assert_called_once_with(title='Error', message='Error message', color='danger', url='http://google.com')
        log_mock.log.assert_has_calls([
            mock.call(40, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3),
            mock.call(40, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        ])

    def test_slack_time_check_3s(self, slack: mock.MagicMock, log_mock: mock.MagicMock):
        log = log_module.Logger(name='everysk-lib-test-slack-message')
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        sleep(3)
        log.slack(title='Error', message='Error message', color='danger', url='http://google.com')
        slack.assert_has_calls([
            mock.call(title='Error', message='Error message', color='danger', url='http://google.com'),
            mock.call().send(),
            mock.call(title='Error', message='Error message', color='danger', url='http://google.com'),
            mock.call().send()
        ])
        log_mock.log.assert_has_calls([
            mock.call(40, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3),
            mock.call(40, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3),
            mock.call(40, 'Slack message: Error -> Error message', extra={'labels': {}}, stacklevel=3)
        ])


class LoggerFormatterTestCase(TestCase):

    def setUp(self) -> None:
        self.formatter = log_module.Formatter()

    def test_get_default_dict(self):
        self.assertDictEqual(
            self.formatter._get_default_dict(message='test', severity='INFO'),
            {'message': 'test', 'severity': 'INFO'}
        )

    def test_get_default_extra_dict(self):
        self.assertDictEqual(
            self.formatter._get_default_extra_dict(
                name='everysk-log-formatter-test',
                headers={'X-Request-ID': '123'},
                payload={'data': '123'},
                response={'result': 'ok'},
                traceback='',
                labels={'data': '123'}
            ),
            {
                'logName': 'everysk-log-formatter-test',
                'labels': {'data': '123'},
                'traceback': '',
                'http': {
                    'headers': {'X-Request-ID': '123'},
                    'payload': {'data': '123'},
                    'response': {'result': 'ok'}
                }
            }
        )

    def test_get_default_extra_dict_traceback(self):
        try:
            a = 1 / 0 # pylint: disable=unused-variable
        except ZeroDivisionError:
            self.assertDictEqual(
                self.formatter._get_default_extra_dict(
                    name='everysk-log-formatter-test',
                    headers={'X-Request-ID': '123'},
                    payload={'data': '123'},
                    response={'result': 'ok'},
                    traceback=traceback.format_exc(),
                    labels={'data': '123'}
                ),
                {
                    'logName': 'everysk-log-formatter-test',
                    'labels': {'data': '123'},
                    'traceback': traceback.format_exc(),
                    'http': {
                        'headers': {'X-Request-ID': '123'},
                        'payload': {'data': '123'},
                        'response': {'result': 'ok'},
                    }
                }
            )

    def test_get_default_gcp_dict(self):
        self.assertDictEqual(
            self.formatter._get_default_gcp_dict(headers={'X-Request-ID': '123'}, filename='test.py', line=10, func_name='test_func'),
            {
                'logging.googleapis.com/sourceLocation': {'file': 'test.py', 'function': 'test_func', 'line': 10},
                'logging.googleapis.com/spanId': '',
                'logging.googleapis.com/trace': '',
                'logging.googleapis.com/trace_sampled': False
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_default_gcp_dict_traceparent(self):
        self.assertDictEqual(
            self.formatter._get_default_gcp_dict(
                headers={'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'},
                filename='test.py',
                line=10,
                func_name='test_func'
            ),
            {
                'logging.googleapis.com/sourceLocation': {'file': 'test.py', 'function': 'test_func', 'line': 10},
                'logging.googleapis.com/spanId': '1c6c592f9e46e3fb',
                'logging.googleapis.com/trace': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'logging.googleapis.com/trace_sampled': True
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_default_gcp_dict_x_cloud_trace_context(self):
        self.assertDictEqual(
            self.formatter._get_default_gcp_dict(
                headers={'x-cloud-trace-context': '4bfa9e049143840bef864a7859f2e5df/2048109991600514043;o=1'},
                filename='test.py',
                line=10,
                func_name='test_func'
            ),
            {
                'logging.googleapis.com/sourceLocation': {'file': 'test.py', 'function': 'test_func', 'line': 10},
                'logging.googleapis.com/spanId': '2048109991600514043',
                'logging.googleapis.com/trace': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'logging.googleapis.com/trace_sampled': True
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_result_dict(self):
        record = logging.LogRecord(
            args=(),
            exc_info=None,
            func='test_func',
            level=logging.INFO,
            lineno=10,
            msg='test',
            name='everysk-log-formatter-test',
            pathname='test.py',
        )

        record.http_headers = {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'}
        record.http_payload = {'data': '123'}
        record.http_response = {'result': 'ok'}
        self.assertDictEqual(
            self.formatter._get_result_dict(record),
            {
                'message': 'test',
                'severity': 'INFO',
                'labels': {},
                'logName': 'everysk-log-formatter-test',
                'traceback': '',
                'http': {
                    'headers': {'traceparent': '00-4bfa9e049143840bef864a7859f2e5df-1c6c592f9e46e3fb-01'},
                    'payload': {'data': '123'},
                    'response': {'result': 'ok'},
                },
                'logging.googleapis.com/sourceLocation': {'file': 'test.py', 'function': 'test_func', 'line': 10},
                'logging.googleapis.com/spanId': '1c6c592f9e46e3fb',
                'logging.googleapis.com/trace': 'projects/g-project/traces/4bfa9e049143840bef864a7859f2e5df',
                'logging.googleapis.com/trace_sampled': True
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_get_result_dict_no_http(self):
        record = logging.LogRecord(
            args=(),
            exc_info=None,
            func='test_func',
            level=logging.INFO,
            lineno=10,
            msg='test',
            name='everysk-log-formatter-test',
            pathname='test.py',
        )

        self.assertDictEqual(
            self.formatter._get_result_dict(record),
            {
                'message': 'test',
                'severity': 'INFO',
                'labels': {},
                'logName': 'everysk-log-formatter-test',
                'traceback': '',
                'http': {
                    'headers': {},
                    'payload': {},
                    'response': {},
                },
                'logging.googleapis.com/sourceLocation': {'file': 'test.py', 'function': 'test_func', 'line': 10},
                'logging.googleapis.com/spanId': '',
                'logging.googleapis.com/trace': '',
                'logging.googleapis.com/trace_sampled': False
            }
        )

    @mock.patch.dict('os.environ', {'EVERYSK_GOOGLE_CLOUD_PROJECT': 'g-project'})
    def test_format_message(self):
        record = logging.LogRecord(
            args=(),
            exc_info=None,
            func='test_func',
            level=logging.INFO,
            lineno=10,
            msg='test',
            name='everysk-log-formatter-test',
            pathname='test.py',
        )
        result = self.formatter._get_result_dict(record)
        self.assertEqual(
            self.formatter.formatMessage(record),
            json.dumps(result)
        )


@mock.patch('time.time', mock.MagicMock(return_value=1704067200.0))
class LoggerStdoutTestCase(TestCase):

    def setUp(self) -> None:
        self.log = log_module.Logger(name='everysk-log-stdout-test')

    def test_critical_with_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.critical('with labels', extra={'labels': {}})
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - CRITICAL - {} - with labels\n')

    def test_critical_without_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.critical('without labels')
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - CRITICAL - {} - without labels\n')

    def test_debug_with_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.debug('with labels', extra={'labels': {}})
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - DEBUG - {} - with labels\n')

    def test_debug_without_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.debug('without labels')
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - DEBUG - {} - without labels\n')

    def test_error_with_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.error('with labels', extra={'labels': {}})
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - ERROR - {} - with labels\n')

    def test_error_without_labels(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.error('without labels')
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - ERROR - {} - without labels\n')

    def test_info_with_http_payload_in_bytes(self):
        with mock.patch.object(self.log._log.handler, 'stream') as stream:
            self.log.info('with http payload in bytes', extra={'http_payload': b'{"key": "value"}'})
            stream.write.assert_called_once_with('2024-01-01 00:00:00,000 - INFO - {} - with http payload in bytes\n')


@mock.patch.dict('os.environ', {'LOGGING_JSON': '1'})
class LoggerStackLevelTestCase(TestCase):

    def setUp(self):
        self.default_stacklevel = log_module.Logger._default_stacklevel

    def tearDown(self):
        log_module.Logger._default_stacklevel = self.default_stacklevel

    def test_default(self):
        log = log_module.Logger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/_tests/log.py', 'line': 943, 'function': 'test_default'}
            )

    def test_init(self):
        log_module.Logger._default_stacklevel = 2
        log = log_module.Logger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/log.py', 'line': 662, 'function': 'info'}
            )

        log = log_module.Logger(name='everysk-log-stacklevel-test', stacklevel=3)
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/_tests/log.py', 'line': 963, 'function': 'test_init'}
            )

    def test_class_atribute(self):
        log_module.Logger._default_stacklevel = 2
        log = log_module.Logger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/log.py', 'line': 662, 'function': 'info'}
            )

        class FakeLogger(log_module.Logger):
            stacklevel = 3
        log = FakeLogger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/_tests/log.py', 'line': 985, 'function': 'test_class_atribute'}
            )

    def test_method(self):
        log_module.Logger._default_stacklevel = 2
        log = log_module.Logger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test')
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/log.py', 'line': 662, 'function': 'info'}
            )

        log = log_module.Logger(name='everysk-log-stacklevel-test')
        with mock.patch.object(log._log.handler, 'stream') as stream:
            log.info('test', stacklevel=3)
            result = json.loads(stream.write.call_args[0][0])
            self.assertDictEqual(
                result['logging.googleapis.com/sourceLocation'],
                {'file': '/var/app/src/everysk/core/_tests/log.py', 'line': 1005, 'function': 'test_method'}
            )
