---
source: skills/codex-effort-estimator/references/ai-coding-assistance-adjustment.md
source_commit: 7fda18bc617a3e1bb86991c22e81a7bf090eccd7
canonical: false
---

# AI コーディング補助補正

この reference は、ユーザーが AI コーディング補助、コーディングエージェント、Copilot のような補助、または AI 支援による実装を前提とすると明示した場合だけ使います。

これは人間の工数見積もりを補正するものです。AI エージェントの実所要時間を見積もるものではありません。

## 原則

raw WBS/PERT の後で補正を適用します。raw baseline は見える状態で固定し、その上で AI 支援後の範囲を示します。定型的なコーディング作業は減らし、人間中心の調整、検証、不確実性対応は残します。

Codex が見積もりを手伝っているだけでは、この補正を適用しません。

スコープまたは実装方式が変わるたびに、`AI削減区分` を再導出しなければなりません。フルカスタムシステムでは `複雑実装` または `検証重` だった行でも、より薄い Excel/VBA、既存テンプレートへの値埋め、設定中心、または顧客側でテストするスコープでは `定型実装` または `コード隣接` になり得ます。スコープを狭めた後に古いタグを引き継いではいけません。

## 判断と権限の分離

次の2つの判断を分離します。

- 削減可能性の判断: 作業の文脈を持つ WBS/PERT 作成者が行単位で判断します。各行に `AI削減区分` と短い根拠を出力します。
- 係数の権限: 下記の固定係数はこの reference が定めます。AI 補正処理は、望ましい合計値に合わせて係数を選んだり、親集計に合わせて調整したり、raw baseline の値を上書きしたりしてはいけません。

この補正は raw estimate に従属する変換であり、独立した見積もり方式ではありません。

## 固定行レベル係数

`AI削減区分` ごとに次の定数を使います。工程全体へ裁量的な係数を適用してはいけません。

| AI削減区分 | 固定倍率 | 使用条件 |
|---|---:|---|
| `定型実装` | `0.70` | 定型 scaffold、単純 CRUD、boilerplate、機械的 refactor、または pattern が確立した実装。 |
| `コード隣接` | `0.85` | 仕様が明確な実装、単純な業務ロジック、簡易な test/docs/script、またはコードに隣接する設計作業。 |
| `複雑実装` | `0.90` | 複雑な業務ルール、legacy behavior matching、debugging、integration、security、deployment、performance、または observability。 |
| `検証重` | `0.95` | Excel/PDF fidelity、data migration、old-vs-new comparison、visual QA、acceptance evidence、または report validation。 |
| `削減不可` | `1.00` | PM、requirements、stakeholder review、acceptance、training、handoff、未解決の domain decision、または coordination。 |
| `対象外` | `1.00` | AI コーディング補助の前提外にある作業。 |

旧形式の workbook では次の別名を許可します。

| 別名 | 扱い |
|---|---|
| `削減あり` | `コード隣接` |
| `一部削減` | `コード隣接` |
| `削減困難` | `削減不可` |
| `削りすぎ注意` | `検証重` |

行の `AI削減区分` が未定義の場合は `1.00` を適用し、`要確認` としてフラグを立て、係数を創作してはいけません。

## 手順

1. low / most likely / high の値を持つ raw WBS/PERT 行から始めます。
2. 各行に `AI削減区分` と根拠を必須とします。削減可能な作業と削減不可能な作業が1行に混在する場合は、係数適用前に分割します。根拠から分割できない場合は、より保守的な区分を使い、その理由を明記します。
   - foundation、CRUD、共通 UI、scaffolding、script、または pattern 化された実装の行は、`定型実装`、`コード隣接`、`複雑実装` のどれかを明示的に判断します。legacy behavior matching、security、operations、performance、不確実な integration など具体的な複雑性要因を示さず、一般的な「foundation」行を `複雑実装` のままにしてはいけません。
   - Excel/VBA 中心のスコープでは、sheet への CSV import、master data mapping、numbering/code generation、formula wiring、既存テンプレートへの値埋めは、source が厳密な legacy reproduction、複雑な domain validation、または old-vs-new acceptance evidence を要求しない限り、通常は `定型実装` または `コード隣接` です。
   - report/template 作業が `検証重` となるのは、納品物に厳密な visual fidelity、PDF/print reproduction、または supplier-owned acceptance evidence が含まれる場合だけです。既存テンプレートを再利用し、顧客が詳細テストを実施するスコープなら、`コード隣接` または `定型実装` の方向へ再評価します。
3. 各行の `AI削減区分` に対応する固定係数を low / most likely / high に適用します。raw baseline のセルは変更してはいけません。
4. 行単位で乗算した後、補正済み行を工程別および全体 summary へ集計します。
5. risk と contingency は見える状態で残します。未解決要件を productivity factor に隠してはいけません。
6. raw baseline と AI 支援後の範囲の両方を報告し、base の差分を見える状態にします。
7. 補正後合計が baseline より 35% 超低い場合、その削減を明示的にフラグし、行単位の scope evidence で正当化します。45% 超低い場合は、高度に反復的な CRUD、強い test、明確な pattern、安定した要件など強い根拠を要求します。根拠がなければ、不確実な行をより保守的な区分へ移します。
8. 実装比重の高い raw base の大半が `複雑実装` / `検証重` に分類され、AI による全体削減率が 15% 未満の場合は、保守性の sanity check を明示的に実施します。定型または pattern 化された行を再分類するか、保守的なタグを正当化する具体的な複雑性要因を記載します。
9. 前提を説明します。AI は code の生成・修正を助けますが、design decision、review、integration、validation、acceptance の責任は人間に残ります。

## Output Schema

返すもの:

- Raw baseline low / base / high person-days。
- `WBS分類`、`WBS作業`、`AI削減区分`、`Raw Low`、`Raw Base`、`Raw High`、`固定倍率`、`Adjusted Low`、`Adjusted Base`、`Adjusted High`、`Base差分`、`判断者`、`係数権限`、`根拠` を含む行単位の adjustment table。
- AI 支援後の low / base / high person-days。
- 削減不可能な作業。
- AI 補助が効きにくい risk。
- Reduction sanity check。特に total reduction が 35% を超える場合。
- Confidence level。

unit rate と commercial assumption が与えられていない限り、この補正を pricing に使ってはいけません。
