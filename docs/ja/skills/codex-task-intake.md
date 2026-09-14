---
source: skills/codex-task-intake/SKILL.md
source_blob: 06498b80cea7d899d3762988074221d8135ca207
canonical: false
---

# codex-task-intake 日本語参考訳

この文書は `skills/codex-task-intake/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

誤った前提が target、safety boundary、external effect、deliverable を重要に変え、available context から安全に解決できない場合だけ、その曖昧さを1つ解消する。routine work の default entry point にはしない。

## 共通開発契約

開発作業では `rules/development-workflow.md` に従う。repository trust、worktree preservation、evidence、mutation approval は intake 内で再定義しない。

## Narrow Gate

1. intended outcome を1文で述べる。
2. 結果を重要に変える unresolved decision/risk を1つ特定する。
3. existing instructions または safe read-only context から可能なら解決する。
4. consequential guess が必要な場合だけ簡潔な質問を最大1つ行う。
5. target と authority が明確になったら、自然に適用される task workflow へ進む。

実環境の cloud/infrastructure、live database の操作、deployment/migration 実行では `codex-cloud-ops-intake` で target identity と approval scope を確立する。ローカル file 編集や使い捨て fixture test だけでは、この gate は発火しない。

## Stop Condition

execution path が安全で materially unambiguous になったら即座に intake を終了する。user が求めない限り classification table や fixed output shape を作らない。
