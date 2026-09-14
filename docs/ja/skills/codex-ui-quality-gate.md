---
source: skills/codex-ui-quality-gate/SKILL.md
source_blob: 4dec3a5fe42ddbfffae14dbff499be863279c599
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
3. 製品の supported devices と変更の影響から viewport を選ぶ。desktop/mobile 対応の responsive surface は両方、desktop 専用品は対応 desktop のみ確認する。局所的な見た目の変更で無関係な device/route へ広げない。
4. console errors、network failures、layout overflow、text clipping、interaction behavior を見る。
5. 変更が影響する UI state、empty/loading/error state、interaction を確認する。静的 content のみなら visual inspection でよく、無関係な interaction を強制しない。
6. 恒久修正が必要な finding は evidence とともに `codex-implementation` へ戻し、修正後に gate を再実行する。戻した finding が未検証のまま pass にしない。

subagents が使える場合は、changed route と expected states が明確になってから focused UI verification を worker に任せる。

最終 UI、関連 environment、supported targets、expected states が変わらなければ、共通契約に従って記録済み browser evidence を再利用する。修正後は影響する state/viewport と無効化された check を再実行し、報告 phase に移るだけで無影響の確認を繰り返さない。

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
