import unittest
from src.http_client import Client, Response, Transport


class Fake(Transport):
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0
    def send(self, method, url, *, body=None):
        self.calls += 1
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class ClientTest(unittest.TestCase):
    def test_success(self):
        t = Fake([Response(200,{})])
        self.assertEqual(Client(t).request("GET","/").status, 200)
        self.assertEqual(t.calls, 1)


if __name__ == "__main__":
    unittest.main()
