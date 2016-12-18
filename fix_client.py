import socket


class InvalidResponseException(Exception):
    """Raises when received invalid response message"""
    pass


class Tags:
    MsgType = "35"
    TestReqID = "112"


class FixClient:
    """QUIK Fix adapter client"""
    FIX_VERSION = "FIX.4.2"
    DELIM = chr(1)
    BUFF_SIZE = 1024

    def __init__(self, host_and_port, extra_headers, msg_seq_num_init=1):
        self.extra_headers = extra_headers # list of extra headers to each request
        self.host_and_port = host_and_port # (host, port) tuple
        self.msg_seq_num = msg_seq_num_init
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.sock.connect(self.host_and_port)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.sock.close()
        return exc_type is None  # Raise exceptions upwards


    def request_logon(self, is_reset_seq_num=True):
        reset = "Y" if is_reset_seq_num else "N"
        resp = self.request(["35=A", "141="+reset, "109=E5", "98=0", "108=53"])
        if resp[Tags.MsgType] == "A":
            return resp, True
        else:
            return resp, False

    def request(self, body_tags):
        self.send(body_tags)
        resp = self.parse_message(self.sock.recv(self.BUFF_SIZE).decode())
        if Tags.MsgType not in resp:
            raise InvalidResponseException("MsgType(35) tag is missing in the response.")
        if resp[Tags.MsgType] == "0" or resp[Tags.MsgType] == "1" or resp[Tags.MsgType] == "2":
            # for Heartbeat and TestRequest send back Heartbeat and return next received msg.
            self.send_heartbeat(resp.get(Tags.TestReqID, None))
            resp = self.parse_message(self.sock.recv(self.BUFF_SIZE).decode())
        return resp

    def send_heartbeat(self, test_req_ID=None):
        tags = ["35=0"]
        if test_req_ID:
            tags.append("112="+test_req_ID)
        self.send(tags)

    def send(self, tags):
        self.sock.send(self._build_request(tags))
        self.msg_seq_num += 1

    def parse_message(self, msg):
        *tags, _ = msg.split(self.DELIM)  # msg has a trailing DELIM, so skip it
        return {k: v for tag in tags for k, v in [tag.split("=")]}


    def _build_request(self, tags):
        tags += ["34=" + str(self.msg_seq_num), *self.extra_headers]
        body_len = len(ascii("-".join(tags))) - 1  # consider delim as 1 char
        head = ["8=" + self.FIX_VERSION, "9=" + str(body_len)]
        tailless = self.DELIM.join(head + tags) + self.DELIM
        checksum = sum(map(ord, tailless)) % 256
        return (tailless + "10={:03d}".format(checksum) + self.DELIM).encode("ascii")
