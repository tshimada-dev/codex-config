# Cache lookup contract

An entry is **fresh** while `now < expires_at`. At the exact expiry boundary it
enters the stale window. While `expires_at <= now < stale_until`, the old value may
be served once per lookup and the caller is told to request refresh. These lookups
increment `stale`, not `hit` or `miss`.

At `now >= stale_until`, the entry is fully expired: return a miss, increment
`miss`, and do not request refresh.
