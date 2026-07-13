---
source: rules/checklists/implementation.md
source_blob: f6e7251bb19753532cb30de8dd3da5318ba1a642
canonical: false
---

# Implementation Checklist 日本語参考訳

- 期待結果、証拠、ownership、readiness、repository trust は `$HOME\.codex\rules\development-workflow.md` に従う。
- research notes または active run note がある場合は、編集前に読み直す。
- 変更は依頼された挙動と近くの tests/docs に限定する。
- ユーザー変更を保持し、無関係なファイルを戻さない。
- 新しい abstraction より既存 helper、type、convention、script を優先する。
- stable、deterministic、relevant、reasonably cheap な test seam がある場合は、恒久変更前に focused check が意図した理由で失敗することを確認する。
- test-first が実務上難しい場合は、恒久変更前に理由と、信頼できる最小の代替 feedback を記録する。
- 実装中の focused red/green feedback と、統合後の final verification を区別する。
- final diff を確認し、意図しない churn、secret、debug print、無関係な編集を取り除く。
- active run note がある場合は、変更ファイル、acceptance evidence、readiness、後で重要になる判断を記録する。
