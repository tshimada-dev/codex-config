[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CodexHome = (Join-Path $HOME ".codex"),

    [switch]$Overwrite,

    [switch]$Backup
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required because the installer copies only tracked managed files."
}

if ($Backup -and -not $Overwrite) {
    throw "-Backup can only be used with -Overwrite."
}

$script:CopiedFileCount = 0
$script:OverwrittenFileCount = 0
$script:UnchangedFileCount = 0
$script:BackedUpFileCount = 0

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

function Join-ManagedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,

        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    return Join-Path $Root ($RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
}

function Get-ManagedRelativeFiles {
    $files = Invoke-Git -Arguments @(
        "ls-files",
        "--",
        "AGENTS.md",
        "rules",
        "templates",
        "skills/codex-*"
    )

    return $files | Where-Object { $_ } | Sort-Object
}

function Test-SameFileContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Left,

        [Parameter(Mandatory = $true)]
        [string]$Right
    )

    return (Get-FileHash -LiteralPath $Left).Hash -eq (Get-FileHash -LiteralPath $Right).Hash
}

function Copy-ManagedFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [string]$BackupRoot
    )

    $source = Join-ManagedPath -Root $RepoRoot -RelativePath $RelativePath
    $destination = Join-ManagedPath -Root $CodexHome -RelativePath $RelativePath
    $destinationExists = Test-Path -LiteralPath $destination

    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing source file: $source"
    }

    if ($destinationExists) {
        if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
            throw "Destination exists and is not a file: $destination"
        }

        if (Test-SameFileContent -Left $source -Right $destination) {
            $script:UnchangedFileCount++
            Write-Host "Unchanged: $RelativePath"
            return
        }

        if (-not $Overwrite) {
            throw "Refusing to overwrite existing file with different content: $destination. Re-run with -Overwrite to replace managed files."
        }

        if ($Backup) {
            $backupDestination = Join-ManagedPath -Root $BackupRoot -RelativePath $RelativePath
            $backupParent = Split-Path -Parent $backupDestination
            if ($backupParent -and -not (Test-Path -LiteralPath $backupParent)) {
                if ($PSCmdlet.ShouldProcess($backupParent, "Create backup directory")) {
                    New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
                }
            }

            if ($PSCmdlet.ShouldProcess($backupDestination, "Back up existing $RelativePath")) {
                Copy-Item -LiteralPath $destination -Destination $backupDestination -Force
                $script:BackedUpFileCount++
            }
        }
    }

    $destinationParent = Split-Path -Parent $destination
    if ($destinationParent -and -not (Test-Path -LiteralPath $destinationParent)) {
        if ($PSCmdlet.ShouldProcess($destinationParent, "Create directory")) {
            New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        }
    }

    $action = if ($destinationExists) { "Overwrite with $source" } else { "Copy from $source" }
    if ($PSCmdlet.ShouldProcess($destination, $action)) {
        Copy-Item -LiteralPath $source -Destination $destination -Force
        if ($destinationExists) {
            $script:OverwrittenFileCount++
        }
        else {
            $script:CopiedFileCount++
        }
    }
}

if (-not (Test-Path -LiteralPath $CodexHome)) {
    if ($PSCmdlet.ShouldProcess($CodexHome, "Create Codex home")) {
        New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
    }
}

$backupRoot = $null
if ($Backup) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = "${CodexHome}.backup-$timestamp"
}

foreach ($relativePath in Get-ManagedRelativeFiles) {
    Copy-ManagedFile -RelativePath $relativePath -BackupRoot $backupRoot
}

if ($WhatIfPreference) {
    Write-Host "WhatIf completed for Codex config install to $CodexHome"
}
elseif ($Overwrite) {
    Write-Host "Installed Codex config to $CodexHome with overwrite enabled"
    Write-Host "Copied: $CopiedFileCount; overwritten: $OverwrittenFileCount; unchanged: $UnchangedFileCount"
    if ($Backup -and $BackedUpFileCount -gt 0) {
        Write-Host "Backed up $BackedUpFileCount file(s) to $backupRoot"
    }
}
else {
    Write-Host "Installed Codex config to $CodexHome without overwriting existing files"
    Write-Host "Copied: $CopiedFileCount; unchanged: $UnchangedFileCount"
}
