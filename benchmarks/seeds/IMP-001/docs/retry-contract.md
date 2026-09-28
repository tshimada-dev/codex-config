# Retry contract

Automatic retries are allowed only for GET, HEAD, PUT and DELETE. POST is not retried
unless a future API explicitly accepts an idempotency key.

Retry transport failures represented by `OSError`, HTTP 429, and HTTP 503. Other
4xx/5xx responses are returned immediately.

Maximum attempts includes the first request. Before every retry, cancellation must be
checked. If `Retry-After` is an integer number of seconds, use it; otherwise use
backoff delays of 1, 2, 4, ... seconds. Never sleep after the final attempt.
