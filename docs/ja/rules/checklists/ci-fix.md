---
source: rules/checklists/ci-fix.md
source_blob: d294e50730889aab6282e6bd50de7f567e76a5a2
canonical: false
---

# CI Fix Checklist 日本語参考訳

- 期待結果、証拠、ownership、readiness、repository trust は `$HOME\.codex\rules\development-workflow.md` に従う。
- 失敗している job、step、command、最初の意味ある error を特定する。
- failure を test、lint、typecheck、build、dependency、environment、flaky、external service に分類する。
- 可能なら同じ command、または最小の同等 command で local reproduction する。
- product behavior の failure は `codex-debug-discipline` で再現と原因を確立し、恒久変更は `codex-implementation` に渡す。
- test seam が stable な場合は regression check が意図した理由で失敗することを確認する。rerun-only、flaky failure、狭すぎる substitute は回帰証拠にしない。
- 最小限の関連変更で root cause を直す。
- 失敗していた command、または信頼できる local equivalent を再実行する。
- failure の証拠、fix、verification command、readiness、残る CI risk を active run note に記録する。
