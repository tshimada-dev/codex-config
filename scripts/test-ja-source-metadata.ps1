[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$Checker = Join-Path $ScriptDir "check-ja-source-commits.ps1"
$TempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd(
    [System.IO.Path]::DirectorySeparatorChar,
    [System.IO.Path]::AltDirectorySeparatorChar
)
$RepoRoot = Join-Path $TempBase ("codex-config-ja-metadata-" + [guid]::NewGuid().ToString("N"))

function Invoke-RepoGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $output = & git -C $RepoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed"
    }
    return $output
}

function Set-Utf8NoBomContent {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Value, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-MetadataCheck {
    param([string[]]$Arguments = @())

    & pwsh -NoProfile -File $Checker -RepositoryRoot $RepoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "check-ja-source-commits.ps1 $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

try {
    New-Item -ItemType Directory -Path $RepoRoot -Force | Out-Null
    Invoke-RepoGit -Arguments @("init", "--quiet") | Out-Null
    Invoke-RepoGit -Arguments @("config", "user.name", "Codex Metadata Test") | Out-Null
    Invoke-RepoGit -Arguments @("config", "user.email", "codex-metadata-test@example.invalid") | Out-Null

    $sourcePath = Join-Path $RepoRoot "rules/sample.md"
    $translationPath = Join-Path $RepoRoot "docs/ja/sample.md"
    Set-Utf8NoBomContent -Path $sourcePath -Value "# Sample`n`nVersion one.`n"
    Invoke-RepoGit -Arguments @("add", "rules/sample.md") | Out-Null
    Invoke-RepoGit -Arguments @("commit", "--quiet", "-m", "add sample source") | Out-Null
    $sourceCommit = Invoke-RepoGit -Arguments @("rev-parse", "HEAD") | Select-Object -First 1

    Set-Utf8NoBomContent -Path $translationPath -Value @"
---
source: rules/sample.md
source_commit: $sourceCommit
canonical: false
---

# Sample 日本語

Version one.
"@
    Invoke-RepoGit -Arguments @("add", "docs/ja/sample.md") | Out-Null
    Invoke-RepoGit -Arguments @("commit", "--quiet", "-m", "add sample translation") | Out-Null

    Set-Utf8NoBomContent -Path $sourcePath -Value "# Sample`n`nVersion two.`n"
    Set-Utf8NoBomContent -Path $translationPath -Value @"
---
source: rules/sample.md
source_commit: $sourceCommit
canonical: false
---

# Sample 日本語

Version two.
"@

    $beforeWhatIfHash = (Get-FileHash -LiteralPath $translationPath).Hash
    Invoke-MetadataCheck -Arguments @("-Update", "-WhatIf")
    $afterWhatIfHash = (Get-FileHash -LiteralPath $translationPath).Hash
    if ($beforeWhatIfHash -ne $afterWhatIfHash) {
        throw "-Update -WhatIf modified the translation file"
    }

    Invoke-MetadataCheck -Arguments @("-Update")
    $currentBlob = Invoke-RepoGit -Arguments @("hash-object", "--", "rules/sample.md") | Select-Object -First 1
    $updatedTranslation = Get-Content -LiteralPath $translationPath -Raw
    if ($updatedTranslation -notmatch "(?m)^source_blob:\s*$currentBlob\s*$" -or $updatedTranslation -match "(?m)^source_commit:") {
        throw "tracked translation was not migrated to the current source_blob"
    }

    Invoke-RepoGit -Arguments @("add", "rules/sample.md", "docs/ja/sample.md") | Out-Null
    Invoke-RepoGit -Arguments @("commit", "--quiet", "-m", "update source and translation together") | Out-Null
    Invoke-MetadataCheck

    $newSourcePath = Join-Path $RepoRoot "rules/new-source.md"
    $newTranslationPath = Join-Path $RepoRoot "docs/ja/new-source.md"
    $baselineCommit = Invoke-RepoGit -Arguments @("rev-parse", "HEAD") | Select-Object -First 1
    Set-Utf8NoBomContent -Path $newSourcePath -Value "# New source`n"
    Set-Utf8NoBomContent -Path $newTranslationPath -Value @"
---
source: rules/new-source.md
source_commit: $baselineCommit
canonical: false
---

# 新規source

This untracked translation has body changes.
"@

    Invoke-MetadataCheck -Arguments @("-Update")
    $newBlob = Invoke-RepoGit -Arguments @("hash-object", "--", "rules/new-source.md") | Select-Object -First 1
    $newTranslation = Get-Content -LiteralPath $newTranslationPath -Raw
    if ($newTranslation -notmatch "(?m)^source_blob:\s*$newBlob\s*$") {
        throw "untracked translation body was not accepted for source_blob migration"
    }

    Invoke-RepoGit -Arguments @("add", "rules/new-source.md", "docs/ja/new-source.md") | Out-Null
    Invoke-RepoGit -Arguments @("commit", "--quiet", "-m", "add source and translation together") | Out-Null
    Invoke-MetadataCheck

    Write-Host "Japanese source metadata regression tests passed."
}
finally {
    $repoFullPath = [System.IO.Path]::GetFullPath($RepoRoot)
    $tempPrefix = $TempBase + [System.IO.Path]::DirectorySeparatorChar
    if (-not $repoFullPath.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove test directory outside the temp root: $repoFullPath"
    }
    if (Test-Path -LiteralPath $repoFullPath) {
        Remove-Item -LiteralPath $repoFullPath -Recurse -Force
    }
}
