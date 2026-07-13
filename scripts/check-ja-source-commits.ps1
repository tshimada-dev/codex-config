[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$Update,

    [switch]$AllowMetadataOnlyUpdate
)

$ErrorActionPreference = "Stop"

if ($AllowMetadataOnlyUpdate -and -not $Update) {
    throw "-AllowMetadataOnlyUpdate can only be used with -Update."
}

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $output = & git -C $RepoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed"
    }

    return $output
}

function Get-FrontMatter {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    if (-not $Content.StartsWith("---`n") -and -not $Content.StartsWith("---`r`n")) {
        return $null
    }

    $normalized = $Content -replace "`r`n", "`n"
    $end = $normalized.IndexOf("`n---`n", 4)
    if ($end -lt 0) {
        return $null
    }

    return $normalized.Substring(4, $end - 4)
}

function ConvertTo-Metadata {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FrontMatter
    )

    $metadata = @{}
    foreach ($line in ($FrontMatter -split "`n")) {
        if ($line -match "^\s*([^:#]+):\s*(.*?)\s*$") {
            $metadata[$Matches[1]] = $Matches[2]
        }
    }

    return $metadata
}

function Test-GitCommit {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Commit
    )

    & git -C $RepoRoot cat-file -e "$Commit^{commit}" 2>$null
    return $LASTEXITCODE -eq 0
}

function Test-GitPathAtCommit {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Commit,

        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $gitPath = $Path -replace "\\", "/"
    & git -C $RepoRoot cat-file -e "${Commit}:$gitPath" 2>$null
    return $LASTEXITCODE -eq 0
}

function Test-HasNonSourceRevisionDiff {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $diffs = @(
        Invoke-Git -Arguments @("diff", "--unified=0", "--", $Path)
        Invoke-Git -Arguments @("diff", "--cached", "--unified=0", "--", $Path)
    )

    foreach ($line in $diffs) {
        if ($line -match "^[+-]" -and
            $line -notmatch "^\+\+\+ " -and
            $line -notmatch "^--- " -and
            $line -notmatch "^[+-]source_(commit|blob):\s*") {
            return $true
        }
    }

    return $false
}

$docsRoot = Join-Path $RepoRoot "docs\ja"
$docs = Get-ChildItem -LiteralPath $docsRoot -Filter "*.md" -Recurse
$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$checked = 0
$updated = 0

foreach ($doc in $docs) {
    $content = Get-Content -LiteralPath $doc.FullName -Raw
    $frontMatter = Get-FrontMatter -Content $content
    if (-not $frontMatter) {
        continue
    }

    $metadata = ConvertTo-Metadata -FrontMatter $frontMatter
    if (-not $metadata.ContainsKey("source")) {
        continue
    }

    $checked++
    $relativeDoc = [System.IO.Path]::GetRelativePath($RepoRoot, $doc.FullName)
    $sourcePath = $metadata["source"]
    $sourceFullPath = Join-Path $RepoRoot $sourcePath

    if (-not (Test-Path -LiteralPath $sourceFullPath)) {
        $errors.Add("${relativeDoc}: source does not exist: $sourcePath")
        continue
    }

    if (-not $metadata.ContainsKey("canonical") -or $metadata["canonical"] -ne "false") {
        $errors.Add("${relativeDoc}: expected canonical: false")
    }

    $dirtySource = [bool](Invoke-Git -Arguments @("status", "--porcelain", "--", $sourcePath))
    $dirtyTranslation = [bool](Invoke-Git -Arguments @("status", "--porcelain", "--", $relativeDoc))
    $translationHasContentChanges = Test-HasNonSourceRevisionDiff -Path $relativeDoc

    if ($metadata.ContainsKey("source_blob")) {
        if ($metadata.ContainsKey("source_commit")) {
            $errors.Add("${relativeDoc}: use either source_blob or source_commit, not both")
            continue
        }

        $sourceBlob = $metadata["source_blob"]
        $currentBlob = (Invoke-Git -Arguments @("hash-object", "--", $sourcePath) | Select-Object -First 1)
        if ($Update -and $sourceBlob -ne $currentBlob) {
            if (-not $translationHasContentChanges -and -not $AllowMetadataOnlyUpdate) {
                $errors.Add("${relativeDoc}: refusing to update source_blob without Japanese content changes. Update the Japanese reference text first, or re-run with -AllowMetadataOnlyUpdate when a metadata-only refresh is intentional.")
                continue
            }

            $newContent = $content -replace "(?m)^source_blob:\s*.+$", "source_blob: $currentBlob"
            if ($PSCmdlet.ShouldProcess($relativeDoc, "Update source_blob to $currentBlob")) {
                Set-Content -LiteralPath $doc.FullName -Value $newContent -NoNewline
                $updated++
                $sourceBlob = $currentBlob
                $dirtyTranslation = $true
            }
        }

        if ($sourceBlob -notmatch "^[0-9a-f]{40,64}$") {
            $errors.Add("${relativeDoc}: source_blob is not a valid Git object id: $sourceBlob")
        }
        elseif ($sourceBlob -ne $currentBlob) {
            $errors.Add("${relativeDoc}: stale source_blob $sourceBlob; current source blob is $currentBlob")
        }

        if ($dirtySource) {
            $warnings.Add("${relativeDoc}: source has uncommitted changes; source_blob validates the current content")
        }
        if ($dirtyTranslation) {
            $warnings.Add("${relativeDoc}: translation file has uncommitted changes")
        }
        continue
    }

    if (-not $metadata.ContainsKey("source_commit")) {
        $errors.Add("${relativeDoc}: missing source_commit or source_blob")
        continue
    }

    $sourceCommit = $metadata["source_commit"]
    $latestCommit = (Invoke-Git -Arguments @("log", "-1", "--format=%H", "--", $sourcePath) | Select-Object -First 1)
    if (-not $latestCommit) {
        $errors.Add("${relativeDoc}: no git history for source; use source_blob for a new source: $sourcePath")
        continue
    }

    if ($Update -and $dirtySource) {
        if (-not $translationHasContentChanges -and -not $AllowMetadataOnlyUpdate) {
            $errors.Add("${relativeDoc}: refusing to replace source_commit with source_blob without Japanese content changes. Update the Japanese reference text first, or re-run with -AllowMetadataOnlyUpdate when a metadata-only refresh is intentional.")
            continue
        }

        $currentBlob = (Invoke-Git -Arguments @("hash-object", "--", $sourcePath) | Select-Object -First 1)
        $newContent = $content -replace "(?m)^source_commit:\s*.+$", "source_blob: $currentBlob"
        if ($PSCmdlet.ShouldProcess($relativeDoc, "Replace source_commit with source_blob $currentBlob")) {
            Set-Content -LiteralPath $doc.FullName -Value $newContent -NoNewline
            $updated++
            $dirtyTranslation = $true
        }
        $warnings.Add("${relativeDoc}: source has uncommitted changes; source_blob validates the current content")
        if ($dirtyTranslation) {
            $warnings.Add("${relativeDoc}: translation file has uncommitted changes")
        }
        continue
    }

    if ($Update -and $sourceCommit -ne $latestCommit) {
        if (-not $translationHasContentChanges -and -not $AllowMetadataOnlyUpdate) {
            $errors.Add("${relativeDoc}: refusing to update source_commit without Japanese content changes. Update the Japanese reference text first, or re-run with -AllowMetadataOnlyUpdate when a metadata-only refresh is intentional.")
            continue
        }

        $newContent = $content -replace "(?m)^source_commit:\s*.+$", "source_commit: $latestCommit"
        if ($PSCmdlet.ShouldProcess($relativeDoc, "Update source_commit to $latestCommit")) {
            Set-Content -LiteralPath $doc.FullName -Value $newContent -NoNewline
            $updated++
            $sourceCommit = $latestCommit
            $dirtyTranslation = $true
        }
    }

    if (-not (Test-GitCommit -Commit $sourceCommit)) {
        $errors.Add("${relativeDoc}: source_commit is not a valid commit: $sourceCommit")
        continue
    }

    if (-not (Test-GitPathAtCommit -Commit $sourceCommit -Path $sourcePath)) {
        $errors.Add("${relativeDoc}: source did not exist at source_commit: $sourcePath")
        continue
    }

    if ($sourceCommit -ne $latestCommit) {
        $errors.Add("${relativeDoc}: stale source_commit $sourceCommit; latest committed source is $latestCommit")
    }

    if ($dirtySource) {
        $warnings.Add("${relativeDoc}: source has uncommitted changes; refresh source_commit after committing $sourcePath")
    }

    if ($dirtyTranslation) {
        $warnings.Add("${relativeDoc}: translation file has uncommitted changes")
    }
}

foreach ($warning in $warnings) {
    Write-Warning $warning
}

if ($errors.Count -gt 0) {
    foreach ($errorMessage in $errors) {
        Write-Error $errorMessage -ErrorAction Continue
    }
    exit 1
}

Write-Host "Checked $checked Japanese reference files."
if ($Update) {
    Write-Host "Updated $updated source revision value(s)."
}
