---
source: templates/repo-agents.md
source_commit: dd1c94c
canonical: false
---

# Repository Codex Instructions 日本語参考訳

この文書は `templates/repo-agents.md` の日本語参考訳です。実際のテンプレートとして使う canonical は英語版です。

## Project Shape

- Main source:
- Tests:
- Scripts:
- Docs:

## Working Rules

- 無関係なユーザー変更を保持する。
- 変更は依頼された挙動に絞る。
- repository-local の helper や convention を優先する。
- subagents が使える場合は、context-heavy research、広い planning、独立した implementation slice、review、verification に優先して使う。
- 中断や再開の可能性がある長時間作業は `docs/codex/runs/` に記録する。
- handoff は active run note がある場合はそこに追記し、単体の handoff が必要な場合だけ `docs/codex/handoffs/` を使う。

## Verification

- Format:
- Lint:
- Typecheck:
- Test:
- Build:

## Safety

- 破壊的 command、remote mutation、deploy、migration、publishing、secret handling の前に確認する。
