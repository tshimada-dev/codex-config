# Settings contract

Precedence is defaults < config file < environment < CLI. A key is explicit when it
is present in the source mapping; `False`, `0`, and the empty string are therefore
valid overriding values.

Unknown keys are ignored. Merge operations must not mutate any caller-owned input
mapping because the same parsed mappings may be reused by validation and diagnostics.
