###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import pickle
from everysk.core.exceptions import SigningError
from everysk.core.signing import sign, unsign
from everysk.core.unittests import TestCase, mock


@mock.patch.dict('os.environ', {'EVERYSK_SIGNING_KEY': 'c90d39a0e065'})
class SignTestCase(TestCase):
    maxDiff = None

    def test_string(self):
        data = sign('hello world')
        self.assertEqual(
            data,
            b'65121913be6cdc515b374e8c4b9e0c13a415a49a:hello world'
        )

    def test_bytes(self):
        data = sign(b'hello world')
        self.assertEqual(
            data,
            b'65121913be6cdc515b374e8c4b9e0c13a415a49a:hello world'
        )

    def test_bytearray(self):
        data = sign(bytearray([1, 2]))
        self.assertEqual(
            data,
            b'2c9a262668685179b8e1a437409ff3b9f62b6000:\x01\x02'
        )

    def test_pickle(self):
        data = sign(pickle.dumps('hello world'))
        self.assertEqual(
            data,
            b'17bac588109969e77738126f1468ea64fd78437a:\x80\x04\x95\x0f\x00\x00\x00\x00\x00\x00\x00\x8c\x0bhello world\x94.'
        )


@mock.patch.dict('os.environ', {'EVERYSK_SIGNING_KEY': 'c90d39a0e065'})
class UnsignTestCase(TestCase):

    def test_string(self):
        data = unsign(b'65121913be6cdc515b374e8c4b9e0c13a415a49a:hello world')
        self.assertEqual(data, b'hello world')

    def test_bytes(self):

        data = unsign(b'65121913be6cdc515b374e8c4b9e0c13a415a49a:hello world')
        self.assertEqual(data, b'hello world')

    def test_bytearray(self):
        data = unsign(b'2c9a262668685179b8e1a437409ff3b9f62b6000:\x01\x02')
        self.assertEqual(data, b'\x01\x02')

    def test_pickle(self):
        data = unsign(b'17bac588109969e77738126f1468ea64fd78437a:\x80\x04\x95\x0f\x00\x00\x00\x00\x00\x00\x00\x8c\x0bhello world\x94.')
        self.assertEqual(pickle.loads(data), 'hello world')

    def test_invalid_signing_key(self):
        with self.assertRaisesRegex(SigningError, 'Error trying to unsign data.'):
            unsign(b'201f7c5b76a9e9f683d54cec8a666897472d0f5f:hello world')
