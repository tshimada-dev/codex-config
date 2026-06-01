---
source: rules/checklists/implementation.md
source_commit: dd1c94c
canonical: false
---

# Implementation Checklist 日本語参考訳

- 編集前に research notes を読み直す。
- 変更は依頼された挙動と近くの tests/docs に限定する。
- ユーザー変更を保持し、無関係なファイルを戻さない。
- 新しい abstraction より既存 helper、type、convention、script を優先する。
- 挙動、contract、risk のある logic が変わる場合は tests を追加または更新する。
- final diff を確認し、意図しない churn、secret、debug print、無関係な編集を取り除く。
- 変更ファイルと後で重要になる判断を active run note に記録する。
