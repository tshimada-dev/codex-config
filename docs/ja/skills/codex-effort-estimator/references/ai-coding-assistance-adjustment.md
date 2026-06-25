---
source: skills/codex-effort-estimator/references/ai-coding-assistance-adjustment.md
source_commit: 7fda18bc617a3e1bb86991c22e81a7bf090eccd7
canonical: false
---

# AI コーディング補助補正

この reference は、ユーザーが AI coding assistance、coding agent、Copilot 的補助、AI-assisted implementation を前提にすると明示した場合だけ使います。

これは人間の工数見積もりを補正するものです。AI agent の wall-clock time 見積もりではありません。

## 原則

raw WBS/PERT の後で補正します。baseline を見える状態で残し、その上で AI-assisted range を示します。定型的な coding 作業は減らし、人間中心の調整、検証、不確実性対応は残します。

Codex が見積もりを手伝っているだけでは、この補正を適用しません。

## 工程別ガイド

| 工程または作業種別 | 典型倍率 | メモ |
|---|---:|---|
| 定型 scaffold、単純 CRUD、boilerplate、機械的 refactor | 0.55-0.75 | 要件と pattern が明確な場合、AI の効果が大きい。 |
| 仕様が明確な実装、単純な業務ロジック | 0.65-0.85 | testability と local convention に依存する。 |
| Unit test 下書き、fixture、簡易 docs、migration script | 0.70-0.90 | 人間による review と test design は残す。 |
| 複雑な業務ルール、legacy behavior matching、debugging | 0.80-1.00 | AI は役立つが、discovery と validation が支配的。 |
| Integration、security、deployment、performance、observability | 0.85-1.05 | 環境制約と review cycle に制約されやすい。 |
| Excel/PDF fidelity、data migration、old-vs-new comparison、visual QA | 0.90-1.10 | coding は速くなる場合があるが、validation loop は残る。AI 生成物が correction/review cycle を増やす場合は 1.0 超を使う。 |
| PM、requirements、stakeholder review、acceptance、training、handoff | 0.95-1.00 | coding assistance では通常ほとんど減らない。 |
| 不明確な要件、未解決の domain decision | 1.00 | coding reduction ではなく discovery を使う。 |

codebase が未知、test が弱い、要件が曖昧、出力に manual validation が必要な場合は、倍率レンジの高い側を選びます。

## 手順

1. raw WBS/PERT estimate または phase breakdown から始める。
2. reducible phase と non-reducible phase に分ける。
3. WBS/PERT 行が reducible work と non-reducible work を混在させている場合、倍率適用前にその行を分割する。根拠から分割できない場合は保守的な倍率を使い、理由を説明する。
4. phase-specific multiplier は reducible coding または code-adjacent work だけに適用する。
5. risk と contingency は見える状態で残す。未解決要件を productivity factor に隠さない。
6. baseline と AI-assisted range の両方を報告する。
7. adjusted total が baseline より 35% 超低い場合、明示的に reduction を flag し、scope evidence で正当化する。45% 超低い場合は、反復的 CRUD、強い test、明確な pattern、安定した要件など強い根拠を要求する。根拠が弱い場合は multiplier を上げる。
8. 前提を説明する。AI は code の生成・修正を助けるが、design decision、review、integration、validation、acceptance の責任は人間に残る。

## Output Schema

返すもの:

- Raw baseline low / base / high person-days。
- `Phase`, `Baseline`, `Multiplier`, `Adjusted`, `Rationale` を含む adjustment table。
- AI-assisted low / base / high person-days。
- Non-reducible work。
- AI assistance が効きにくい risk。
- Reduction sanity check。特に total reduction が 35% を超える場合。
- Confidence level。

unit rate と commercial assumption が与えられていない限り、この補正を pricing に使わないでください。
