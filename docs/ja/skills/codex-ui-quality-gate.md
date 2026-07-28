---
source: skills/codex-ui-quality-gate/SKILL.md
source_blob: f3acc12131cf5ebe6242efb2bc029d0b5a77e91d
canonical: false
---

# codex-ui-quality-gate 日本語参考訳

この文書は `skills/codex-ui-quality-gate/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

frontend、CSS、layout、responsive behavior、canvas/WebGL、images、animations、forms、navigation、accessibility など、視覚確認が必要な変更を browser-based checks で検証する。

## 共通開発契約

`rules/development-workflow.md` に従う独立 verification gate として、expected outcome と acceptance criteria に対して統合結果を確認する。恒久的な product edit は `codex-implementation` が所有する。

## Verification Steps

1. app の起動方法と target route を確認する。
2. Browser plugin / Codex in-app browser など最適な browser path で relevant page を開く。
3. desktop と mobile など必要な viewport で確認する。
4. console errors、network failures、layout overflow、text clipping、interaction behavior を見る。
5. 変更した UI state、empty/loading/error state、主要 interaction を確認する。
6. 恒久修正が必要な finding は evidence とともに `codex-implementation` へ戻し、修正後に gate を再実行する。戻した finding が未検証のまま pass にしない。

subagents が使える場合は、changed route と expected states が明確になってから focused UI verification を worker に任せる。

## Browser Probes

必要に応じて以下を確認する。

- route と viewport
- overflow status
- console status
- interaction tested
- screenshot path only if intentionally kept

## Artifact Hygiene

- screenshots や temporary browser profiles は repo に混ぜない。
- temporary browser profiles は repo 外に置くか、final delivery 前に削除する。
- Chrome profile files、caches、raw automation logs を deliverable にしない。

## Reporting

final report には、確認した expected outcome/acceptance criteria、route、viewport、tests/browser checks、残る visual risk を短く書く。browser check が実行できない場合は理由を明示し、代替 check を報告する。
