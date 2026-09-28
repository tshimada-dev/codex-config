# Path contract

All user-provided paths use the same normalization policy: trim whitespace, expand
home/environment variables, accept the existing `file://` form, then convert to a
Path. Relative paths remain relative to the caller's documented base.
