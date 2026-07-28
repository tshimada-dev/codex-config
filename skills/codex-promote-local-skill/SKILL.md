---
name: codex-promote-local-skill
description: Assess whether a local Codex Skill outside codex-config should be repository-managed, then safely promote, merge, or retain it. Use when Codex is asked to inspect newly added local Skills, judge repository-management value, harden or rename a Skill to the codex-* convention, add tests and Japanese references, commit it, install the committed version into CODEX_HOME, and remove the old Skill only after exact verification.
---

# Promote Local Skill

Evaluate local Skills consistently and make repository promotion recoverable and auditable.

## Shared development contract

Read and follow [`../../rules/development-workflow.md`](../../rules/development-workflow.md). Use `codex-repo-scout` for repository evidence, hand durable edits to `codex-implementation`, and use `codex-pr-readiness` for staging and commit readiness. Use `$skill-creator` when creating or substantially restructuring the promoted Skill.

## Authority modes

Classify the user's request before changing files:

- `assess`: inspect and report `promote`, `merge`, or `keep-local`; do not edit, commit, install, rename, or delete.
- `promote`: implement and commit the repository-managed Skill, but do not install or remove the local source unless requested.
- `full-migration`: assess, implement, commit, install from the commit, verify, and remove the old Skill when the user explicitly requested the complete workflow.

Do not infer permanent deletion authority from an assessment request.

## Safety invariants

- Treat the original local Skill as user-owned until final removal is verified and authorized.
- Never inspect or report the contents of `.env`, credentials, private keys, auth files, or other sensitive-looking files.
- Reject symbolic links, junctions, sensitive-looking files, and unexpected files instead of following, copying, or deleting them.
- Keep runtime noise such as `__pycache__`, `.pyc`, `.DS_Store`, and `Thumbs.db` out of the repository.
- Commit before installation. Install only tracked content from repository `HEAD`.
- Remove the old Skill last. Never remove it when the installed tree, managed manifest, commit, or original snapshot differs.
- Preserve unrelated dirty-worktree changes and unrelated Skills.

## 1. Snapshot the local source

Resolve absolute paths for the repository, `CODEX_HOME`, source Skill, proposed repository Skill, and installed target. Store the snapshot outside the source Skill and outside tracked repository paths.

```powershell
python scripts/audit_skill_promotion.py snapshot `
  --path "$OldSkill" `
  --output "$AuditSnapshot"
```

The snapshot records relative paths, sizes, hashes, and sensitive-looking path names without exposing file contents. Stop if it reports sensitive-looking paths or unsupported links. Do not silently exclude a real source file merely to make promotion pass.

## 2. Decide management value

Use `codex-repo-scout` to compare the local Skill with repository Skill descriptions, roles, dependencies, scripts, and tests.

Choose `promote` only when all applicable conditions hold:

- the workflow is reusable beyond one transient task;
- it does not depend on private data, secrets, or one machine's accidental state;
- repository maintenance, distribution, and version history add value;
- it has a distinct trigger and does not substantially duplicate an existing Skill;
- behavior can be validated with a deterministic test or a credible explicit check;
- its operational risk can be bounded by clear authority and failure rules.

Choose `merge` when an existing Skill owns the same trigger or workflow and can absorb the useful parts without becoming incoherent.

Choose `keep-local` when the Skill is personal, ephemeral, secret-bearing, machine-specific, too narrow to maintain, or not independently testable.

Report the decision and evidence. In `assess` mode, stop here.

## 3. Implement a promotion or merge

For promotion:

1. Select a concise `codex-*` name under 64 characters. Rename only when it improves convention, triggering, or collision avoidance.
2. Scaffold a new Skill with `$skill-creator`; do not move or mutate the original local directory.
3. Migrate only essential instructions, scripts, references, and assets. Replace absolute machine paths and personal assumptions with parameters or documented prerequisites.
4. Add or refresh `agents/openai.yaml`.
5. Add focused tests for scripts and fragile workflow rules.
6. Integrate the Skill into:
   - `config/development-skills.json`;
   - relevant `.github/workflows/validate.yml` checks;
   - `docs/ja/skills/<skill-name>.md`;
   - `docs/ja/README.md`.
7. Update Japanese source metadata with `scripts/check-ja-source-commits.ps1 -Update`.

For merge, edit the owning Skill through `codex-implementation`, add regression evidence, and do not create a redundant Skill directory.

## 4. Verify and commit before installation

Run the Skill validator:

```powershell
python "$SkillCreatorRoot/scripts/quick_validate.py" "$RepoRoot/skills/$SkillName"
```

Run focused tests first, followed by repository workflow validation, installer dry runs, Copilot packaging checks, and Japanese metadata checks when applicable.

Use `codex-pr-readiness` to review the scoped diff and stage only promotion files. Commit the coherent change before touching the installed target. Do not install from an uncommitted or partially staged Skill tree.

## 5. Install the committed Skill

Run the repository installer with `-WhatIf -Overwrite` first. Continue only when the planned overwrites are the promoted Skill and managed manifest; stop if unrelated managed files would change.

```powershell
pwsh -NoProfile -File "$RepoRoot/scripts/install.ps1" `
  -CodexHome "$CodexHome" -Overwrite
```

Verify the committed repository tree, installed tree, and managed manifest:

```powershell
python scripts/audit_skill_promotion.py verify-install `
  --repo-root "$RepoRoot" `
  --skill-name "$SkillName" `
  --codex-home "$CodexHome"
```

If the local source already used the final Skill name, this is an in-place promotion. Do not perform a separate old-directory deletion.

## 6. Remove the old renamed Skill last

Proceed only in `full-migration` mode with explicit old-Skill removal authority. Verify that the old source is unchanged since assessment and that the installed target exactly matches the committed Skill:

```powershell
python scripts/audit_skill_promotion.py verify-removal `
  --repo-root "$RepoRoot" `
  --skill-name "$SkillName" `
  --codex-home "$CodexHome" `
  --old-skill-path "$OldSkill" `
  --source-snapshot "$AuditSnapshot"
```

Require `ready_for_old_skill_removal: true`. Then resolve the old path again and require that it is a direct child of `CODEX_HOME/skills`, differs from the installed target, and exactly matches the audited path. Delete only that literal directory with the platform-native filesystem command. On Windows, keep path validation and `Remove-Item -LiteralPath -Recurse -Force` in the same PowerShell process.

After removal:

- confirm the old directory is absent;
- rerun `verify-install`;
- confirm the repository contains no unexpected changes;
- report the commit, installed file count, removed old path, and any unrelated worktree state left untouched.

## Failure handling

- If the snapshot changes, stop and review the new source state before creating a replacement snapshot.
- If promotion value is uncertain, prefer `keep-local` or `merge`; do not create a repository Skill merely to mirror every local directory.
- If tests or repository validation fail, do not commit or install.
- If installation differs from the committed tree or manifest, preserve both Skills and diagnose.
- If removal verification fails, preserve the old Skill and do not broaden the deletion scope.

## Bundled script

- `scripts/audit_skill_promotion.py`: content-blind source snapshots, committed-install verification, and exact old-Skill removal readiness.
- `scripts/test_audit_skill_promotion.py`: disposable regression tests for sensitive paths, runtime noise, tree mismatches, manifest coverage, and source preservation.
