import unittest
from fix_client import FixClient


class TestFixClient(unittest.TestCase):

    def setUp(self):
        self.cli = FixClient(None, ["d=f"], msg_seq_num_init=1)
        self.req = self.cli._build_request(["a=b", "c=2"]).decode()
        self.resp = self.req

    def test_build_request(self):
        self.assertIn("a=b", self.req)
        self.assertIn("c=2", self.req)
        self.assertIn("d=f", self.req)

    def test_build_request_msg_length(self):
        self.assertIn("9=17", self.req)

    def test_build_request_checksum(self):
        self.assertIn("10=176", self.req)

    def test_parse_response(self):
        tags = self.cli.parse_message(self.resp)
        self.assertEqual(tags["a"], "b")
        self.assertEqual(tags["d"], "f")
        self.assertEqual(tags["9"], "17")
