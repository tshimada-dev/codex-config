---
source: skills/codex-cloud-ops-intake/SKILL.md
source_blob: da4f25533b3db9036129a31ba2cf1281b9c36c97
canonical: false
---

# codex-cloud-ops-intake 日本語参考訳

この文書は `skills/codex-cloud-ops-intake/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

Cloud、infrastructure、database、deployment、migration command の前に、推測 target への操作を防ぎ、mutation 用の exact approval packet を作る。

## 共通 safety boundary

一般的な approval、destructive operation、repository trust、secret handling は `rules/development-workflow.md` を正とする。この Skill は cloud target identity と次の approval packet だけを追加する。

## Target と operation

command を選ぶ前に以下を確認する。

1. Provider/system と environment。
2. target を選ぶ exact account/profile/project、region、cluster/context/namespace、Terraform workspace、database endpoint。
3. `read-only`、`plan/dry-run`、`remote mutation`、`destructive mutation` の operation class。
4. Target resources、expected effect、rollback/recovery path、material cost/blast radius。

AWS profile、Kubernetes context、Terraform workspace、database endpoint、region、account、environment を便利だからと推測しない。user context または read-only identity command で確認し、未解決 target は development ではなく unknown と扱う。

read-only discovery、plan/dry-run、mutation の順を優先し、mutation の前に plan/diff を確認する。mutation は exact command と target の承認を必要とする。

## Approval Prompt

remote/destructive mutation では、以下の固定形で承認を求める。

```text
Please confirm this external operation before I run it:
- Command: ...
- Environment/account/region/context: ...
- Target resources: ...
- Expected effect: ...
- Rollback/recovery plan: ...
- Cost/blast radius: ...
```

確認された command だけを実行する。command が変わる場合は再確認する。

## Handoff

operation class、confirmed target identity、read-only/plan evidence、まだ承認が必要な exact commands、unresolved target risk を引き継ぐ。
