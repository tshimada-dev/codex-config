---
source: skills/codex-pr-readiness/SKILL.md
source_commit: 19c15b99d16f1e7fb1d3d795442637b05693ca81
canonical: false
---

# codex-pr-readiness 日本語参考訳

この文書は `skills/codex-pr-readiness/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

完了した作業を reviewable change に整える。commit、PR、CI follow-up、review comments 対応などで使う。

## Review Pass

1. status を確認する。
   - `git status --short --branch`
   - `git diff --stat`
   - targeted `git diff`
2. 自分の変更と無関係な user changes を分ける。
3. diff が一つの coherent story になっているか確認する。そうでない場合は分割を提案する。
4. 可能なら relevant verification を実行する。local verification が CI と異なる場合は、CI contract を満たしたと主張せず、差分を明示する。
5. summary を用意する。
   - what changed
   - why it changed
   - tests/checks
   - known risks

verification を skip した場合は、理由、実行すべきだった command、残る risk を明示する。

subagents が使える場合は、stage/commit 前の focused pre-PR review を reviewer agent に任せる。

## Commit Discipline

- user が依頼したときだけ commit する。
- requested change に属する files だけ stage する。
- unrelated user-owned changes は stage しない。
- secrets、logs、temporary files、unrelated formatting churn を入れない。
- non-interactive git commands を使う。
- pre-commit hooks が files を変更したら、commit 前に新しい diff を確認する。

## PR Body Shape

```markdown
## Summary
- ...

## Verification
- ...

## Notes
- ...
```

PR body は factual に保ち、過剰に売り込まない。

## Review Comments

review comments に対応する場合:

1. exact comment と surrounding diff を読む。
2. required change ごとに group する。
3. user が subset を選んだ場合は、選ばれた comments だけ直す。
4. stale、conflicting、product judgment が必要な comment は明記する。
