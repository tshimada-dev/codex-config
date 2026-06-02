param(
    [string]$RepoPath = (Get-Location).Path,
    [string]$Scope = "",
    [string]$ExtraPrompt = "",
    [string]$OutFile = "",
    [decimal]$MaxBudgetUsd = 2.00,
    [int]$MaxPromptChars = 200000,
    [switch]$Run
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([string[]]$Arguments)

    $output = & git @Arguments 2>&1 | ForEach-Object { $_.ToString() }
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed:$([Environment]::NewLine)$($output -join [Environment]::NewLine)"
    }

    return $output
}

function Test-SensitiveName {
    param([string]$Value)

    $pattern = "(?i)(^|[\\/])\.env($|[.\-/])|(^|[\\/])\.npmrc$|(^|[\\/])\.netrc$|secret|token|credential|password|passwd|auth|api[-_]?key|private[-_]?key|\.pem$|\.p12$|\.pfx$|\.key$|\.p8$|id_rsa|cookies?|kubeconfig|(^|[\\/])\.kube([\\/]|$)"
    return $Value -match $pattern
}

function Test-SensitiveDiffLine {
    param([string]$Value)

    if ($Value -notmatch "^[+-]" -or $Value -match "^(\+\+\+|---) ") {
        return $false
    }

    $pattern = "(?i)((api[_-]?key|access[_-]?token|refresh[_-]?token|id[_-]?token|password|passwd|secret|credential|private[_-]?key|client[_-]?secret)\s*[:=]|authorization\s*:|bearer\s+[A-Za-z0-9._~+/=-]+)"
    return $Value -match $pattern
}

$resolvedRepo = (Resolve-Path -LiteralPath $RepoPath).Path
Push-Location $resolvedRepo
try {
    $gitRootLines = @(Invoke-Git @("rev-parse", "--show-toplevel"))
    $gitRoot = $gitRootLines[0]
    if (-not $gitRoot) {
        throw "Not inside a git repository: $resolvedRepo"
    }

    $claude = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claude) {
        throw "Claude Code CLI was not found on PATH. Install or expose the 'claude' command first."
    }

    $status = @(Invoke-Git @("status", "--short"))
    if ($status.Count -eq 0) {
        throw "No git changes found to review."
    }

    $changedNames = @()
    $changedNames += @(Invoke-Git @("diff", "--name-only"))
    $changedNames += @(Invoke-Git @("diff", "--cached", "--name-only"))
    $changedNames += @(Invoke-Git @("ls-files", "--others", "--exclude-standard"))
    $changedNames = @($changedNames | Where-Object { $_ } | Sort-Object -Unique)

    $sensitiveNames = @($changedNames | Where-Object { Test-SensitiveName -Value $_ })
    if ($sensitiveNames.Count -gt 0) {
        $list = $sensitiveNames -join [Environment]::NewLine
        throw "Refusing to build a Claude review prompt because changed file names look sensitive:$([Environment]::NewLine)$list"
    }

    $unstagedStat = @(Invoke-Git @("diff", "--stat"))
    $stagedStat = @(Invoke-Git @("diff", "--cached", "--stat"))
    $unstagedDiff = @(Invoke-Git @("diff", "--no-ext-diff", "--unified=80"))
    $stagedDiff = @(Invoke-Git @("diff", "--cached", "--no-ext-diff", "--unified=80"))
    $untracked = @(Invoke-Git @("ls-files", "--others", "--exclude-standard"))
    $allDiffLines = @($unstagedDiff + $stagedDiff)

    $sensitiveDiffLines = @($allDiffLines | Where-Object { Test-SensitiveDiffLine -Value $_ })
    if ($sensitiveDiffLines.Count -gt 0) {
        throw "Refusing to build a Claude review prompt because the diff contains sensitive-looking added or removed lines. Narrow the diff or review locally."
    }

    $prompt = @"
Review the included Codex work as a senior code reviewer.
Do not modify files. Base your answer only on the provided context.
Prioritize correctness bugs, regressions, security/privacy issues, data loss, and missing tests.
Return findings first, ordered by severity, with file/path references when possible.
If there are no material issues, say so clearly and note residual risk.

Repository: $gitRoot
Scope: $Scope
Additional context: $ExtraPrompt

Important constraints:
- This is an external read-only review request.
- Do not ask to run commands or edit files.
- Untracked file contents are not included unless they are also present in a staged diff.

Git status:
``````
$($status -join [Environment]::NewLine)
``````

Changed files:
``````
$($changedNames -join [Environment]::NewLine)
``````

Unstaged diff stat:
``````
$($unstagedStat -join [Environment]::NewLine)
``````

Staged diff stat:
``````
$($stagedStat -join [Environment]::NewLine)
``````

Untracked files:
``````
$($untracked -join [Environment]::NewLine)
``````

Unstaged diff:
``````
$($unstagedDiff -join [Environment]::NewLine)
``````

Staged diff:
``````
$($stagedDiff -join [Environment]::NewLine)
``````
"@

    if ($prompt.Length -gt $MaxPromptChars) {
        throw "Refusing to call Claude because the review prompt is $($prompt.Length) characters, above MaxPromptChars=$MaxPromptChars. Split the diff by subsystem."
    }

    $promptPath = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-claude-code-review-" + [System.Guid]::NewGuid().ToString("N") + ".md")
    Set-Content -LiteralPath $promptPath -Value $prompt -Encoding UTF8

    if (-not $Run) {
        Write-Output "Prompt written to: $promptPath"
        Write-Output "Preview command:"
        Write-Output "Get-Content -Raw '$promptPath' | claude -p --input-format text --output-format text --tools '' --max-budget-usd $MaxBudgetUsd"
        return
    }

    $claudeArgs = @(
        "-p",
        "--input-format", "text",
        "--output-format", "text",
        "--tools", "",
        "--max-budget-usd", $MaxBudgetUsd.ToString([Globalization.CultureInfo]::InvariantCulture)
    )

    $result = Get-Content -Raw -LiteralPath $promptPath | & claude @claudeArgs
    if ($OutFile) {
        Set-Content -LiteralPath $OutFile -Value ($result -join [Environment]::NewLine) -Encoding UTF8
        Write-Output "Claude review written to: $OutFile"
    }
    else {
        $result
    }
}
finally {
    Pop-Location
}
