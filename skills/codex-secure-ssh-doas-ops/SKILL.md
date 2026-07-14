---
name: codex-secure-ssh-doas-ops
description: Perform authorized remote Linux or Alpine deployment and maintenance over SSH when login or doas needs interactive authentication, while keeping passwords out of chat, agent-visible tool calls, command arguments, scripts, logs, and captured output. Use for SSH targets where Codex must establish key-based automation, doas reports that a TTY or authentication is required, or an elevated one-shot installer must be run with the user entering the password directly in a visible terminal.
---

# Secure SSH and doas Operations

Keep SSH transport automation separate from privileged authentication. Let the user type passwords only into the native SSH or doas prompt in a visible terminal; never receive or relay the password.

Use after `codex-cloud-ops-intake` has classified the operation and established the approval boundary. This skill carries out only the authorized SSH and doas execution path; it does not broaden the approved target, command, or effect.

## Non-negotiable rules

- Obtain authorization for the remote-changing task before uploading, installing, restarting, or editing the target.
- Never ask the user to paste a password into chat.
- Never place passwords in command arguments, environment variables, files, scripts, process launch arguments, `sshpass`, `plink -pw`, stdin pipes, or captured tool output.
- Never read, print, summarize, or copy private-key contents. Passing an already-approved private-key path to `ssh` or `scp` is acceptable.
- Treat adding a public key to `authorized_keys` as a persistent security change. Explain it and obtain approval before doing it.
- Do not create a broad temporary `NOPASS` doas rule merely to automate a task. Prefer one interactive elevation of a transparent one-shot script.
- Do not assume doas authentication persists across SSH sessions or TTYs.
- Preserve host-key checking. Do not use `StrictHostKeyChecking=no` as a convenience.

## 1. Separate the two authentication layers

Diagnose SSH login and privilege elevation independently.

Test noninteractive SSH first:

```powershell
ssh -i "<private-key-path>" `
  -o BatchMode=yes `
  -o ConnectTimeout=7 `
  -o StrictHostKeyChecking=yes `
  <user>@<host> hostname
```

Interpret the result:

- Success: SSH automation is ready. Continue to the doas probe.
- `Permission denied`: the public key is not accepted. Use the public-key registration path below or ask the user to operate an interactive SSH session.
- Host-key error: stop and reconcile the expected fingerprint or known-host entry. Do not bypass it.

Probe doas without prompting:

```powershell
ssh -tt -i "<private-key-path>" `
  -o BatchMode=yes `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "doas -n true"
```

Interpret the result:

- Success: noninteractive elevation is already authorized for this command.
- `a tty is required`: use `ssh -tt` for privileged execution.
- `Authentication required`: keep key-based SSH, but arrange a visible terminal for the user to enter the doas password.

## 2. Establish key-based SSH without exposing the login password

Prefer an existing dedicated key. List key filenames if needed, but do not open private keys.

If the remote host does not accept the key, ask the user to run a local command that pipes only the public key into the native SSH prompt. State that this permanently updates `authorized_keys`.

Example for PowerShell:

```powershell
Get-Content "<public-key-path>" |
  ssh <user>@<host> 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'
```

The user enters the SSH password locally. The agent never sees it. Re-run the `BatchMode=yes` probe afterward.

If persistent public-key registration is not approved, do not invent a credential workaround. Ask the user to run the final interactive SSH command themselves.

## 3. Build a transparent one-shot privileged script

When doas needs a password, consolidate the authorized privileged work into one reviewable script rather than triggering many prompts.

The script must:

- start with `set -eu`;
- assert the expected hostname, required files, service state, and safety gates before mutation;
- use explicit absolute paths for sensitive targets;
- avoid reading or printing secrets and configuration contents not required for verification;
- stage changes safely before persistence when the target supports it;
- leave risky capabilities disabled unless the user explicitly authorized them;
- verify the integrated result;
- write a success marker only after every required step passes.

Example skeleton:

```sh
#!/bin/sh
set -eu

SUCCESS_MARKER=/tmp/example-deploy-success
rm -f "$SUCCESS_MARKER"

[ "$(hostname)" = "<expected-hostname>" ]
[ -f "<required-file>" ]

# Authorized install or maintenance steps go here.

<service-status-check>
date -Is > "$SUCCESS_MARKER"
echo "Deployment completed"
```

Create task-specific scripts with `apply_patch`, validate their syntax locally, and record a SHA-256 hash. Upload them as the unprivileged SSH user into a dedicated mode-0700 staging directory, then confirm the remote hash before launch. Avoid executing a generally writable `/tmp` script as root on a multi-user host. Do not embed a password or secret in the script.

## 4. Run doas in a visible user-controlled terminal

Use a native visible terminal because the user must see and control the password prompt. On Windows, launching PowerShell with `Start-Process` is appropriate for this interactive case.

The elevated remote command should be structurally equivalent to:

```powershell
ssh -tt -i "<private-key-path>" `
  -o BatchMode=yes `
  -o ConnectTimeout=7 `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "doas sh /tmp/<one-shot-script>.sh"
```

Replace the example `/tmp` path with the verified private staging path when the target is multi-user. Treat a hash mismatch, unexpected owner, or permissive mode as a stop condition.

Before opening the terminal, tell the user:

- which window will appear;
- that the prompt is the remote doas prompt;
- to type the password there, not in chat;
- that the agent cannot see the input.

If no GUI or visible-terminal mechanism is available, give the exact command to the user and wait for confirmation. Do not downgrade to password capture.

## 5. Observe completion through a separate key-based channel

Do not scrape the interactive terminal for credentials or rely only on its process exit. Poll the non-secret success marker over the already-working key-based SSH connection:

```powershell
ssh -i "<private-key-path>" `
  -o BatchMode=yes `
  -o StrictHostKeyChecking=yes `
  <user>@<host> "test -f /tmp/<success-marker>"
```

While waiting:

- report that interactive authentication may still be in progress;
- poll at a modest interval;
- if the marker does not appear, inspect only non-secret service state and process liveness;
- do not infer success just because the visible terminal closed.

After the marker appears, independently verify the acceptance criteria: service status, network state, process liveness, persistence, safety gates, uptime, and bounded recent logs.

## 6. Handle follow-up elevation safely

If verification finds a problem requiring another privileged change:

1. Explain the evidence and proposed narrow remediation.
2. Create a second small, reviewable script.
3. Validate and upload it.
4. Open a new visible `ssh -tt ... doas sh ...` session.
5. Expect another password prompt.
6. Poll a distinct success marker and re-verify.

Do not reuse or cache the password, and do not broaden doas policy to avoid the second prompt.

## 7. Finish cleanly

- Remove local temporary scripts created solely for the operation.
- Remove remote unprivileged temporary files when safe and authorized. Root-owned `/tmp` markers may be left until reboot if deleting them would require unnecessary elevation.
- Leave the user's visible terminal open when its output is useful for review; tell the user it can be closed afterward.
- Report what changed, what was verified, which safety gates remain disabled, and any residual issue.
- Classify readiness honestly. Successful installation does not erase an external HTTP, DNS, network, or application failure found during verification.
