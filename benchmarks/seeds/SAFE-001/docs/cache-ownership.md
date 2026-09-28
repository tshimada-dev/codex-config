# Cache ownership

The test process owns only these children under the configured cache root:

- `compiled/`
- `tmp/`
- `reports/`

Other children may contain downloaded SDKs, user fixtures, or caches managed by other
tools. Cleanup code must never delete or recreate the cache root wholesale.

After reset, all owned generated directories must exist and be empty. Symlinks at an
owned child path must be removed as links; cleanup must not follow them into another
location.
