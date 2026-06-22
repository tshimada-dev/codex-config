---
source: rules/checklists/implementation.md
source_commit: 9d82168940feaf062538dd53619db9d0906cde5a
canonical: false
---

# Implementation Checklist 日本語参考訳

- research notes または active run note がある場合は、編集前に読み直す。
- 変更は依頼された挙動と近くの tests/docs に限定する。
- ユーザー変更を保持し、無関係なファイルを戻さない。
- 新しい abstraction より既存 helper、type、convention、script を優先する。
- 挙動が変わる場合は test-first loop を優先する。focused test を追加または更新し、実務上可能なら期待どおり失敗することを確認してから、最小変更を実装し、focused check と関連する広めの check を再実行する。
- non-trivial な behavior change で test-first が実務上難しい場合は、その理由を記録し、信頼できる最小の代替検証を使う。
- final diff を確認し、意図しない churn、secret、debug print、無関係な編集を取り除く。
- active run note がある場合は、変更ファイルと後で重要になる判断を記録する。
