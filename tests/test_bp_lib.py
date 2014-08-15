import unittest
import json

import bp_lib as bp
import bp_options as bp_opts


MOCK_TEST_KEY = "test_y3w(lmx!@d3r1zh$$h0l2rq&5twdpv$m$7qlb6f4pzqmib4r*w"

# Set this to False to skip invoice creation tests. This requires your apiKey to be set in bp_options.
# WARNING: Setting this to True will create an open invoice to your account.
TEST_INVOICES = True and bp_opts.bpOptions['apiKey']


class DecodeResponseTests(unittest.TestCase):
    def setUp(self):
        self.invalid_input_response = "testing invalid json"
        self.no_input = ""
        self.valid_input = '{"test": "response"}'

    def test_no_input(self):
        self.assertTrue(isinstance(bp.bpDecodeResponse(self.no_input), basestring), "Expected string error")

    def test_invalid_input(self):
        self.assertRaises(ValueError, bp.bpDecodeResponse, self.invalid_input_response)

    def test_valid_input(self):
        self.assertTrue(isinstance(bp.bpDecodeResponse(self.valid_input), dict), "Expected dict")


class HashTests(unittest.TestCase):
    def setUp(self):
        self.apiKey = MOCK_TEST_KEY
        self.apiKey2 = MOCK_TEST_KEY + "_2"

    def test_hash_valid_comparison(self):
        self.assertEqual(bp.bpHash("valid", self.apiKey), bp.bpHash("valid", self.apiKey), "Expected deterministic output from hashing")

    def test_hash_invalid_comparison(self):
        self.assertNotEqual(bp.bpHash("invalid", self.apiKey), bp.bpHash("invalid2", self.apiKey), "Expected different inputs to have different hashes")

    def test_hash_invalid_key_comparison(self):
        self.assertNotEqual(bp.bpHash("valid", self.apiKey), bp.bpHash("valid", self.apiKey2), "Expected different keys to have different hashes")

    def test_hash_invalid_unicode_comparison(self):
        self.assertNotEqual(bp.bpHash(unicode("valid"), self.apiKey), bp.bpHash(str("valid"), self.apiKey2), "Expected different keys to have different hashes")


class VerifyNotificationTests(unittest.TestCase):
    def setUp(self):
        self.apiKey = MOCK_TEST_KEY
        posData = {'customer_id': 1000000}

        self.postData = json.dumps({
            "id": 1,
            "url": "http://example.com/example_invoice1",
            "posData": json.dumps({"posData": posData, "hash": bp.bpHash(str(posData), self.apiKey)}),
            "status": "complete",
            "price": 5,
            "currency": "USD",
            "btcPrice": 0.00001
        })
        self.invalidPostData = json.dumps({
            "id": 1,
            "url": "http://example.com/example_invoice1",
            "posData": json.dumps({"posData": posData, "hash": bp.bpHash("invalid!", self.apiKey)}),
            "status": "complete",
            "price": 5,
            "currency": "USD",
            "btcPrice": 0.00001
        })

    def test_valid_notification(self):
        self.assertFalse(isinstance(bp.bpVerifyNotification(self.apiKey, self.postData), basestring), "Expected verification to pass.")

    def test_invalid_notification(self):
        self.assertTrue(isinstance(bp.bpVerifyNotification(self.apiKey, self.invalidPostData), basestring), "Expected verification to fail.")


class FakeBuildOpener():
    def __init__(self, *args):
        self.addheaders = []

    def open(self, *args):
        return FakeOpen()


class FakeOpen():
    def read(self, *args):
        return json.dumps({'status': 'new', 'invoiceTime': 1393950046292, 'currentTime': 1393950046520, 'url': 'https://bitpay.com/invoice?id=aASDF2jh4ashkASDfh234', 'price': 1, 'btcPrice': '1.0000', 'currency': 'BTC', 'posData': '{"posData": "fish", "hash": "ASDfkjha452345ASDFaaskjhasdlfkflkajsdf"}', 'expirationTime': 1393950946292, 'id': 'aASDF2jh4ashkASDfh234'})


class CurlTests(unittest.TestCase):
    def setUp(self):
        self.apiKey = MOCK_TEST_KEY
        bp.urllib2.build_opener = FakeBuildOpener

    def test_valid_curl(self):
        response = bp.bpCurl("test url", self.apiKey)
        self.assertTrue(response.get("status", False), "Expected response to contain correct status info.")

    def test_invalid_curl_url(self):
        response = bp.bpCurl("", self.apiKey)
        self.assertTrue(response.get("error", False), "Expected error to return.")

    def test_invalid_curl_api(self):
        response = bp.bpCurl("test url", "")
        self.assertTrue(response.get("error", False), "Expected error to return.")

    def tearDown(self):
        reload(bp)


@unittest.skipUnless(TEST_INVOICES, "Invoice testing is disabled.")
class CreateInvoiceTests(unittest.TestCase):
    def setUp(self):
        pass