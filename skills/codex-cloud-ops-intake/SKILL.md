---
name: codex-cloud-ops-intake
description: Classify and gate cloud, infrastructure, database, deployment, and migration work before execution. Use when Codex is asked to inspect or change AWS, Terraform, Kubernetes, Helm, CDK, SAM, Serverless Framework, Pulumi, databases, production or staging resources, deployments, migrations, remote state, cost-incurring resources, or any operation with external side effects.
---

# Codex Cloud Ops Intake

Use this skill before any cloud, infrastructure, database, deployment, or migration command. The goal is to make the target, effect, and approval boundary explicit before Codex touches external state.

## Intake

Record these facts before choosing commands:

1. Provider or system: AWS, Terraform, Kubernetes, Helm, CDK, SAM, Serverless, Pulumi, database, deployment tool, or other.
2. Account, profile, project, cluster, context, region, namespace, database, or endpoint.
3. Environment: production, staging, development, local, or unknown.
4. Operation class:
   - `read-only`: list, describe, status, diff, logs, or explain commands that should not mutate state.
   - `dry-run/plan`: commands such as `terraform plan`, `kubectl diff`, or deployment previews that may read remote state but should not mutate it.
   - `remote mutation`: create, update, deploy, apply, migrate, scale, restart, write, import, or restore.
   - `destructive mutation`: delete, destroy, drop, truncate, purge, prune, force replace, rollback with data loss, or volume removal.
5. Target resources and expected effect.
6. Cost and blast radius.
7. Rollback or recovery path, including whether it has been tested.

## Decision Rules

- Prefer read-only discovery before plan/dry-run, and prefer plan/dry-run before mutation.
- Treat production, staging, and unknown environments as high risk. Unknown is not development.
- Do not run remote mutation or destructive mutation commands without explicit user approval for the exact command, target resources, expected effect, and rollback plan.
- Do not infer AWS profile, Kubernetes context, Terraform workspace, database endpoint, or region from convenience. Confirm it or read it with a read-only command first.
- Do not handle secrets, credentials, kubeconfigs, `.env` files, private keys, or tokens unless the user explicitly asks and the task requires it.
- For database work, prefer transaction-wrapped read-only inspection and backups before any write, migration, or destructive operation.
- For infrastructure as code, inspect the diff or plan output before apply/deploy. If the plan is unavailable or ambiguous, stop and ask.

## Approval Prompt

For any remote mutation or destructive mutation, ask for approval in this shape:

```text
Please confirm this external operation before I run it:
- Command: ...
- Environment/account/region/context: ...
- Target resources: ...
- Expected effect: ...
- Rollback/recovery plan: ...
- Cost/blast radius: ...
```

Run only the confirmed command. If the command changes, ask again.

## Output

When handing off to implementation or debugging, include:

- operation class
- confirmed environment and target
- safe read-only or dry-run commands already run
- commands still requiring explicit approval
- assumptions and unresolved risks
