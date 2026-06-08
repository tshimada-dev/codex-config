---
source: skills/codex-effort-estimator/references/risk-model-pass.md
source_commit: 17be59e3fe075540200adf764fe1654cf6b3be3d
canonical: false
---

# Risk Model Pass 日本語参考訳

この文書は `skills/codex-effort-estimator/references/risk-model-pass.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

uncertainty drivers から risk-adjusted estimate を作る pass です。軽量な scenario model、または distribution を置ける場合の Monte Carlo-style model として使います。risk を WBS high に隠さず、probability、impact、correlation を audit 可能にします。

## Independence Rules

1. WBS total、WBS line estimate、WBS-derived PERT、component-unit total、parent synthesis、prior estimate artifact、期待する final range を使わない。
2. source-visible risk drivers と、WBS ではない independent base-effort anchor から始める。WBS risk overlay と明示された場合だけ WBS を base にできる。
3. probability、impact、correlation assumptions を明示する。
4. overlap は parent synthesis で扱い、この pass 内では同じ risk を二重計上しない。

## Procedure

- report/PDF fidelity、sample-vs-production data gaps、encoding/external characters、external integration uncertainty、acceptance criteria ambiguity、stakeholder/review wait、legal/policy change、deployment constraints などを risk drivers として抽出する。
- 各 risk に probability と impact low/base/high を置く。
- correlation group を付ける。
- `expected_risk = probability * expected_impact`
- `risk_adjusted_center = base_effort + sum(expected_risk)`
- simulation しない場合は low-risk / expected-risk / high-risk correlated scenario を出す。

## Output Schema

- Independent base-effort anchor and rationale
- Risk register: `Risk`, `Probability`, `Impact low/base/high`, `Expected exposure`, `Correlation group`, `Basis`, `Mitigation/confirmation`
- Risk-adjusted low/base/high or P50/P80/P90
- Correlated high-risk scenario
- Overlap warnings
- Confidence and confirmation questions

他 estimator の結論を使わず、risk math を unexplained contingency に隠しません。
