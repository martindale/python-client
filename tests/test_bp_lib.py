from unittest import TestCase
import json

import bp_lib as bp


MOCK_TEST_KEY = "test_y3w(lmx!@d3r1zh$$h0l2rq&5twdpv$m$7qlb6f4pzqmib4r*w"


class DecodeResponseTests(TestCase):
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


class HashTests(TestCase):
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


class VerifyNotificationTests(TestCase):
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