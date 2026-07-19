---
source: docs/evaluations/debug-discipline-ab.md
source_blob: 3ec7a7faa78edcac83795d4f019b17b26c560e9b
canonical: false
---

# Debug-discipline 複数ケース golden / A-B 評価 日本語参考訳

この文書は `docs/evaluations/debug-discipline-ab.md` の日本語参考訳です。
再現条件、採点、採否判断の正本は英語版です。

## 目的と受け入れ基準

- `AC-8-1`: 既存の implementation-loop 2ケースに加え、
  debug-discipline 用の seeded disposable fixture 2件と、提出後に公開する
  golden harness 2件を用意する。
- `AC-8-2`: 結果を見る前にA/Bの条件と判定規則を固定し、複数ケースで
  再実行できるようにする。

評価対象は、現在の debug discipline がproduct correctnessを落とさず診断証拠を
改善するかであり、modelやworkflowの普遍的優位性ではありません。

## 結果前に固定した条件

- Variant A: 同じ2件のREADMEと通常の作業指示を受けるが、
  `codex-debug-discipline`を読まず使用しない。
- Variant B: 同じ2件に加え、canonicalな`codex-debug-discipline`を全文読み、
  診断手順とimplementation handoffを実行する。
- 別々のsubagent、別々の使い捨てcopy、各1 turnで実行し、golden harnessは
  両提出が終わるまで見せない。
- case 01はprofileを含まないcache keyによるstate contamination、case 02は
  dependency listのaliasによる入力破壊と2回目の順序違反をseedした。

採点は、golden behavior 35点、regression 15点、scope/cleanup 15点、
diagnostic evidence 20点、test quality 10点、効率と残存risk 5点の100点です。
すべてのgolden assertion、元test、追加testが通り、範囲外変更と一時instrumentation
がないことを有効性gateとしました。Bを支持するには、正確性の非劣性と診断証拠の
改善に加え、action数と時間がAの2倍以内であることを結果前に要求しました。

公開したcriteria-only snapshot
`docs/evaluations/preregistrations/debug-discipline-ab-20260719.md`は候補実行前の
`2026-07-19T13:58:33.7878831+09:00`に固定し、そのSHA-256は
`636c41ec26243327d229c00a6db7b1bb386967462f5ff0f781bd59e9e64b88a2`
でした。

## 実行結果

| 観測値 | Variant A | Variant B |
| --- | ---: | ---: |
| 指示文字数 | 1,050 | 1,184 |
| 所要時間 | 161秒 | 314秒 |
| top-level実行call | 7 | 15 |
| 内包されたshell + patch call | 9 | 21 |
| 候補自身のunit test | 10/10 | 7/7 |
| withheld golden assertion | 20/20 | 20/20 |

両者ともcase 01ではcache keyにprofileを追加しcache境界でdeep-copy、case 02では
scheduling前にdependency listをcopyする同じ最小修正を選びました。提出testを
未修正seedへ戻すと、Aはcase 01で3件・case 02で1件、Bはcase 01で2件・case 02で
1件が意図どおり失敗しました。README、CLI、validation、公開interfaceは維持され、
範囲外変更はありません。Aは使い捨てdirectoryに生成された`__pycache__`を残した
ため、manifestと公開物から除外しました。Bは除去済みです。

再現commandは次のとおりです。

```powershell
python docs/evaluations/harness/debug-discipline-case-01-golden.py CANDIDATE\case-01
python docs/evaluations/harness/debug-discipline-case-02-golden.py CANDIDATE\case-02
python -m unittest discover -s CANDIDATE\case-01 -p 'test_*.py' -v
python -m unittest discover -s CANDIDATE\case-02 -p 'test_*.py' -v
```

## 採点と判断

| 評価軸 | Variant A | Variant B |
| --- | ---: | ---: |
| Golden behavior / 異常系 (35) | 35 | 35 |
| 既存・追加regression (15) | 15 | 15 |
| Scope / cleanup (15) | 15 | 15 |
| Diagnostic evidence (20) | 20 | 20 |
| Test quality (10) | 10 | 10 |
| 効率 / 残存risk (5) | 5 | 5 |
| **合計** | **100** | **100** |

両variantとも、事前登録したdiagnostic evidenceの全要件（expected/actual、各case
3件の反証可能hypothesis、個別probe、根拠付きroot causeとfix shape、regression、
final check、残存risk）を満たしました。Bの`If ... then ...`やconfirmed/rejected表記は
明示的ですが、そのstyle差へ点を配る規則は結果前に定義していないため採点に使いません。
Aの`__pycache__`もcommit・manifest・公開対象に含まれないため、両者のscopeは満点です。
効率軸も観測値の記録だけが固定要件で部分点式はなかったため、別のsupport gateを適用する
前の採点は両者100点です。

behavior/regression/scope小計は双方65、diagnostic evidenceも双方20で同点です。さらに
Bのtop-level action比2.14は事前固定した2倍上限を超えました。したがってBは、診断証拠で
Aを上回らないこととaction上限超過の2点でsupport ruleを満たさず、今回の2ケースでは
skillの優位性を支持しません。正確性とrubric evidenceが同等なので、指示量とoperation数が
小さいbaselineを今回のseedでは優先します。

ただし、これはcanonical skillの削除や書換えを正当化しません。2件の同一model
roleplayはUI、concurrency、performance、distributed failureへ一般化できず、style差は
事前登録した判断軸ではないためです。canonical skillは変更していません。

`AC-8-1`は両開発skillのfixture/harnessで、`AC-8-2`は事前hash、別agent・隔離copy、
4組すべての再実行証拠で満たしました。action数はagent自己申告であり二次的観測です。
golden harnessはtestへの過適合を減らしますが、platform-wide instruction leakageは
完全には排除しません。より広い採否判断には異なるtask classの追加batchが必要です。
