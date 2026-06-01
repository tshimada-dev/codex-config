---
source: rules/checklists/ci-fix.md
source_commit: dd1c94c
canonical: false
---

# CI Fix Checklist 日本語参考訳

- 失敗している job、step、command、最初の意味ある error を特定する。
- failure を test、lint、typecheck、build、dependency、environment、flaky、external service に分類する。
- 可能なら同じ command、または最小の同等 command で local reproduction する。
- 最小限の関連変更で root cause を直す。
- 失敗していた command、または信頼できる local equivalent を再実行する。
- failure の証拠、fix、verification command、残る CI risk を active run note に記録する。
