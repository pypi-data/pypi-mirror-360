###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import json
from everysk.core import exceptions
from everysk.core.serialize import dumps
from everysk.core.unittests import TestCase


class BaseExceptionTestCase(TestCase):
    cls = exceptions._BaseException # pylint: disable=protected-access

    def test_init_no_args(self):
        obj = self.cls()
        self.assertEqual(obj.msg, 'Application error.')
        self.assertEqual(str(obj), 'Application error.')

    def test_init_args(self):
        message = 'Error message.'
        obj = self.cls(message)
        self.assertEqual(obj.msg, message)
        self.assertEqual(str(obj), message)

    def test_args_later(self):
        message = 'Other test.'
        obj = self.cls('Test')
        obj.args = (message, )
        self.assertEqual(obj.args, (message,))
        self.assertEqual(obj.msg, message)
        self.assertEqual(str(obj), message)

    def test_args_error(self):
        with self.assertRaisesRegex(ValueError, "The 'args' value must be a tuple not <class 'str'>."):
            obj = self.cls('Test')
            obj.args = 'Other test'

    def test_init_kwargs(self):
        message = 'Error message.'
        obj = self.cls(msg=message)
        self.assertEqual(obj.msg, message)
        self.assertEqual(str(obj), message)


class DefaultErrorTestCase(BaseExceptionTestCase):
    cls = exceptions.DefaultError


class FieldValueErrorTestCase(BaseExceptionTestCase):
    cls = exceptions.FieldValueError

    def test_inheritance(self):
        self.assertTrue(issubclass(exceptions.FieldValueError, exceptions._BaseException)) # pylint: disable=protected-access
        self.assertTrue(issubclass(exceptions.FieldValueError, ValueError))


class HttpErrorTestCase(BaseExceptionTestCase):
    cls = exceptions.HttpError

    def test_init_no_args(self):
        obj = self.cls()
        self.assertEqual(obj.msg, 'Application error.')
        self.assertEqual(obj.status_code, 500)
        self.assertEqual(str(obj), '500 -> Application error.')

    def test_init_args(self):
        message = 'Error message.'
        obj = self.cls(message)
        self.assertEqual(obj.msg, message)
        self.assertEqual(obj.status_code, 500)
        self.assertEqual(str(obj), '500 -> Error message.')

    def test_init_kwargs(self):
        message = 'Error message.'
        obj = self.cls(msg=message, status_code=404)
        self.assertEqual(obj.msg, message)
        self.assertEqual(obj.status_code, 404)
        self.assertEqual(str(obj), '404 -> Error message.')

    def test_args_later(self):
        message = 'Other test.'
        obj = self.cls('Test')
        obj.args = (message, )
        self.assertEqual(obj.msg, message)
        self.assertEqual(str(obj), '500 -> Other test.')


class ReadonlyErrorTestCase(BaseExceptionTestCase):
    cls = exceptions.ReadonlyError


class RequiredErrorTestCase(BaseExceptionTestCase):
    cls = exceptions.RequiredError

class TestAPIError(TestCase):
    cls = exceptions.APIError

    def test_api_error_no_message(self):
        """ Test APIError with no message """
        error = self.cls(404, None)
        self.assertEqual(str(error), 'API ERROR')

    def test_api_error_with_message(self):
        """ Test APIError with JSON message """
        message = dumps({'error': 'Not Found', 'status': 404})
        error = self.cls(404, message)
        expected_output = json.dumps(json.loads(message), sort_keys=True, indent=2)
        self.assertEqual(str(error), expected_output)

    def test_api_error_message_handling(self):
        """ Test APIError handles incorrect JSON format in message """
        with self.assertRaises(json.JSONDecodeError):
            self.cls(400, 'Not a JSON string')

    def test_api_error_with_empty_message(self):
        """ Test APIError with empty message """
        error = self.cls(500, '')
        self.assertEqual(str(error), 'API ERROR')


class HandledExceptionTestCase(TestCase):

    cls = exceptions.HandledException

    def test_handled_exception_error_message(self):
        obj = self.cls()
        self.assertEqual(obj.msg, "Application error.")

    def test_inheritance(self):
        self.assertTrue(issubclass(exceptions.HandledException, exceptions._BaseException)) # pylint: disable=protected-access


class SDKExceptionsTestCase(TestCase):

    cls = exceptions.SDKInternalError

    def test_sdk_internal_error(self):
        obj = self.cls('SDK Internal Error')
        self.assertEqual(obj.msg, 'SDK Internal Error')

    def test_sdk_internal_error_inheritance(self):
        self.assertTrue(issubclass(exceptions.SDKInternalError, exceptions._BaseException)) # pylint: disable=protected-access

    def test_sdk_value_error(self):
        with self.assertRaises(exceptions.SDKValueError) as context:
            from everysk.sdk.entities import Portfolio # pylint: disable=no-name-in-module, import-outside-toplevel

            Portfolio(name="test", tags=['tag1', 'tag2']).to_query()

        self.assertEqual(str(context.exception), "Can't filter by Name and Tags at the same time")
