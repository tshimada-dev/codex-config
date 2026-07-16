---
name: codex-cloud-ops-intake
description: Classify and gate cloud, infrastructure, database, deployment, and migration work before execution. Use when Codex is asked to inspect or change AWS, Terraform, Kubernetes, Helm, CDK, SAM, Serverless Framework, Pulumi, databases, production or staging resources, deployments, migrations, remote state, cost-incurring resources, or any operation with external side effects.
---

# Codex Cloud Ops Intake

Use this skill before cloud, infrastructure, database, deployment, or migration commands. Its narrow purpose is to prevent operations against an assumed target and to produce an exact approval packet for mutations.

## Shared Safety Boundary

<!-- workflow-invariant: shared-contract -->

General approval, destructive-operation, repository-trust, and secret-handling rules come from [`../../rules/development-workflow.md`](../../rules/development-workflow.md). This skill adds cloud target identity and the approval packet below.

## Target And Operation

Before choosing a command:

1. Identify the provider or system and environment.
2. Establish the exact account/profile/project, region, cluster/context/namespace, Terraform workspace, or database endpoint that selects the target.
3. Classify the operation as `read-only`, `plan/dry-run`, `remote mutation`, or `destructive mutation`.
4. Record the target resources, expected effect, rollback/recovery path, and material cost or blast radius.

Never infer an AWS profile, Kubernetes context, Terraform workspace, database endpoint, region, account, or environment for convenience. Confirm it from user-provided context or a read-only identity command. Treat an unresolved target as unknown, not development.

Prefer read-only discovery before plan/dry-run and inspect the plan or diff before mutation. Any mutation requires approval for the exact command and target.

## Approval Prompt

For a remote or destructive mutation, ask in this fixed shape:

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

## Handoff

Carry forward the operation class, confirmed target identity, read-only or plan evidence, exact commands still awaiting approval, and unresolved target risk.
