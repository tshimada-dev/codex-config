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
- 中断や再開の可能性がある長時間作業は `docs/agent-runs/` に記録する。

## Verification

- Format:
- Lint:
- Typecheck:
- Test:
- Build:

## Safety

- 破壊的 command、remote mutation、deploy、migration、publishing、secret handling の前に確認する。
