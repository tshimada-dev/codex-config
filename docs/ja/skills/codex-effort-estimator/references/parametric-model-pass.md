---
source: skills/codex-effort-estimator/references/parametric-model-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Parametric Model Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/parametric-model-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

countable scope parameters と productivity coefficients から、WBS と独立した top-down estimate を作るために使います。work breakdown や artifact ごとの見積表ではなく、明示的な estimating equation による独立 anchor です。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. source documents、sizing facts、この reference だけを使う。sizing pass output を使う場合も count、count confidence、ambiguity notes だけを使う。
3. 計算前に model equation を定義し、他 method に合わせて coefficient を選ばない。
4. coefficient source を local actual、historical benchmark、public benchmark、heuristic、judgment のどれかとして記録する。

## Procedure

- workflows/use cases、screens/forms、reports/templates/PDF outputs、imports/exports/integrations、entities/master data、calculation/rule clusters、formal deliverables などから driver を選ぶ。
- driver ごとに low/base/high coefficient を person-days per unit で設定する。
- source-backed な場合だけ fixed overhead、governance overhead、report-fidelity factor、data-quality factor、integration complexity factor、acceptance/validation multiplier を加える。
- `subtotal = fixed_overhead + sum(count * coefficient)`、`adjusted_total = subtotal * combined_factor` で low/base/high を出す。

## Output Schema

- Source files inspected
- Model equation and included drivers
- Driver table: `Driver`, `Count`, `Count basis`, `Low/Base/High coefficient`, `Coefficient source`, `Notes`
- Adjustment table: `Factor`, `Low`, `Base`, `High`, `Basis`, `Why not double-counted`
- Overall low/base/high person-days
- Calibration confidence
- Assumptions、exclusions、risks、confirmation questions

他 estimator の結論を使わず、WBS に合わせて係数を調整しません。
