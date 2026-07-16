---
source: skills/codex-repo-scout/SKILL.md
source_blob: 74748212e7c574ad7c63b082874bef9280861dd4
canonical: false
---

# codex-repo-scout 日本語参考訳

この文書は `skills/codex-repo-scout/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

relevant files、conventions、ownership boundaries、executable checks が不明な場合だけ、実装に必要な repository context を集める。通常の file search や inspection に formal scouting pass は不要。

## 共通開発契約

`rules/development-workflow.md` に従う。scouting は constraints と executable evidence を発見し、trust、worktree preservation、expected outcome、verification は共通契約を正とする。

## Explorer Evidence Packets

subagents が使えて subsystem 単位に分けられる大きさなら、bounded explorer question を割り当てる。

- explorer ごとに subsystem、feature path、question を1つ割り当てる。
- pasted file bodies ではなく、file paths、symbols、commands、relevance、confidence を求める。
- integration decision と critical-path verification は parent が持つ。
- conflicting、low-confidence、implementation-blocking finding だけ再確認する。

## 返す証拠

- likely files、symbols、ownership boundaries。
- existing patterns と変更を制約する repository instructions。
- 結果を証明できる build、test、CI、manual checks。
- 必要な runtime、package manager、service、明確に不足する dependency。
- 重要な uncertainty と、それを解決する最小の次の read-only inspection。

## Stop Conditions

likely write scope、従う pattern、credible verification path が明確になったら停止する。focused pass 後も material gap が残る場合は、gap を示して質問を1つ行うか、narrow inspection step を1つ提案する。

通常の model behavior を言い直すため、または exhaustive repository inventory を集めるためだけに scouting を続けない。
