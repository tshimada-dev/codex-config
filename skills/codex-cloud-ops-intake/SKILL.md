---
name: codex-cloud-ops-intake
description: Establish target identity and approval scope before operating on cloud resources, infrastructure, or a live database, or executing a deployment or migration.
---

# Codex Cloud Ops Intake

Use this skill when commands select or operate on an actual environment. Local SQL/schema editing, migration-file authoring, disposable fixture tests, and ordinary Git/PR operations do not trigger this skill by themselves. Its purpose is to prevent operations against an assumed target and to establish bounded authorization for mutations.

## Shared Safety Boundary

<!-- workflow-invariant: shared-contract -->

General approval, destructive-operation, repository-trust, and secret-handling rules come from [`../../rules/development-workflow.md`](../../rules/development-workflow.md). This skill adds cloud target identity and the approval packet below.

## Target And Operation

Before choosing a command:

1. Identify the provider or system and environment.
2. Establish the exact account/profile/project, region, cluster/context/namespace, Terraform workspace, or database endpoint that selects the target.
3. Classify the operation as `read-only`, `plan/dry-run`, `remote mutation`, or `destructive mutation`.
4. For mutations, record the target resources, expected effect, rollback/recovery path, and material cost or blast radius.

Never infer an AWS profile, Kubernetes context, Terraform workspace, database endpoint, region, account, or environment for convenience. Confirm it from user-provided context or a read-only identity command. Treat an unresolved target as unknown, not development.

Prefer read-only discovery before plan/dry-run and inspect the plan or diff before mutation. Every mutation must be covered by explicit user authorization for its target and effects. Read-only identity checks do not require mutation approval.

## Approval Prompt

Before seeking approval, prepare the concrete plan, diff, or commands that make the operation reviewable. Check existing session authorization first. If it already covers the operation, continue without asking again. Otherwise request the missing authorization, using the following fields as needed:

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

Carry authorization forward only while target, intended effect, permitted follow-up work, recovery bounds, and material cost/blast radius remain within the approved scope. A syntax correction or equivalent command does not by itself require renewed approval. If the user approved only an exact command, preserve that narrower restriction.

Before retrying a failed or ambiguous mutation, inspect the actual state; continue only if the retry is safe and covered by authorization. Ask again for a new target, expanded effects, additional destructive action, security-policy change, increased material cost/blast radius, or recovery beyond the approved bounds. Stop dependent mutations if these bounds or the current state are unresolved; continue safe read-only work. These rules do not override runtime approvals or secret-handling restrictions.

## Handoff

Carry forward the operation class, confirmed target identity, plan evidence, existing authorization and its bounds, actions still awaiting approval, and unresolved target risk. Finish by verifying the approved outcome; report any failure or user-only blocker instead of stopping after the first command succeeds.
