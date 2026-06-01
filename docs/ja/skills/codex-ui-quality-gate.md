---
source: skills/codex-ui-quality-gate/SKILL.md
source_commit: dd1c94c
canonical: false
---

# codex-ui-quality-gate 日本語参考訳

この文書は `skills/codex-ui-quality-gate/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

frontend、CSS、layout、responsive behavior、canvas/WebGL、images、animations、forms、navigation、accessibility など、視覚確認が必要な変更を browser-based checks で検証する。

## Verification Steps

1. app の起動方法と target route を確認する。
2. Browser plugin / Codex in-app browser など最適な browser path で relevant page を開く。
3. desktop と mobile など必要な viewport で確認する。
4. console errors、network failures、layout overflow、text clipping、interaction behavior を見る。
5. 変更した UI state、empty/loading/error state、主要 interaction を確認する。
6. 見つけた問題は、可能なら修正して再確認する。

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

final report には、確認した route、viewport、tests/browser checks、残る visual risk を短く書く。browser check が実行できない場合は理由を明示し、代替 check を報告する。
