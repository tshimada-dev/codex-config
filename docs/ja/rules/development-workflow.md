---
source: rules/development-workflow.md
source_blob: dddc610a6499ed50775beeae793cb79b88a4b90a
canonical: false
---

# Development Workflow Contract 日本語参考訳

この文書は `rules/development-workflow.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 期待結果と証拠

重要な実装、bug fix、CI fix、review readiness では、変更前に「何が true になるべきか」、non-goals/constraints、観測方法を定義する。小さく低リスクな変更は `Outcome: ...; Evidence: ...` の1行でもよい。広い、曖昧、高リスクな作業では acceptance criterion に ID を付け、自動 check または明示的な manual probe と対応付ける。

情報源が競合する場合の優先順位は次のとおり。

1. safety、permission boundary、上位 instruction。
2. ユーザーの最新の明示判断と承認済み acceptance criteria。
3. リポジトリが source of truth として指定した specification または contract。
4. 既存 test と現在挙動。これらは証拠だが、自動的な最上位 authority ではない。

重要な競合を推測で解消せず、その挙動を所有する authority の判断を得る。

## 実装中のフィードバック

安定し、決定的で、対象挙動に関係し、実行コストが妥当な test seam がある場合は focused test-first loop を優先する。

1. focused check を追加または更新し、意図した理由で失敗することを確認する。
2. 期待結果を満たす最小の一貫した変更を実装する。
3. focused check を再実行し、証拠を失わずに refactor する。

この loop が実務上難しい場合は、恒久変更の前に理由を記録し、characterization test、CLI/HTTP reproduction、fixture、static/policy check、render inspection、browser probe、manual procedure など最小の信頼できる代替 feedback を用意する。flaky、無関係、理由不明の failure は有効な test-first の Red として扱わない。実装中の feedback は final verification の代わりにはならない。

## 所有権と遷移

- 調査は制約と検証候補を発見するが、product behavior を推測で決めない。
- planning は期待結果、判断、acceptance criteria、証拠、安全な slice を記録する。
- debugging は reproduction、hypothesis、root-cause evidence、regression-test shape を所有し、恒久変更は implementation へ渡す。
- implementation は product、test、configuration、documentation の恒久 patch と、verification から戻った修正を所有する。
- verification は統合結果を独立して確認する。finding は implementation へ戻し、その後再検証する。
- PR readiness は証拠と残存リスクを報告し、不足している必須検証を補ったことにはしない。

## 最終検証と readiness

final verification は実装後の統合結果を評価する。リポジトリの実コマンドを確認し、狭い check から始め、変更した contract に応じて広げる。local substitute と CI-equivalent evidence は区別する。

- `ready`: 必須証拠がすべて pass し、未解決の重要な競合がない。
- `conditionally-ready`: 必須証拠は pass したが、任意の証拠を skip した、または受容済みの残存リスクがある。
- `not-ready`: 必須証拠がない/失敗している、期待結果が未解決、または重要リスクが未受容。

## Repository Trust

未知または未信頼 repo の command は任意コード実行として扱い、`safe` profile で read-only inspection から始める。runtime/profile が trust を明示している場合、またはユーザーの明示確認後にだけ repository-controlled command を実行する。エージェント自身の判断だけでは trust を昇格させない。破壊的操作、remote mutation、publish、deploy、本番データ、migration、secret handling は引き続き明示承認を必要とする。
