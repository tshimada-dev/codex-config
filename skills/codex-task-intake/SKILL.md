---
name: codex-task-intake
description: Resolve one material ambiguity or authority boundary before execution. Use when a wrong assumption would materially change the target, safety boundary, external effect, or requested deliverable and the answer cannot be discovered safely from available context.
---

# Codex Task Intake

Use this skill as an optional ambiguity gate, not as the default entry point for routine work. Capable models should classify ordinary answer, inspection, editing, planning, and automation requests without a separate intake ritual.

## Shared Development Contract

<!-- workflow-invariant: shared-contract -->

For development work, read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). Repository trust, worktree preservation, evidence, and mutation approval remain owned by shared rules rather than this skill.

## Narrow Gate

1. State the intended outcome in one sentence.
2. Identify the single unresolved decision or risk that could materially change the result.
3. Resolve it from existing instructions or safe read-only context when possible.
4. Ask at most one concise question only when proceeding would require a consequential guess.
5. Once the target and authority are clear, continue with the naturally applicable task workflow.

For cloud, infrastructure, database, deployment, migration, production/staging, or other remote operational work, use `codex-cloud-ops-intake` before executing commands.

## Stop Condition

Stop intake as soon as the execution path is safe and materially unambiguous. Do not produce a classification table or fixed output shape unless the user asked for one.
