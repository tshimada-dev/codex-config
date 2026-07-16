[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CodexHome,

    [switch]$Overwrite,

    [switch]$Backup,

    [switch]$Prune,

    [switch]$InstallConfig,

    [switch]$OverwriteConfig
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

if ($OverwriteConfig -and -not $InstallConfig) {
    throw "-OverwriteConfig can only be used with -InstallConfig."
}

if ($Backup -and -not ($Overwrite -or $Prune -or $InstallConfig)) {
    throw "-Backup can only be used with -Overwrite, -Prune, or -InstallConfig."
}

$script:CopiedFileCount = 0
$script:OverwrittenFileCount = 0
$script:UnchangedFileCount = 0
$script:BackedUpFileCount = 0
$script:PrunedFileCount = 0
$script:ConfigAddedKeyCount = 0
$script:ConfigUpdatedKeyCount = 0
$script:ConfigUnchangedKeyCount = 0
$script:ConfigProfileCopiedCount = 0
$script:ConfigProfileOverwrittenCount = 0
$script:ConfigProfileUnchangedCount = 0

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

    return $files |
        Where-Object {
            $_ -and (Test-Path -LiteralPath (Join-Path $RepoRoot ($_ -replace "/", [System.IO.Path]::DirectorySeparatorChar)) -PathType Leaf)
        } |
        Sort-Object
}

function Get-ConfigProfileRelativeFiles {
    $files = Invoke-Git -Arguments @(
        "ls-files",
        "--",
        "config/profiles/*.config.toml"
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

function Test-ConfigTemplateIsShareable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $sensitivePattern = "(?i)(api[_-]?key|token|password|secret|credential|private[_-]?key)"
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        if ($trimmed -match $sensitivePattern) {
            throw "Refusing to install config template with sensitive-looking key or value: $Path"
        }
    }
}

function Get-ManagedConfigEntries {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    Test-ConfigTemplateIsShareable -Path $Path

    $entries = @()
    $seen = @{}
    $table = ""
    $blockedTablePattern = "^(projects|mcp_servers|marketplaces|plugins|otel)(\.|$)"

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        if ($trimmed -match "^\[([^\]]+)\]$") {
            $table = $Matches[1]
            if ($table -match $blockedTablePattern) {
                throw "Refusing to install non-shareable config table [$table] from $Path"
            }

            continue
        }

        if ($trimmed -match "^([A-Za-z0-9_.-]+)\s*=") {
            $key = $Matches[1]
            $entryId = "$table`n$key"
            if ($seen.ContainsKey($entryId)) {
                throw "Duplicate managed config key in ${Path}: $key"
            }
            $seen[$entryId] = $true

            $entries += [pscustomobject]@{
                Table = $table
                Key = $key
                Line = $line
            }
        }
    }

    return @($entries)
}

function Get-ConfigLineInfo {
    param(
        [System.Collections.Generic.List[string]]$Lines
    )

    $keyIndexes = @{}
    $tableIndexes = @{}
    $table = ""

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $trimmed = $Lines[$i].Trim()
        if ($trimmed -match "^\[([^\]]+)\]$") {
            $table = $Matches[1]
            if (-not $tableIndexes.ContainsKey($table)) {
                $tableIndexes[$table] = $i
            }
            continue
        }

        if ($trimmed -match "^([A-Za-z0-9_.-]+)\s*=") {
            $key = $Matches[1]
            $entryId = "$table`n$key"
            if (-not $keyIndexes.ContainsKey($entryId)) {
                $keyIndexes[$entryId] = $i
            }
        }
    }

    return [pscustomobject]@{
        KeyIndexes = $keyIndexes
        TableIndexes = $tableIndexes
    }
}

function Get-FirstTableIndex {
    param(
        [System.Collections.Generic.List[string]]$Lines
    )

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i].Trim() -match "^\[[^\]]+\]$") {
            return $i
        }
    }

    return $Lines.Count
}

function Get-TableEndIndex {
    param(
        [System.Collections.Generic.List[string]]$Lines,

        [Parameter(Mandatory = $true)]
        [int]$TableStartIndex
    )

    for ($i = $TableStartIndex + 1; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i].Trim() -match "^\[[^\]]+\]$") {
            return $i
        }
    }

    return $Lines.Count
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

    $current = New-Object "System.Collections.Generic.HashSet[string]" ([StringComparer]::Ordinal)
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

function Merge-BaseConfig {
    param(
        [string]$BackupRoot
    )

    if (-not $InstallConfig) {
        return
    }

    $baseConfigPath = Join-ManagedPath -Root $RepoRoot -RelativePath "config/config.base.toml"
    if (-not (Test-Path -LiteralPath $baseConfigPath -PathType Leaf)) {
        throw "Missing base config template: $baseConfigPath"
    }

    $entries = @(Get-ManagedConfigEntries -Path $baseConfigPath)
    if ($entries.Count -eq 0) {
        throw "Base config template has no managed keys: $baseConfigPath"
    }

    $configPath = Join-Path $CodexHome "config.toml"
    $lines = [System.Collections.Generic.List[string]]::new()
    $configExists = Test-Path -LiteralPath $configPath -PathType Leaf
    if ($configExists) {
        foreach ($line in Get-Content -LiteralPath $configPath) {
            $lines.Add($line)
        }
    }

    $changed = $false
    $info = Get-ConfigLineInfo -Lines $lines
    foreach ($entry in $entries) {
        $entryId = "$($entry.Table)`n$($entry.Key)"
        if (-not $info.KeyIndexes.ContainsKey($entryId)) {
            continue
        }

        $index = [int]$info.KeyIndexes[$entryId]
        if ($lines[$index].Trim() -eq $entry.Line.Trim()) {
            $script:ConfigUnchangedKeyCount++
            continue
        }

        if (-not $OverwriteConfig) {
            $displayKey = if ($entry.Table) { "[$($entry.Table)].$($entry.Key)" } else { $entry.Key }
            throw "Refusing to overwrite existing config key with different value: $displayKey. Re-run with -InstallConfig -OverwriteConfig to replace shared config keys."
        }

        $lines[$index] = $entry.Line
        $script:ConfigUpdatedKeyCount++
        $changed = $true
    }

    $missingEntries = @($entries | Where-Object {
        $entryId = "$($_.Table)`n$($_.Key)"
        -not $info.KeyIndexes.ContainsKey($entryId)
    })

    $rootEntries = @($missingEntries | Where-Object { -not $_.Table })
    if ($rootEntries.Count -gt 0) {
        $insertIndex = Get-FirstTableIndex -Lines $lines
        foreach ($entry in $rootEntries) {
            $lines.Insert($insertIndex, $entry.Line)
            $insertIndex++
            $script:ConfigAddedKeyCount++
            $changed = $true
        }

        if ($insertIndex -lt $lines.Count -and $lines[$insertIndex].Trim()) {
            $lines.Insert($insertIndex, "")
        }
    }

    $tables = @($missingEntries | Where-Object { $_.Table } | Select-Object -ExpandProperty Table -Unique)
    foreach ($table in $tables) {
        $tableEntries = @($missingEntries | Where-Object { $_.Table -eq $table })
        $info = Get-ConfigLineInfo -Lines $lines

        if ($info.TableIndexes.ContainsKey($table)) {
            $insertIndex = Get-TableEndIndex -Lines $lines -TableStartIndex ([int]$info.TableIndexes[$table])
            foreach ($entry in $tableEntries) {
                $lines.Insert($insertIndex, $entry.Line)
                $insertIndex++
                $script:ConfigAddedKeyCount++
                $changed = $true
            }
            continue
        }

        if ($lines.Count -gt 0 -and $lines[$lines.Count - 1].Trim()) {
            $lines.Add("")
        }
        $lines.Add("[$table]")
        foreach ($entry in $tableEntries) {
            $lines.Add($entry.Line)
            $script:ConfigAddedKeyCount++
            $changed = $true
        }
    }

    if (-not $changed) {
        return
    }

    if ($configExists) {
        Backup-ManagedFile -Source $configPath -RelativePath "config.toml" -BackupRoot $BackupRoot
    }

    $configParent = Split-Path -Parent $configPath
    if ($configParent -and -not (Test-Path -LiteralPath $configParent)) {
        if ($PSCmdlet.ShouldProcess($configParent, "Create config directory")) {
            New-Item -ItemType Directory -Path $configParent -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($configPath, "Merge shared config keys from config/config.base.toml")) {
        Set-Content -LiteralPath $configPath -Value $lines.ToArray() -Encoding utf8
    }
}

function Copy-ConfigProfileFiles {
    param(
        [string]$BackupRoot
    )

    if (-not $InstallConfig) {
        return
    }

    foreach ($relativePath in Get-ConfigProfileRelativeFiles) {
        $source = Join-ManagedPath -Root $RepoRoot -RelativePath $relativePath
        $profileName = Split-Path -Leaf $source
        $destination = Join-Path $CodexHome $profileName
        $destinationExists = Test-Path -LiteralPath $destination

        Test-ConfigTemplateIsShareable -Path $source

        if ($destinationExists) {
            if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
                throw "Destination profile exists and is not a file: $destination"
            }

            if (Test-SameFileContent -Left $source -Right $destination) {
                $script:ConfigProfileUnchangedCount++
                Write-Host "Unchanged profile: $profileName"
                continue
            }

            if (-not $OverwriteConfig) {
                throw "Refusing to overwrite existing config profile with different content: $destination. Re-run with -InstallConfig -OverwriteConfig to replace shared config profiles."
            }

            Backup-ManagedFile -Source $destination -RelativePath $profileName -BackupRoot $BackupRoot
        }

        if ($PSCmdlet.ShouldProcess($destination, "Install config profile from $source")) {
            Copy-Item -LiteralPath $source -Destination $destination -Force
            if ($destinationExists) {
                $script:ConfigProfileOverwrittenCount++
            }
            else {
                $script:ConfigProfileCopiedCount++
            }
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

Merge-BaseConfig -BackupRoot $backupRoot
Copy-ConfigProfileFiles -BackupRoot $backupRoot

Write-ManagedManifest -RelativePaths $managedRelativeFiles

if ($WhatIfPreference) {
    Write-Host "WhatIf completed for Codex config install to $CodexHome"
}
elseif ($Overwrite -or $OverwriteConfig) {
    $enabledOverwriteModes = @()
    if ($Overwrite) {
        $enabledOverwriteModes += "managed file overwrite"
    }
    if ($OverwriteConfig) {
        $enabledOverwriteModes += "config overwrite"
    }
    Write-Host "Installed Codex config to $CodexHome with $($enabledOverwriteModes -join ', ') enabled"
    Write-Host "Copied: $CopiedFileCount; overwritten: $OverwrittenFileCount; unchanged: $UnchangedFileCount; pruned: $PrunedFileCount"
    if ($InstallConfig) {
        Write-Host "Config keys added: $ConfigAddedKeyCount; updated: $ConfigUpdatedKeyCount; unchanged: $ConfigUnchangedKeyCount"
        Write-Host "Config profiles copied: $ConfigProfileCopiedCount; overwritten: $ConfigProfileOverwrittenCount; unchanged: $ConfigProfileUnchangedCount"
    }
    if ($Backup -and $BackedUpFileCount -gt 0) {
        Write-Host "Backed up $BackedUpFileCount file(s) to $backupRoot"
    }
}
else {
    Write-Host "Installed Codex config to $CodexHome without overwriting existing files"
    Write-Host "Copied: $CopiedFileCount; unchanged: $UnchangedFileCount; pruned: $PrunedFileCount"
    if ($InstallConfig) {
        Write-Host "Config keys added: $ConfigAddedKeyCount; updated: $ConfigUpdatedKeyCount; unchanged: $ConfigUnchangedKeyCount"
        Write-Host "Config profiles copied: $ConfigProfileCopiedCount; overwritten: $ConfigProfileOverwrittenCount; unchanged: $ConfigProfileUnchangedCount"
    }
}
