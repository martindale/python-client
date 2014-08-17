import unittest
import json
import time

import bp_lib as bp
import bp_options as bp_opts


MOCK_TEST_KEY = "test_y3w(lmx!@d3r1zh$$h0l2rq&5twdpv$m$7qlb6f4pzqmib4r*w"
REAL_API_KEY = bp_opts.bpOptions['apiKey']

# Set this to False to skip invoice creation tests. This requires your apiKey to be set in bp_options.
# WARNING: Setting this to True will create an open invoice to your account.
TEST_INVOICES = False and bp_opts.bpOptions['apiKey']


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
        pos_data = {'customer_id': 1000000}

        self.postData = json.dumps({
            "id": 1,
            "url": "http://example.com/example_invoice1",
            "posData": json.dumps({"posData": pos_data, "hash": bp.bpHash(str(pos_data), self.apiKey)}),
            "status": "complete",
            "price": 5,
            "currency": "USD",
            "btcPrice": 0.00001
        })
        self.invalidPostData = json.dumps({
            "id": 1,
            "url": "http://example.com/example_invoice1",
            "posData": json.dumps({"posData": pos_data, "hash": bp.bpHash("invalid!", self.apiKey)}),
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
    def __init__(self):
        pass

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
        self.apiKey = REAL_API_KEY
        self.price = 0.005
        self.price_type = bp_opts.bpOptions['currency']
        self.invoice_response = bp.bpCreateInvoice("OrderId: " + str(time.time()), self.price, "test posData")

    def test_valid_invoice_status(self):
        self.assertTrue(self.invoice_response.get("status", False), "Expected invoice to be valid.")

    def test_valid_invoice_data(self):
        pos_data = bp.bpVerifyNotification(self.apiKey, json.dumps(self.invoice_response))  # Need to convert this back to a json string, which is what we will expect from POST data.
        self.assertFalse(isinstance(pos_data, basestring), "Expected invoice verification to be valid.")

    def test_valid_invoice_price(self):
        self.assertEqual(float(self.invoice_response.get("btcPrice", False)), self.price, "Expected invoice to have the specified price.")
        self.assertEqual(str(self.invoice_response.get("currency", False)), str(self.price_type), "Expected invoice to have the specified currency type.")

    def test_valid_invoice_unpaid(self):
        self.assertEqual(float(self.invoice_response.get("btcPaid", False)), float(0), "Expected invoice to have been unpaid.")

    def test_valid_invoice_url(self):
        self.assertTrue(self.invoice_response.get("url", False), "Expected invoice to have a proper url.")

