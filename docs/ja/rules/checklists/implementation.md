---
source: rules/checklists/implementation.md
source_commit: 48e43573d157de0d17b777a5acb42a84af4825b7
canonical: false
---

# Implementation Checklist 日本語参考訳

- 編集前に research notes を読み直す。
- 変更は依頼された挙動と近くの tests/docs に限定する。
- ユーザー変更を保持し、無関係なファイルを戻さない。
- 新しい abstraction より既存 helper、type、convention、script を優先する。
- 挙動が変わる場合は test-first loop を優先する。focused test を追加または更新し、実務上可能なら期待どおり失敗することを確認してから、最小変更を実装し、focused check と関連する広めの check を再実行する。
- test-first が実務上難しい場合は、その理由を記録し、信頼できる最小の代替検証を使う。
- final diff を確認し、意図しない churn、secret、debug print、無関係な編集を取り除く。
- 変更ファイルと後で重要になる判断を active run note に記録する。
