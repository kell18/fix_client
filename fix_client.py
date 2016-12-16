import socket
import functools


class FixClient:
    FIX_VERSION = "FIX.4.2"
    DELIM = ""

    def __init__(self, adaptor_sock, *extra_headers, msg_seq_num_init=1):
        self.extra_headers = extra_headers
        self.sock = adaptor_sock
        self.msg_seq_num = msg_seq_num_init

    def request(self, body_tags):
        request = self._build_request(body_tags)
        self.sock.send(request)
        resp = self._parse_response(self.sock.recv(1024).decode())
        if resp[self.Tags.MsgType] == "0" or resp[self.Tags.MsgType] == "1" or resp[self.Tags.MsgType] == "2":
            self.send_heartbeat(resp.get(self.Tags.TestReqID, None))
            resp = self._parse_response(self.sock.recv(1024).decode())
        return resp

    def send_heartbeat(self, test_req_ID=None):
        tags = ["35=0", *self.extra_headers]
        if test_req_ID:
            tags.append("112="+test_req_ID)
        self.sock.send(self._build_request(tags))

    def _build_request(self, tags):
        tags += ["34=" + str(self.msg_seq_num), *self.extra_headers]
        self.msg_seq_num += 1
        body_len = len(ascii("-".join(tags))) - 1
        head = ["8=" + self.FIX_VERSION, "9=" + str(body_len)]
        tailless = self.DELIM.join(head + tags) + self.DELIM
        checksum = functools.reduce(lambda prev, c: prev + ord(c), tailless, 0) % 256
        return (tailless + "10={:03d}".format(checksum) + self.DELIM).encode("ascii")

    def _parse_response(self, resp):
        *tags, tail = resp.split(self.DELIM)  # resp has a trailing DELIM, so skip it
        return { k: v for tag in tags for k, v in [tag.split("=")]  }

    class Tags:
        MsgType = "35"
        TestReqID = "112"
