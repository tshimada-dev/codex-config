---
source: rules/checklists/research.md
source_commit: dd1c94c
canonical: false
---

# Research Checklist 日本語参考訳

- ユーザーの依頼を一文で言い直す。
- 対象リポジトリ、現在ディレクトリ、関連サブディレクトリを確認する。
- `AGENTS.md`、README、Makefile、package files、pyproject、scripts などの local instructions を読む。
- `rg` や `rg --files` で関連コード、tests、config、docs を探す。
- 命名、error handling、testing、logging、boundary の既存 pattern を確認する。
- 編集前に git status を確認し、無関係な既存変更をメモする。
- findings、assumptions、risks、open questions を active run note に記録する。
