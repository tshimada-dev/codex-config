---
source: skills/codex-effort-estimator/references/repetition-and-reuse.md
source_commit: e535debff08e37bf3540fa3677f8a8e610fcfb8f
canonical: false
---

# 繰り返し・再利用・規模の経済

scope に繰り返しの variant や共有 skeleton が含まれるとき（複数地区、支店、部署、似た reports、似た screens、import/calculate/number/output を共有する workflow など）に使います。

数えた artifact からの bottom-up 見積は、この種の作業で系統的に上振れします。数えた各項目を bespoke build として値付けしがちだからです。この reference は、その上振れが WBS total に届く前に補正するために置いています。独立した method pass ではなく、sizing と WBS の中で適用する規律です。

## Core Principle

数えた scope は build scope と同じではありません。`N` 個の似た artifact は通常、`N` 個のフルビルドではなく、`1` 個の framework と `N - 1` 個の安い variant です。

```text
group_effort = framework_effort + (instances - 1) * representative_effort * variant_factor
```

- `framework_effort`: engine、最初のフル instance、共有 template を一度だけ作る。
- `representative_effort`: 既に対応済みの instance 1個の典型工数。
- `variant_factor`: 後続 variant が bespoke build に対して実際にどれだけかかるか。

## Variant Factor Guidance

variant factor は「資料での見た目」ではなく「どう実現するか」で選びます。

| Variant の実現方法 | 目安 variant factor | 備考 |
|---|---:|---|
| 純粋な config か data/master 行 | 0.05-0.15 | 同じ code path、データ違い。 |
| 同じ layout engine の template fill | 0.10-0.25 | multi-region/multi-report 出力の多くがここ。 |
| 同じ構造で layout/rule が少し違う | 0.25-0.45 | variant 固有の logic/layout 調整あり。 |
| rule/layout/データ形が実質的に異なる | 0.50-0.90 | ほぼ bespoke として扱い、理由を記録。 |
| 何も再利用しない独立 feature | 1.00 | variant ではない。独立 line で見積。 |

template 共有が未確認、fidelity が厳格（pixel/PDF）、各 variant が固有の validation/acceptance 証跡を要するときは高め側を選びます。

## Cross-Feature Reuse

別々の feature でも skeleton を共有することは多くあります（import→validate→calculate→number→output を共有する複数 workflow、同じ form/grid 基盤の複数 screen など）。

- skeleton を確立する最初の feature はフルコストで見積。
- skeleton を再利用する後続 feature は割引き、net-new の logic/screen/rule/output だけを見積。
- reuse の仮定は明示し、反証可能にする。reuse が不確実なら仮定として残し、フルビルドを黙って積まずに high 側を広げる。

## Count Risk Once

risk と contingency はちょうど 1 箇所に置きます。積み重ねないでください。

- three-point の `high` が既に妥当な悲観 risk を含むなら、同じ risk に対して別個の reserve/risk-reserve line を追加し、かつ fully correlated の endpoint-sum high を見出しにする、という二重・三重計上をしない。
- 1 つの表現を選ぶ: line ごとに `high` を広げる、単一の可視 reserve line を持つ、相関 high-risk scenario を示す。同じ不確実性に対して 3 つ全部はしない。
- 単独の risk-reserve line は、line range に未だ含まれない risk のときだけ許容し、その目的を明記する。

## Top-Down Cross-Check

bottom-up WBS の後、確定前に独立した top-down anchor と突合します。

1. bottom-up total から per-unit を出す（report/screen/workflow/function point あたりの person-days など）。
2. 組織の productivity baseline、過去実績、または妥当な専門家 anchor と比較。
3. bottom-up total が credible anchor を大きく上回る per-unit を示すなら、economy of scale や reuse の適用不足の signal とみなす。まず最大の繰り返し group を再点検する。
4. cross-check 結果を記録: 整合 / 繰り返し・再利用で下方調整 / 理由付きで高位維持。

組織 baseline が無いときはそう述べ、絶対水準が measured productivity で較正されていない document-derived judgment に依存することを明記する。未較正の bottom-up total を anchored であるかのように提示しない。

## Output Expectations

この reference を適用したら、economy of scale を監査可能にします:

- 繰り返し group（instance 数、framework line、使った variant factor）。
- feature 間の reuse 仮定（未確認なら仮定と明記）。
- risk/contingency の単一で明確な配置。
- top-down per-unit cross-check と突合結果。
- 繰り返し出力系では、1 本の大きな未分解 report line ではなく `framework + variants` の明示内訳。
