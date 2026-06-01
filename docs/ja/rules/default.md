---
source: rules/default.rules
source_commit: b2aabbecfae880f70afb36475f707708f79e1075
canonical: false
---

# default.rules 日本語参考訳

この文書は `rules/default.rules` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版の `.rules` ファイルです。

## 方針

デフォルトの個人ポリシーは、保守的かつ汎用的に保つ。

タスク固有のコマンド、変更を伴うコマンド、cloud、package install、公開系のコマンドは、広い allow ではなく、`command-policy.rules` に `prompt` または `forbidden` として入れる。

## allow

このファイルでは最小限の読み取り系だけを許可する。

- `git status`
- `git diff`
- `git log`
- `git show`
- `rg`
