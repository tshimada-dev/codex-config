---
source: skills/codex-cloud-ops-intake/SKILL.md
source_commit: 6028112a9087ea2d4d19e0f1be526c08a7091f1a
canonical: false
---

# codex-cloud-ops-intake 日本語参考訳

この文書は `skills/codex-cloud-ops-intake/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

Cloud、infrastructure、database、deployment、migration command を実行する前に、対象、影響、承認境界を明確にする。

## Intake

command を選ぶ前に、以下を記録する。

1. Provider / system: AWS、Terraform、Kubernetes、Helm、CDK、SAM、Serverless、Pulumi、database、deployment tool など。
2. Account、profile、project、cluster、context、region、namespace、database、endpoint。
3. Environment: production、staging、development、local、unknown。
4. Operation class:
   - `read-only`: list、describe、status、diff、logs、explain など、state を変更しない command。
   - `dry-run/plan`: `terraform plan`、`kubectl diff`、deployment preview など、remote state を読む可能性はあるが変更しない command。
   - `remote mutation`: create、update、deploy、apply、migrate、scale、restart、write、import、restore。
   - `destructive mutation`: delete、destroy、drop、truncate、purge、prune、force replace、data loss を伴う rollback、volume removal。
5. Target resources と expected effect。
6. Cost と blast radius。
7. Rollback / recovery path と、それが検証済みか。

## Decision Rules

- mutation より先に plan/dry-run を優先し、plan/dry-run より先に read-only discovery を優先する。
- production、staging、unknown environment は high risk として扱う。unknown は development ではない。
- remote mutation / destructive mutation は、exact command、target resources、expected effect、rollback plan に対する user の明示承認なしに実行しない。
- AWS profile、Kubernetes context、Terraform workspace、database endpoint、region を便利だからという理由で推測しない。確認するか、read-only command で読む。
- secrets、credentials、kubeconfigs、`.env` files、private keys、tokens は、user が明示的に依頼し、task に必要な場合だけ扱う。
- database work では、write、migration、destructive operation より前に、transaction-wrapped read-only inspection と backup を優先する。
- infrastructure as code では、apply/deploy の前に diff または plan output を確認する。plan が無い、または曖昧なら停止して質問する。

## Approval Prompt

remote mutation / destructive mutation では、以下の形で承認を求める。

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

## Output

implementation / debugging に渡すときは、operation class、confirmed environment and target、実行済みの safe read-only / dry-run command、まだ承認が必要な command、assumptions and unresolved risks を含める。
