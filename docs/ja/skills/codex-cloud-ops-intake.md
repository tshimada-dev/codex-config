---
source: skills/codex-cloud-ops-intake/SKILL.md
source_blob: ce387141c928b7f39c6683e41258f8323b130b6a
canonical: false
---

# codex-cloud-ops-intake 日本語参考訳

この文書は `skills/codex-cloud-ops-intake/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

実環境の cloud/infrastructure、live database の操作、deployment/migration の実行前に、target identity と承認範囲を確立する。ローカルの SQL/schema/migration file 編集、使い捨て fixture の test、通常の Git/PR 操作だけでは発火しない。

## 共通 safety boundary

一般的な approval、destructive operation、repository trust、secret handling は `rules/development-workflow.md` を正とする。この Skill は cloud target identity と次の approval packet だけを追加する。

## Target と operation

command を選ぶ前に以下を確認する。

1. Provider/system と environment。
2. target を選ぶ exact account/profile/project、region、cluster/context/namespace、Terraform workspace、database endpoint。
3. `read-only`、`plan/dry-run`、`remote mutation`、`destructive mutation` の operation class。
4. mutation では target resources、expected effect、rollback/recovery path、material cost/blast radius。

AWS profile、Kubernetes context、Terraform workspace、database endpoint、region、account、environment を便利だからと推測しない。user context または read-only identity command で確認し、未解決 target は development ではなく unknown と扱う。

read-only discovery、plan/dry-run、mutation の順を優先し、mutation の前に plan/diff を確認する。すべての mutation は target と effect に対する明示承認でカバーされる必要がある。read-only identity check は mutation 承認を必要としない。

## Approval Prompt

承認前に具体的な plan/diff/commands を準備し、レビュー可能にする。既存の session 承認でカバーされる場合は再質問せず続行する。不足する承認がある場合だけ、次の項目を必要に応じて提示する。

```text
Please confirm this external operation before I run it:
- Plan/diff/commands: ...
- Environment/account/region/context: ...
- Target resources: ...
- Expected effect: ...
- Permitted follow-up corrections/retries: ...
- Rollback/recovery plan: ...
- Cost/blast radius: ...
```

target、effect、許可された追加修正、回復範囲、material cost/blast radius が承認内にある限り、承認は継続する。構文修正や同等の command への変更だけでは再確認しない。ただし user が exact command だけを承認した場合は、その限定を守る。

失敗・結果不明の mutation を retry する前に実状態を確認し、安全かつ承認範囲内の場合だけ続ける。新しい target、effect の拡大、追加の破壊的操作、security policy 変更、重要な費用・影響範囲の増加、承認外の回復操作では再承認を求める。範囲や現在状態が不明なら依存する mutation を止め、安全な read-only 調査は続ける。runtime approval や secret handling の制限は上書きしない。

## Handoff

operation class、confirmed target identity、plan evidence、既存承認とその範囲、未承認の action、unresolved target risk を引き継ぐ。最初の command 成功で止まらず、承認された outcome を検証し、失敗や user-only blocker を報告する。
