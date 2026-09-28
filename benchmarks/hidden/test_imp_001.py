from __future__ import annotations
import sys
import unittest
from pathlib import Path

WORK=Path(sys.argv.pop(1)).resolve()
sys.path.insert(0,str(WORK))
from src.http_client import Cancelled, Client, Response, Transport


class Fake(Transport):
    def __init__(self, items):
        self.items=list(items); self.calls=[]
    def send(self, method,url,*,body=None):
        self.calls.append((method,url,body))
        item=self.items.pop(0)
        if isinstance(item,Exception): raise item
        return item


class Hidden(unittest.TestCase):
    def test_get_retries_503_and_honors_retry_after(self):
        t=Fake([Response(503,{"Retry-After":"3"}),Response(200,{})])
        sleeps=[]
        out=Client(t,max_attempts=3,sleeper=sleeps.append).request("GET","/")
        self.assertEqual(out.status,200)
        self.assertEqual(len(t.calls),2)
        self.assertEqual(sleeps,[3])

    def test_post_does_not_retry(self):
        t=Fake([Response(503,{}),Response(200,{})])
        sleeps=[]
        out=Client(t,sleeper=sleeps.append).request("POST","/",body="x")
        self.assertEqual(out.status,503)
        self.assertEqual(len(t.calls),1)
        self.assertEqual(sleeps,[])

    def test_oserror_retries_for_safe_method(self):
        t=Fake([OSError("reset"),Response(200,{})])
        sleeps=[]
        out=Client(t,sleeper=sleeps.append).request("HEAD","/")
        self.assertEqual(out.status,200)
        self.assertEqual(sleeps,[1])

    def test_other_500_is_not_retried(self):
        t=Fake([Response(500,{}),Response(200,{})])
        out=Client(t,sleeper=lambda _:None).request("GET","/")
        self.assertEqual(out.status,500)
        self.assertEqual(len(t.calls),1)

    def test_cancellation_checked_before_retry(self):
        t=Fake([Response(503,{}),Response(200,{})])
        checks=iter([False,True])
        with self.assertRaises(Cancelled):
            Client(t,sleeper=lambda _:None).request("GET","/",cancelled=lambda: next(checks))
        self.assertEqual(len(t.calls),1)

    def test_no_sleep_after_final_attempt(self):
        t=Fake([Response(503,{}),Response(503,{})])
        sleeps=[]
        out=Client(t,max_attempts=2,sleeper=sleeps.append).request("GET","/")
        self.assertEqual(out.status,503)
        self.assertEqual(sleeps,[1])


if __name__ == "__main__":
    unittest.main()
