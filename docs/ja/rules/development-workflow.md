---
source: rules/development-workflow.md
source_blob: e69d7704363bf25346ddb77bd267e7ee5096eb75
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

## ワークフローphase

plan、run note、handoff では次のphase名を使う。

- `intake`: request、risk、authority、execution pathを分類する。
- `scouting`: repository constraints、conventions、実行可能なcheckを発見する。
- `planning`: decision、acceptance evidence、dependencies、安全なsliceを記録する。
- `debugging`: defectを再現し、hypothesisを検証し、root causeとregression evidenceを確立する。
- `implementation`: product/repository behaviorの恒久変更を行い、focused feedbackを得る。
- `verification`: 統合結果を期待結果に対して独立に評価する。
- `readiness`: evidence、残存risk、review/release readinessを分類する。
- `paused`: 意図的な中断中に再開可能な状態を保存する。
- `handoff`: current state、evidence、decision、次のowned actionを引き継ぐ。

evidenceにより期待結果が変わる場合やverification findingが戻る場合、phaseは前段へloopしてよい。`paused`と`handoff`はcontinuity stateであり、implementation workを所有しない。

## 所有権と遷移

成果物を2種類に分ける。

- product/repository behavior artifactは、source、test、configuration、migration、user-facing documentation、script、workflow policyなど、出荷挙動またはrepository operationを定義する恒久fileである。これらのeditはimplementationが所有する。
- workflow/evidence artifactは、intake note、scouting finding、plan、debug transcript、run note、verification result、readiness report、commit message、PR textなど、作業の理解と評価を記録する。これらはevidenceを生成するphaseが所有する。

intake/scoutingは制約とverification候補を発見するが、product behaviorを推測で決めない。planningはplanとevidence mappingを所有するが、planに記載した恒久editは所有しない。debuggingはreproduction、hypothesis、root-cause evidence、regression-test shape、明示的にtemporaryなprobeを所有し、広いfixはplanning、bounded fixはimplementationへ渡す。implementationはverification/readinessから戻った修正を含むすべての恒久editを所有する。verificationは統合結果を独立確認し、恒久edit findingをimplementationへ戻して再検証する。readinessはclassificationとpackaging evidenceを所有するが、恒久file correctionはimplementationへ戻す。

## 最終検証と readiness

final verification は実装後の統合結果を評価する。リポジトリの実コマンドを確認し、狭い check から始め、変更した contract に応じて広げる。local substitute と CI-equivalent evidence は区別する。

- `ready`: 必須証拠がすべて pass し、未解決の重要な競合がない。
- `conditionally-ready`: 必須証拠は pass したが、任意の証拠を skip した、または受容済みの残存リスクがある。
- `not-ready`: 必須証拠がない/失敗している、期待結果が未解決、または重要リスクが未受容。

## Worktree の保持

既存および途中で見つかった local change は、current task で自分が作ったもの以外 user-owned と扱う。変更済み target file を編集する前に現在内容と diff を確認し、自分が所有しない hunk を特定して可能なら避けて編集する。依頼された変更が同じ箇所の unknown user work と重要に衝突する場合は停止し、簡潔な質問を1つ行う。無関係な user work を stage、overwrite、move、delete しない。

## Cross-shell path safety

path discovery、validation、destructive mutation は同じ shell 内で完結させる。recursive delete/move の前に、Windows では `Resolve-Path`、Linux/WSL では `readlink -f` など platform-native canonicalizer で target を解決し、意図した exact path または parent 配下であることを確認する。

PowerShell から WSL へ non-trivial な multi-line Bash script を渡す場合は、plain-text temporary helper file より `wsl.exe bash -s -- <arguments>` への stdin pipe を優先する。どちらの形式にも secret を置かない。

## Repository Trust

未知または未信頼 repo の command は任意コード実行として扱い、`safe` profile で read-only inspection から始める。runtime/profile が trust を明示している場合、またはユーザーの明示確認後にだけ repository-controlled command を実行する。エージェント自身の判断だけでは trust を昇格させない。破壊的操作、remote mutation、publish、deploy、本番データ、migration、secret handling は引き続き明示承認を必要とする。
