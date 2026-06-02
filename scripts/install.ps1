[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CodexHome,

    [switch]$Overwrite,

    [switch]$Backup,

    [switch]$Prune
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

if (-not $CodexHome) {
    if ($env:CODEX_HOME) {
        $CodexHome = $env:CODEX_HOME
    }
    else {
        $CodexHome = Join-Path $HOME ".codex"
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required because the installer copies only tracked managed files."
}

if ($Backup -and -not ($Overwrite -or $Prune)) {
    throw "-Backup can only be used with -Overwrite or -Prune."
}

$script:CopiedFileCount = 0
$script:OverwrittenFileCount = 0
$script:UnchangedFileCount = 0
$script:BackedUpFileCount = 0
$script:PrunedFileCount = 0

$ManifestRelativePath = ".codex-config-managed-files"
$ManifestVersion = 1

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

function Get-SourceRepository {
    $remote = & git -C $RepoRoot remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0 -and $remote) {
        return ($remote | Select-Object -First 1)
    }

    return $null
}

function Get-SourceCommit {
    return (Invoke-Git -Arguments @("rev-parse", "HEAD") | Select-Object -First 1)
}

function Get-ManifestPath {
    return Join-ManagedPath -Root $CodexHome -RelativePath $ManifestRelativePath
}

function Read-ManagedManifest {
    $manifestPath = Get-ManifestPath
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        return @()
    }

    $content = Get-Content -LiteralPath $manifestPath -Raw
    if (-not $content) {
        return @()
    }

    if ($content.TrimStart().StartsWith("{")) {
        $manifest = $content | ConvertFrom-Json
        if ($manifest.managed_files) {
            return @($manifest.managed_files | Where-Object { $_ } | Sort-Object)
        }

        return @()
    }

    return @($content -split "\r?\n" | Where-Object { $_ } | Sort-Object)
}

function Write-ManagedManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$RelativePaths
    )

    $manifestPath = Get-ManifestPath
    $manifestParent = Split-Path -Parent $manifestPath
    if ($manifestParent -and -not (Test-Path -LiteralPath $manifestParent)) {
        if ($PSCmdlet.ShouldProcess($manifestParent, "Create manifest directory")) {
            New-Item -ItemType Directory -Path $manifestParent -Force | Out-Null
        }
    }

    $manifest = [ordered]@{
        schema_version = $ManifestVersion
        tool = "codex-config install.ps1"
        source_repo = Get-SourceRepository
        source_commit = Get-SourceCommit
        installed_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        managed_files = @($RelativePaths | Sort-Object)
    }
    $json = $manifest | ConvertTo-Json -Depth 4

    if ($PSCmdlet.ShouldProcess($manifestPath, "Write managed file manifest")) {
        Set-Content -LiteralPath $manifestPath -Value $json -Encoding utf8
    }
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

function Backup-ManagedFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [string]$BackupRoot
    )

    if (-not $Backup) {
        return
    }

    $backupDestination = Join-ManagedPath -Root $BackupRoot -RelativePath $RelativePath
    $backupParent = Split-Path -Parent $backupDestination
    if ($backupParent -and -not (Test-Path -LiteralPath $backupParent)) {
        if ($PSCmdlet.ShouldProcess($backupParent, "Create backup directory")) {
            New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($backupDestination, "Back up existing $RelativePath")) {
        Copy-Item -LiteralPath $Source -Destination $backupDestination -Force
        $script:BackedUpFileCount++
    }
}

function Remove-PrunedManagedFiles {
    param(
        [string[]]$PreviousRelativePaths,

        [string[]]$CurrentRelativePaths,

        [string]$BackupRoot
    )

    if (-not $Prune) {
        return
    }

    $current = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($relativePath in $CurrentRelativePaths) {
        [void]$current.Add($relativePath)
    }

    $codexHomeFullPath = [System.IO.Path]::GetFullPath($CodexHome).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $codexHomePrefix = $codexHomeFullPath + [System.IO.Path]::DirectorySeparatorChar
    foreach ($relativePath in ($PreviousRelativePaths | Sort-Object -Unique)) {
        if ($current.Contains($relativePath)) {
            continue
        }

        $destination = Join-ManagedPath -Root $CodexHome -RelativePath $relativePath
        $destinationFullPath = [System.IO.Path]::GetFullPath($destination)
        if ($destinationFullPath -ne $codexHomeFullPath -and -not $destinationFullPath.StartsWith($codexHomePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to prune path outside Codex home: $destination"
        }

        if (-not (Test-Path -LiteralPath $destination)) {
            continue
        }

        if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
            throw "Refusing to prune managed path that is not a file: $destination"
        }

        Backup-ManagedFile -Source $destination -RelativePath $relativePath -BackupRoot $BackupRoot

        if ($PSCmdlet.ShouldProcess($destination, "Prune previously managed file no longer tracked")) {
            Remove-Item -LiteralPath $destination -Force
            $script:PrunedFileCount++
            Write-Host "Pruned: $relativePath"
        }
    }
}

$managedRelativeFiles = @(Get-ManagedRelativeFiles)
$previousManagedRelativeFiles = @(Read-ManagedManifest)

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

Remove-PrunedManagedFiles -PreviousRelativePaths $previousManagedRelativeFiles -CurrentRelativePaths $managedRelativeFiles -BackupRoot $backupRoot

foreach ($relativePath in $managedRelativeFiles) {
    Copy-ManagedFile -RelativePath $relativePath -BackupRoot $backupRoot
}

Write-ManagedManifest -RelativePaths $managedRelativeFiles

if ($WhatIfPreference) {
    Write-Host "WhatIf completed for Codex config install to $CodexHome"
}
elseif ($Overwrite) {
    Write-Host "Installed Codex config to $CodexHome with overwrite enabled"
    Write-Host "Copied: $CopiedFileCount; overwritten: $OverwrittenFileCount; unchanged: $UnchangedFileCount; pruned: $PrunedFileCount"
    if ($Backup -and $BackedUpFileCount -gt 0) {
        Write-Host "Backed up $BackedUpFileCount file(s) to $backupRoot"
    }
}
else {
    Write-Host "Installed Codex config to $CodexHome without overwriting existing files"
    Write-Host "Copied: $CopiedFileCount; unchanged: $UnchangedFileCount; pruned: $PrunedFileCount"
}
