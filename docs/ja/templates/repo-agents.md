---
source: templates/repo-agents.md
source_blob: 41baf6f02167eb3d1c11238840e7570ea8375d7b
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
- subagents は独立した価値を持つ bounded work に限って使い、model choice、reasoning effort、context isolation、parent ownership はグローバルな Subagent Delegation rules に従う。
- 中断や再開の可能性がある長時間作業は、このリポジトリで定められた run note 場所に記録する。慣習がない場合は、repo 内に internal run note を追加せず `$HOME\.codex\runs\<repo-name>\YYYYMMDD-HHMM-<short-task>.md` を使う。
- handoff は active run note がある場合はそこに追記し、単体の handoff が必要な場合だけ `docs/codex/handoffs/` を使う。

## Verification

- Format:
- Lint:
- Typecheck:
- Test:
- Build:
- CI parity: local command が CI と異なる場合は差分を記録し、同等として黙って扱わない。

## Safety

- 破壊的 command、remote mutation、deploy、migration、publishing、secret handling の前に確認する。
- secret、token、private key、cookie、`.env` の内容は、ユーザーが明示的に依頼し、かつ task に必要な場合を除き、inspect、print、copy、upload、summary しない。
