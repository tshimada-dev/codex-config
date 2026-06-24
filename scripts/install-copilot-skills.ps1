[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CopilotSkillsHome,

    [string[]]$SkillName,

    [switch]$Overwrite,

    [switch]$Backup,

    [switch]$Prune,

    [switch]$AllSkills,

    [switch]$IncludeCodexAgentMetadata
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

if (-not $CopilotSkillsHome) {
    $CopilotSkillsHome = Join-Path $HOME ".copilot\skills"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required because the installer copies only tracked skill files."
}

if ($Backup -and -not ($Overwrite -or $Prune)) {
    throw "-Backup can only be used with -Overwrite or -Prune."
}

if ($AllSkills -and $SkillName -and $SkillName.Count -gt 0) {
    throw "-AllSkills cannot be combined with -SkillName."
}

$ManifestRelativePath = ".codex-config-copilot-managed-files"
$ManifestVersion = 1

$DefaultCopilotSkillNames = @(
    "codex-task-intake",
    "codex-repo-scout",
    "codex-implementation-loop",
    "codex-debug-discipline",
    "codex-plan-slices",
    "codex-pr-readiness",
    "codex-ui-quality-gate"
)

$script:CopiedFileCount = 0
$script:OverwrittenFileCount = 0
$script:UnchangedFileCount = 0
$script:BackedUpFileCount = 0
$script:PrunedFileCount = 0
$script:PrunedDirectoryCount = 0

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

function ConvertTo-CopilotSkillName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceSkillName
    )

    if (-not $SourceSkillName.StartsWith("codex-", [StringComparison]::Ordinal)) {
        throw "Expected a codex-* skill name, got: $SourceSkillName"
    }

    return "copilot-$($SourceSkillName.Substring("codex-".Length))"
}

function ConvertTo-SourceSkillName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RequestedSkillName
    )

    $normalized = ($RequestedSkillName -replace "\\", "/").Trim("/")
    $leaf = Split-Path -Leaf $normalized

    if ($leaf.StartsWith("copilot-", [StringComparison]::Ordinal)) {
        return "codex-$($leaf.Substring("copilot-".Length))"
    }

    if ($leaf.StartsWith("codex-", [StringComparison]::Ordinal)) {
        return $leaf
    }

    return "codex-$leaf"
}

function Get-TrackedSkillFiles {
    $files = Invoke-Git -Arguments @(
        "ls-files",
        "--",
        "skills/codex-*"
    )

    $tracked = @($files | Where-Object { $_ })
    if (-not $IncludeCodexAgentMetadata) {
        $tracked = @($tracked | Where-Object { $_ -notmatch "/agents/" })
    }

    return @($tracked | Sort-Object)
}

function Get-SourceSkillNameFromRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    if ($RelativePath -notmatch "^skills/(codex-[^/]+)/") {
        throw "Unexpected skill path: $RelativePath"
    }

    return $Matches[1]
}

function Get-SelectedSkillNames {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$TrackedFiles
    )

    $available = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($file in $TrackedFiles) {
        [void]$available.Add((Get-SourceSkillNameFromRelativePath -RelativePath $file))
    }

    if ($AllSkills) {
        return @($available | Sort-Object)
    }

    if (-not $SkillName -or $SkillName.Count -eq 0) {
        $missingDefaults = @($DefaultCopilotSkillNames | Where-Object { -not $available.Contains($_) })
        if ($missingDefaults.Count -gt 0) {
            throw "Default Copilot skill set references missing source skills: $($missingDefaults -join ', ')"
        }

        return @($DefaultCopilotSkillNames | Sort-Object)
    }

    $selected = @()
    foreach ($requested in $SkillName) {
        $sourceName = ConvertTo-SourceSkillName -RequestedSkillName $requested
        if (-not $available.Contains($sourceName)) {
            throw "Unknown skill '$requested'. Available skills: $(@($available | Sort-Object) -join ', ')"
        }

        $selected += $sourceName
    }

    return @($selected | Sort-Object -Unique)
}

function ConvertTo-CopilotRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath
    )

    $sourceName = Get-SourceSkillNameFromRelativePath -RelativePath $SourceRelativePath
    $copilotName = ConvertTo-CopilotSkillName -SourceSkillName $sourceName
    $sourcePrefix = "skills/$sourceName/"
    $innerPath = $SourceRelativePath.Substring($sourcePrefix.Length)

    return "$copilotName/$innerPath"
}

function ConvertTo-CopilotSkillContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$SourceSkillName,

        [Parameter(Mandatory = $true)]
        [string]$CopilotSkillName,

        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath
    )

    if ($SourceRelativePath -notmatch "/SKILL\.md$" -and $SourceRelativePath -notmatch "/agents/") {
        return $Content
    }

    $escapedSourceName = [regex]::Escape($SourceSkillName)
    $converted = $Content -replace "(?m)^name:\s+$escapedSourceName\s*$", "name: $CopilotSkillName"
    $converted = $converted -replace "\b$escapedSourceName\b", $CopilotSkillName

    return $converted
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
    return Join-ManagedPath -Root $CopilotSkillsHome -RelativePath $ManifestRelativePath
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

    $manifest = $content | ConvertFrom-Json
    if ($manifest.managed_files) {
        return @($manifest.managed_files | Where-Object { $_ } | Sort-Object)
    }

    return @()
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
        tool = "codex-config install-copilot-skills.ps1"
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

function Copy-CopilotSkillFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath,

        [string]$BackupRoot
    )

    $sourceName = Get-SourceSkillNameFromRelativePath -RelativePath $SourceRelativePath
    $copilotName = ConvertTo-CopilotSkillName -SourceSkillName $sourceName
    $destinationRelativePath = ConvertTo-CopilotRelativePath -SourceRelativePath $SourceRelativePath
    $source = Join-ManagedPath -Root $RepoRoot -RelativePath $SourceRelativePath
    $destination = Join-ManagedPath -Root $CopilotSkillsHome -RelativePath $destinationRelativePath
    $destinationExists = Test-Path -LiteralPath $destination

    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing source file: $source"
    }

    $shouldTransform = $SourceRelativePath -match "/SKILL\.md$" -or $SourceRelativePath -match "/agents/"
    $copySource = $source
    $tempFile = $null
    try {
        if ($shouldTransform) {
            $sourceContent = Get-Content -LiteralPath $source -Raw
            $convertedContent = ConvertTo-CopilotSkillContent `
                -Content $sourceContent `
                -SourceSkillName $sourceName `
                -CopilotSkillName $copilotName `
                -SourceRelativePath $SourceRelativePath

            $tempFile = [System.IO.Path]::GetTempFileName()
            Set-Content -LiteralPath $tempFile -Value $convertedContent -Encoding utf8NoBOM
            $copySource = $tempFile
        }

        if ($destinationExists) {
            if (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
                throw "Destination exists and is not a file: $destination"
            }

            if (Test-SameFileContent -Left $copySource -Right $destination) {
                $script:UnchangedFileCount++
                Write-Host "Unchanged: $destinationRelativePath"
                return
            }

            if (-not $Overwrite) {
                throw "Refusing to overwrite existing file with different content: $destination. Re-run with -Overwrite to replace Copilot skill files."
            }

            Backup-ManagedFile -Source $destination -RelativePath $destinationRelativePath -BackupRoot $BackupRoot
        }

        $destinationParent = Split-Path -Parent $destination
        if ($destinationParent -and -not (Test-Path -LiteralPath $destinationParent)) {
            if ($PSCmdlet.ShouldProcess($destinationParent, "Create directory")) {
                New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
            }
        }

        $action = if ($destinationExists) { "Overwrite with transformed $SourceRelativePath" } else { "Copy transformed $SourceRelativePath" }
        if ($PSCmdlet.ShouldProcess($destination, $action)) {
            Copy-Item -LiteralPath $copySource -Destination $destination -Force
            if ($destinationExists) {
                $script:OverwrittenFileCount++
            }
            else {
                $script:CopiedFileCount++
            }
        }
    }
    finally {
        if ($tempFile) {
            Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue
        }
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

    $skillsHomeFullPath = [System.IO.Path]::GetFullPath($CopilotSkillsHome).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $skillsHomePrefix = $skillsHomeFullPath + [System.IO.Path]::DirectorySeparatorChar

    foreach ($relativePath in ($PreviousRelativePaths | Sort-Object -Unique)) {
        if ($current.Contains($relativePath)) {
            continue
        }

        $destination = Join-ManagedPath -Root $CopilotSkillsHome -RelativePath $relativePath
        $destinationFullPath = [System.IO.Path]::GetFullPath($destination)
        if ($destinationFullPath -ne $skillsHomeFullPath -and -not $destinationFullPath.StartsWith($skillsHomePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to prune path outside Copilot skills home: $destination"
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

function Remove-EmptyPrunedDirectories {
    param(
        [string[]]$PreviousRelativePaths,

        [string[]]$CurrentRelativePaths
    )

    if (-not $Prune) {
        return
    }

    $current = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($relativePath in $CurrentRelativePaths) {
        [void]$current.Add($relativePath)
    }

    $skillsHomeFullPath = [System.IO.Path]::GetFullPath($CopilotSkillsHome).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $skillsHomePrefix = $skillsHomeFullPath + [System.IO.Path]::DirectorySeparatorChar

    $candidateDirectories = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($relativePath in ($PreviousRelativePaths | Sort-Object -Unique)) {
        if ($current.Contains($relativePath)) {
            continue
        }

        $relativeDirectory = Split-Path -Parent ($relativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
        while ($relativeDirectory) {
            [void]$candidateDirectories.Add($relativeDirectory)
            $relativeDirectory = Split-Path -Parent $relativeDirectory
        }
    }

    foreach ($relativeDirectory in ($candidateDirectories | Sort-Object Length -Descending)) {
        $directory = Join-Path $CopilotSkillsHome $relativeDirectory
        $directoryFullPath = [System.IO.Path]::GetFullPath($directory)
        if ($directoryFullPath -eq $skillsHomeFullPath -or -not $directoryFullPath.StartsWith($skillsHomePrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to prune directory outside Copilot skills home: $directory"
        }

        if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
            continue
        }

        if (@(Get-ChildItem -LiteralPath $directory -Force).Count -gt 0) {
            continue
        }

        if ($PSCmdlet.ShouldProcess($directory, "Prune empty directory left by managed file removal")) {
            Remove-Item -LiteralPath $directory -Force
            $script:PrunedDirectoryCount++
            Write-Host "Pruned directory: $relativeDirectory"
        }
    }
}

$trackedFiles = @(Get-TrackedSkillFiles)
$selectedSkillNames = @(Get-SelectedSkillNames -TrackedFiles $trackedFiles)
$selected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($name in $selectedSkillNames) {
    [void]$selected.Add($name)
}

$selectedFiles = @($trackedFiles | Where-Object {
    $selected.Contains((Get-SourceSkillNameFromRelativePath -RelativePath $_))
})
$managedRelativeFiles = @($selectedFiles | ForEach-Object { ConvertTo-CopilotRelativePath -SourceRelativePath $_ })
$previousManagedRelativeFiles = @(Read-ManagedManifest)

if (-not (Test-Path -LiteralPath $CopilotSkillsHome)) {
    if ($PSCmdlet.ShouldProcess($CopilotSkillsHome, "Create Copilot skills directory")) {
        New-Item -ItemType Directory -Path $CopilotSkillsHome -Force | Out-Null
    }
}

$backupRoot = $null
if ($Backup) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = "${CopilotSkillsHome}.backup-$timestamp"
}

Remove-PrunedManagedFiles -PreviousRelativePaths $previousManagedRelativeFiles -CurrentRelativePaths $managedRelativeFiles -BackupRoot $backupRoot
Remove-EmptyPrunedDirectories -PreviousRelativePaths $previousManagedRelativeFiles -CurrentRelativePaths $managedRelativeFiles

foreach ($relativePath in $selectedFiles) {
    Copy-CopilotSkillFile -SourceRelativePath $relativePath -BackupRoot $backupRoot
}

Write-ManagedManifest -RelativePaths $managedRelativeFiles

$installedSkillNames = @($selectedSkillNames | ForEach-Object { ConvertTo-CopilotSkillName -SourceSkillName $_ })
if ($WhatIfPreference) {
    Write-Host "WhatIf completed for Copilot skill install to $CopilotSkillsHome"
}
elseif ($Overwrite) {
    Write-Host "Installed Copilot skills to $CopilotSkillsHome with overwrite enabled"
}
else {
    Write-Host "Installed Copilot skills to $CopilotSkillsHome without overwriting existing files"
}

Write-Host "Skills: $($installedSkillNames -join ', ')"
Write-Host "Copied: $CopiedFileCount; overwritten: $OverwrittenFileCount; unchanged: $UnchangedFileCount; pruned files: $PrunedFileCount; pruned directories: $PrunedDirectoryCount"
if ($Backup -and $BackedUpFileCount -gt 0) {
    Write-Host "Backed up $BackedUpFileCount file(s) to $backupRoot"
}
