---
source: skills/codex-wsl-command-bridge/SKILL.md
source_commit: 7f793288408b1425ed8d57ea4c2d4fd84f2d00e7
canonical: false
---

# codex-wsl-command-bridge 日本語参考訳

この文書は `skills/codex-wsl-command-bridge/SKILL.md` の日本語参考訳です。Codex が実行時に読む canonical な定義は英語版です。

## 目的

Windows PowerShell 上で動く Codex から WSL/Linux の command を実行するときに、PowerShell と Bash の quote、path、改行の違いによる事故を避ける。

## 判断ルール

短く、read-only で、quote が複雑でない command だけは inline WSL を使ってよい。

```powershell
wsl bash -lc 'pwd && uname -a'
```

次のいずれかを含む場合は helper script を優先する。

- `$target` や `$pid` などの Bash variables
- `$(pwd)` などの command substitution
- loops、conditionals、here-docs、multi-line scripts
- nested quotes、JSON、YAML、sed/awk/perl snippets、regexes
- Windows path conversion
- file creation、edits、copies、moves、deletes
- 特定の WSL checkout で実行する Git operations

## Helper Script

複雑な作業では `scripts/Invoke-WslScript.ps1` を使う。helper は Bash script を UTF-8 LF の一時ファイルとして Windows temp に書き、WSL path に変換して `wsl bash` で実行し、最後に一時ファイルを削除する。

helper に渡す script には secrets、tokens、credentials、private keys、sensitive customer data を含めない。一時 script は短時間だが Windows filesystem 上に plain text として存在する。

例:

```powershell
$skill = "$env:USERPROFILE\.codex\skills\codex-wsl-command-bridge"
& "$skill\scripts\Invoke-WslScript.ps1" -Script @'
set -euo pipefail
cd /home/<user>/projects/example
git status --short --branch
'@
```

distro 名は必要な場合だけ指定する。

```powershell
& "$skill\scripts\Invoke-WslScript.ps1" -Distro Ubuntu-24.04 -Script @'
set -euo pipefail
uname -a
'@
```

## Path Rules

- WSL command 内では `/home/<user>/projects/example` のような Linux paths を使う。
- Windows UI や app access だけに `\\wsl.localhost\Ubuntu-24.04\home\<user>\projects\example` のような UNC path を使う。
- `/mnt/c/...` は Windows filesystem を意図的に読み書きするときだけ使う。
- Windows path から WSL path を作るときは manual string concatenation を避け、helper または `wslpath` を使う。

## Safety Rules

WSL で recursive delete または move を行う前に:

1. destructive または作業を失う可能性がある操作では user の明示承認を得る。
2. `readlink -f` で target を resolve する。
3. resolve 後の path が期待した path そのもの、または期待した parent の内側であることを確認する。
4. path variable を quote する。

Pattern:

```bash
target="/home/<user>/projects/example"
resolved="$(readlink -f "$target")"
case "$resolved" in
  /home/<user>/projects/example|/home/<user>/projects/example/*) ;;
  *) echo "Refusing unexpected path: $resolved" >&2; exit 1 ;;
esac
rm -rf -- "$target"
```

user が明示的に依頼し、task に必要な場合を除き、WSL 内の secrets を inspect、print、copy、summarize しない。

## Git Workflow In WSL

user が Linux-native work を望む場合は、WSL checkout を authoritative として扱う。

```bash
cd /home/<user>/projects/example
git status --short --branch
```

remote operation には WSL 側の Git credentials を使う。GitHub authentication が失敗した場合は、WSL で `gh auth login --hostname github.com --git-protocol https --web` を提案する。

## Reporting

final answer では、触った Linux path と重要な command result を報告する。bridge 自体を debug している場合を除き、helper の内部処理を長く説明しない。
