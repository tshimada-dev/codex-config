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
$DefinitionRelativePath = "config/development-skills.json"
$DefinitionPath = Join-Path $RepoRoot $DefinitionRelativePath
$ManifestRelativePath = ".codex-config-copilot-managed-files"
$ManifestVersion = 1
$DevelopmentWorkflowSourceRelativePath = "rules/development-workflow.md"
$DevelopmentWorkflowSkillReference = "../../rules/development-workflow.md"
$CopilotDevelopmentWorkflowSkillReference = "references/development-workflow.md"
$GeneratedTextExtensions = @(".md", ".ps1", ".py", ".json", ".yaml", ".yml", ".toml", ".txt")

if (-not $CopilotSkillsHome) {
    $CopilotSkillsHome = Join-Path $HOME ".copilot\skills"
}

$copilotSkillsHomeFullPath = [System.IO.Path]::GetFullPath($CopilotSkillsHome)
$fileSystemRoot = [System.IO.Path]::GetPathRoot($copilotSkillsHomeFullPath)
$trimmedHome = $copilotSkillsHomeFullPath.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
$trimmedFileSystemRoot = $fileSystemRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
if ($trimmedHome -eq $trimmedFileSystemRoot) {
    throw "CopilotSkillsHome cannot be a filesystem root: $copilotSkillsHomeFullPath"
}
$CopilotSkillsHome = $trimmedHome

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is required because the installer copies only tracked skill files."
}

if ($Backup -and -not ($Overwrite -or $Prune)) {
    throw "-Backup can only be used with -Overwrite or -Prune."
}

if ($AllSkills -and $SkillName -and $SkillName.Count -gt 0) {
    throw "-AllSkills cannot be combined with -SkillName."
}

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

function Set-Utf8NoBomContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath,

        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($LiteralPath, $Value, $encoding)
}

function Test-SequenceEqual {
    param(
        [object[]]$Left,
        [object[]]$Right
    )

    if (@($Left).Count -ne @($Right).Count) {
        return $false
    }

    for ($index = 0; $index -lt @($Left).Count; $index++) {
        if ([string]$Left[$index] -cne [string]$Right[$index]) {
            return $false
        }
    }

    return $true
}

function Assert-NoReparsePointInContainedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,

        [Parameter(Mandatory = $true)]
        [string]$Candidate,

        [Parameter(Mandatory = $true)]
        [string]$Purpose
    )

    $rootFullPath = [System.IO.Path]::GetFullPath($Root).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $relativePath = [System.IO.Path]::GetRelativePath($rootFullPath, $Candidate)
    $current = $rootFullPath
    foreach ($component in $relativePath -split '[\\/]') {
        if (-not $component -or $component -eq '.') {
            continue
        }

        $current = Join-Path $current $component
        $item = Get-Item -LiteralPath $current -Force -ErrorAction SilentlyContinue
        if ($null -eq $item) {
            break
        }

        $isReparsePoint = ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
        $hasLinkTarget = $item.PSObject.Properties.Name -contains 'LinkTarget' -and $null -ne $item.LinkTarget
        if ($isReparsePoint -or $hasLinkTarget) {
            throw "Refusing $Purpose through a symbolic link, junction, or reparse point: $current"
        }
    }
}

function Get-ContainedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,

        [Parameter(Mandatory = $true)]
        [string]$RelativePath,

        [Parameter(Mandatory = $true)]
        [string]$Purpose
    )

    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        throw "Refusing $Purpose with rooted relative path: $RelativePath"
    }

    $rootFullPath = [System.IO.Path]::GetFullPath($Root).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $rootFullPath ($RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)))
    $prefix = $rootFullPath + [System.IO.Path]::DirectorySeparatorChar
    if ($candidate -eq $rootFullPath -or -not $candidate.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing $Purpose outside root '$rootFullPath': $candidate"
    }

    Assert-NoReparsePointInContainedPath -Root $rootFullPath -Candidate $candidate -Purpose $Purpose

    return $candidate
}

function Assert-DirectoryPathCanBeCreated {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DirectoryPath
    )

    $candidate = [System.IO.Path]::GetFullPath($DirectoryPath)
    while ($candidate -and -not (Test-Path -LiteralPath $candidate)) {
        $parent = Split-Path -Parent $candidate
        if (-not $parent -or $parent -eq $candidate) {
            break
        }
        $candidate = $parent
    }

    if ($candidate -and (Test-Path -LiteralPath $candidate) -and -not (Test-Path -LiteralPath $candidate -PathType Container)) {
        throw "Cannot create directory because an ancestor is not a directory: $candidate"
    }
}

function Get-FileContentHash {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath
    )

    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash
}

function Get-TextHash {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Content)
    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [Convert]::ToHexString($hash.ComputeHash($bytes))
    }
    finally {
        $hash.Dispose()
    }
}

function Get-TrackedSkillFiles {
    $files = Invoke-Git -Arguments @("ls-files", "--", "skills/codex-*")
    $tracked = @(
        $files |
            Where-Object {
                $_ -and (Test-Path -LiteralPath (Join-Path $RepoRoot ($_ -replace "/", [System.IO.Path]::DirectorySeparatorChar)) -PathType Leaf)
            }
    )
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

function Test-IsGeneratedTextRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    return $GeneratedTextExtensions -contains [System.IO.Path]::GetExtension($RelativePath).ToLowerInvariant()
}

function Read-DevelopmentSkillDefinition {
    if (-not (Test-Path -LiteralPath $DefinitionPath -PathType Leaf)) {
        throw "Missing development skill definition: $DefinitionPath"
    }

    $definition = Get-Content -LiteralPath $DefinitionPath -Raw | ConvertFrom-Json
    if ($definition.schema_version -ne 1 -or -not $definition.skills) {
        throw "Unsupported or empty development skill definition: $DefinitionPath"
    }

    $sourceNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $copilotNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($entry in $definition.skills) {
        if ($entry.source_name -notmatch "^codex-[a-z0-9-]+$") {
            throw "Invalid source_name in $DefinitionRelativePath`: $($entry.source_name)"
        }
        if ($entry.copilot_name -notmatch "^copilot-[a-z0-9-]+$") {
            throw "Invalid copilot_name for $($entry.source_name): $($entry.copilot_name)"
        }
        if (-not $sourceNames.Add([string]$entry.source_name)) {
            throw "Duplicate source_name in $DefinitionRelativePath`: $($entry.source_name)"
        }
        if (-not $copilotNames.Add([string]$entry.copilot_name)) {
            throw "Duplicate copilot_name in $DefinitionRelativePath`: $($entry.copilot_name)"
        }
        foreach ($requiredProperty in @("default", "support", "role", "phase", "owns_durable_product_edits", "uses_development_workflow", "dependencies")) {
            if ($entry.PSObject.Properties.Name -notcontains $requiredProperty) {
                throw "Missing '$requiredProperty' for $($entry.source_name) in $DefinitionRelativePath"
            }
        }
    }

    foreach ($entry in $definition.skills) {
        foreach ($dependency in @($entry.dependencies)) {
            if (-not $sourceNames.Contains([string]$dependency)) {
                throw "Unknown dependency '$dependency' declared by $($entry.source_name)"
            }
            if ([string]$dependency -ceq [string]$entry.source_name) {
                throw "A skill cannot depend on itself: $($entry.source_name)"
            }
        }
    }

    return $definition
}

function Get-ReferencedSourceSkillNames {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$SourceSkillName
    )

    return @(
        [regex]::Matches($Content, $script:KnownSourceSkillPattern) |
            ForEach-Object { $_.Value } |
            Where-Object { $_ -cne $SourceSkillName } |
            Sort-Object -Unique
    )
}

function Assert-DeclaredDependenciesMatchContent {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$TrackedFiles
    )

    foreach ($entry in $DevelopmentSkillDefinition.skills) {
        $textFiles = @($TrackedFiles | Where-Object {
            (Get-SourceSkillNameFromRelativePath -RelativePath $_) -ceq $entry.source_name -and
            (Test-IsGeneratedTextRelativePath -RelativePath $_)
        })
        $referenced = @()
        foreach ($relativePath in $textFiles) {
            $source = Get-ContainedPath -Root $RepoRoot -RelativePath $relativePath -Purpose "source read"
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
                throw "Missing source file: $source"
            }
            $content = Get-Content -LiteralPath $source -Raw
            $referenced += Get-ReferencedSourceSkillNames -Content $content -SourceSkillName $entry.source_name
        }

        $actual = @($referenced | Sort-Object -Unique)
        $declared = @($entry.dependencies | Sort-Object -Unique)
        if (-not (Test-SequenceEqual -Left $actual -Right $declared)) {
            throw "Dependency declaration mismatch for $($entry.source_name). Declared: $($declared -join ', '); generated text references: $($actual -join ', ')"
        }
    }
}

function ConvertTo-SourceSkillName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RequestedSkillName
    )

    $normalized = ($RequestedSkillName -replace "\\", "/").Trim("/")
    $leaf = Split-Path -Leaf $normalized
    if ($script:SourceEntryByName.ContainsKey($leaf)) {
        return $leaf
    }
    if ($script:SourceNameByCopilotName.ContainsKey($leaf)) {
        return $script:SourceNameByCopilotName[$leaf]
    }

    $prefixed = "codex-$leaf"
    if ($script:SourceEntryByName.ContainsKey($prefixed)) {
        return $prefixed
    }

    throw "Unknown skill '$RequestedSkillName'. Available skills: $(@($script:SourceEntryByName.Keys | Sort-Object) -join ', ')"
}

function Get-SelectedSkillNames {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.Generic.HashSet[string]]$Available
    )

    if ($AllSkills) {
        $seedNames = @($Available | Sort-Object)
    }
    elseif (-not $SkillName -or $SkillName.Count -eq 0) {
        $seedNames = @($DevelopmentSkillDefinition.skills | Where-Object default | ForEach-Object { [string]$_.source_name } | Sort-Object)
    }
    else {
        $seedNames = @($SkillName | ForEach-Object { ConvertTo-SourceSkillName -RequestedSkillName $_ } | Sort-Object -Unique)
    }

    $closure = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $queue = [System.Collections.Generic.Queue[string]]::new()
    foreach ($name in $seedNames) {
        if (-not $Available.Contains($name)) {
            throw "Selected skill has no tracked source files: $name"
        }
        if ($closure.Add($name)) {
            $queue.Enqueue($name)
        }
    }

    while ($queue.Count -gt 0) {
        $name = $queue.Dequeue()
        $entry = $script:SourceEntryByName[$name]
        foreach ($dependency in @($entry.dependencies)) {
            if (-not $Available.Contains([string]$dependency)) {
                throw "Dependency '$dependency' required by '$name' has no tracked source files"
            }
            if ($closure.Add([string]$dependency)) {
                $queue.Enqueue([string]$dependency)
            }
        }
    }

    return @($closure | Sort-Object)
}

function ConvertTo-CopilotRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath
    )

    $sourceName = Get-SourceSkillNameFromRelativePath -RelativePath $SourceRelativePath
    $entry = $script:SourceEntryByName[$sourceName]
    if (-not $entry) {
        throw "No Copilot name mapping for source skill: $sourceName"
    }

    $sourcePrefix = "skills/$sourceName/"
    $innerPath = $SourceRelativePath.Substring($sourcePrefix.Length)
    return "$($entry.copilot_name)/$innerPath"
}

function ConvertTo-CopilotSkillContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,

        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath
    )

    if (-not (Test-IsGeneratedTextRelativePath -RelativePath $SourceRelativePath)) {
        return $Content
    }

    $converted = [regex]::Replace($Content, $script:KnownSourceSkillPattern, {
        param($match)
        $sourceName = $match.Value
        if (-not $script:SourceEntryByName.ContainsKey($sourceName)) {
            throw "No Copilot name mapping for generated identifier '$sourceName' in $SourceRelativePath"
        }
        return [string]$script:SourceEntryByName[$sourceName].copilot_name
    })
    $converted = $converted.Replace($DevelopmentWorkflowSkillReference, $CopilotDevelopmentWorkflowSkillReference)
    if ($converted -cmatch $script:KnownSourceSkillPattern) {
        throw "Generated content still contains a known source skill identifier in $SourceRelativePath"
    }

    return $converted
}

function Get-CopilotDevelopmentWorkflowRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceSkillName
    )

    return "$($script:SourceEntryByName[$SourceSkillName].copilot_name)/$CopilotDevelopmentWorkflowSkillReference"
}

function Read-ManagedManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManifestPath
    )

    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        return [pscustomobject]@{ Raw = $null; Value = $null; ManagedFiles = @() }
    }
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Managed manifest path exists and is not a file: $ManifestPath"
    }

    $raw = Get-Content -LiteralPath $ManifestPath -Raw
    if (-not $raw) {
        throw "Managed manifest is empty: $ManifestPath"
    }
    $value = $raw | ConvertFrom-Json
    $managedFiles = @($value.managed_files | Where-Object { $_ } | ForEach-Object { [string]$_ } | Sort-Object -Unique)
    return [pscustomobject]@{ Raw = $raw; Value = $value; ManagedFiles = $managedFiles }
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

function New-DesiredManifestContent {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ManagedFiles,

        [Parameter(Mandatory = $true)]
        [pscustomobject]$PreviousManifest
    )

    $sourceRepository = Get-SourceRepository
    $sourceCommit = Get-SourceCommit
    $installedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    if ($PreviousManifest.Value -and
        $PreviousManifest.Value.schema_version -eq $ManifestVersion -and
        [string]$PreviousManifest.Value.tool -ceq "codex-config install-copilot-skills.ps1" -and
        [string]$PreviousManifest.Value.source_repo -ceq [string]$sourceRepository -and
        [string]$PreviousManifest.Value.source_commit -ceq [string]$sourceCommit -and
        (Test-SequenceEqual -Left @($PreviousManifest.ManagedFiles) -Right @($ManagedFiles))) {
        if ($PreviousManifest.Value.installed_at -is [datetime]) {
            $installedAt = $PreviousManifest.Value.installed_at.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
        else {
            $installedAt = [string]$PreviousManifest.Value.installed_at
        }
    }

    $manifest = [ordered]@{
        schema_version = $ManifestVersion
        tool = "codex-config install-copilot-skills.ps1"
        source_repo = $sourceRepository
        source_commit = $sourceCommit
        installed_at = $installedAt
        managed_files = @($ManagedFiles)
    }
    return ($manifest | ConvertTo-Json -Depth 4)
}

function Write-ManagedManifestAtomic {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ManifestPath,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    if (-not $PSCmdlet.ShouldProcess($ManifestPath, "Atomically replace managed file manifest")) {
        return
    }

    $manifestParent = Split-Path -Parent $ManifestPath
    if (-not (Test-Path -LiteralPath $manifestParent)) {
        New-Item -ItemType Directory -Path $manifestParent -Force | Out-Null
    }
    $temporaryPath = Join-Path $manifestParent ("." + [System.IO.Path]::GetFileName($ManifestPath) + ".tmp-" + [System.Guid]::NewGuid().ToString("N"))
    try {
        Set-Utf8NoBomContent -LiteralPath $temporaryPath -Value $Content
        if (Test-Path -LiteralPath $ManifestPath -PathType Leaf) {
            [System.IO.File]::Move($temporaryPath, $ManifestPath, $true)
        }
        else {
            [System.IO.File]::Move($temporaryPath, $ManifestPath)
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) {
            Remove-Item -LiteralPath $temporaryPath -Force
        }
    }
}

function New-CopyOperation {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRelativePath,

        [Parameter(Mandatory = $true)]
        [string]$DestinationRelativePath,

        [switch]$Transform
    )

    $source = Get-ContainedPath -Root $RepoRoot -RelativePath $SourceRelativePath -Purpose "source read"
    $destination = Get-ContainedPath -Root $CopilotSkillsHome -RelativePath $DestinationRelativePath -Purpose "destination write"
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Missing source file: $source"
    }

    $content = $null
    $sourceHash = $null
    if ($Transform) {
        $content = ConvertTo-CopilotSkillContent -Content (Get-Content -LiteralPath $source -Raw) -SourceRelativePath $SourceRelativePath
        $sourceHash = Get-TextHash -Content $content
    }
    else {
        $sourceHash = Get-FileContentHash -LiteralPath $source
    }

    $destinationExists = Test-Path -LiteralPath $destination
    if ($destinationExists -and -not (Test-Path -LiteralPath $destination -PathType Leaf)) {
        throw "Destination exists and is not a file: $destination"
    }
    $unchanged = $destinationExists -and ((Get-FileContentHash -LiteralPath $destination) -ceq $sourceHash)
    if ($destinationExists -and -not $unchanged -and -not $Overwrite) {
        throw "Refusing to overwrite existing file with different content: $destination. Re-run with -Overwrite to replace Copilot skill files."
    }

    Assert-DirectoryPathCanBeCreated -DirectoryPath (Split-Path -Parent $destination)
    return [pscustomobject]@{
        Source = $source
        SourceRelativePath = $SourceRelativePath
        Destination = $destination
        DestinationRelativePath = $DestinationRelativePath
        Content = $content
        Transform = [bool]$Transform
        Exists = $destinationExists
        Unchanged = $unchanged
    }
}

function Backup-File {
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

    $backupDestination = Get-ContainedPath -Root $BackupRoot -RelativePath $RelativePath -Purpose "backup write"
    $backupParent = Split-Path -Parent $backupDestination
    if (-not (Test-Path -LiteralPath $backupParent)) {
        if ($PSCmdlet.ShouldProcess($backupParent, "Create backup directory")) {
            New-Item -ItemType Directory -Path $backupParent -Force | Out-Null
        }
    }
    if ($PSCmdlet.ShouldProcess($backupDestination, "Back up existing $RelativePath")) {
        Copy-Item -LiteralPath $Source -Destination $backupDestination
        $script:BackedUpFileCount++
    }
}

function Invoke-CopyOperation {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Operation,

        [string]$BackupRoot
    )

    if ($Operation.Unchanged) {
        $script:UnchangedFileCount++
        Write-Host "Unchanged: $($Operation.DestinationRelativePath)"
        return
    }

    if ($Operation.Exists) {
        Backup-File -Source $Operation.Destination -RelativePath $Operation.DestinationRelativePath -BackupRoot $BackupRoot
    }
    $parent = Split-Path -Parent $Operation.Destination
    if (-not (Test-Path -LiteralPath $parent)) {
        if ($PSCmdlet.ShouldProcess($parent, "Create directory")) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    $action = if ($Operation.Exists) { "Overwrite with generated $($Operation.SourceRelativePath)" } else { "Copy generated $($Operation.SourceRelativePath)" }
    if ($PSCmdlet.ShouldProcess($Operation.Destination, $action)) {
        if ($Operation.Transform) {
            Set-Utf8NoBomContent -LiteralPath $Operation.Destination -Value $Operation.Content
        }
        else {
            Copy-Item -LiteralPath $Operation.Source -Destination $Operation.Destination -Force
        }
        if ($Operation.Exists) {
            $script:OverwrittenFileCount++
        }
        else {
            $script:CopiedFileCount++
        }
    }
}

function Invoke-PruneOperations {
    param(
        [AllowEmptyCollection()]
        [pscustomobject[]]$Operations,

        [string]$BackupRoot
    )

    foreach ($operation in $Operations) {
        if (-not $operation.Exists) {
            continue
        }
        Backup-File -Source $operation.Destination -RelativePath $operation.RelativePath -BackupRoot $BackupRoot
        if ($PSCmdlet.ShouldProcess($operation.Destination, "Prune previously managed file no longer selected")) {
            Remove-Item -LiteralPath $operation.Destination -Force
            $script:PrunedFileCount++
            Write-Host "Pruned: $($operation.RelativePath)"
        }
    }
}

function Remove-EmptyPrunedDirectories {
    param(
        [AllowEmptyCollection()]
        [pscustomobject[]]$PruneOperations
    )

    $directories = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($operation in $PruneOperations) {
        $directory = Split-Path -Parent $operation.Destination
        while ($directory -and $directory -ne [System.IO.Path]::GetFullPath($CopilotSkillsHome)) {
            [void]$directories.Add($directory)
            $directory = Split-Path -Parent $directory
        }
    }

    foreach ($directory in ($directories | Sort-Object Length -Descending)) {
        if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
            continue
        }
        if (@(Get-ChildItem -LiteralPath $directory -Force).Count -gt 0) {
            continue
        }
        if ($PSCmdlet.ShouldProcess($directory, "Prune empty directory left by managed file removal")) {
            Remove-Item -LiteralPath $directory -Force
            $script:PrunedDirectoryCount++
            Write-Host "Pruned directory: $directory"
        }
    }
}

# Research and declaration validation. No destination mutation occurs before this block completes.
$DevelopmentSkillDefinition = Read-DevelopmentSkillDefinition
$script:SourceEntryByName = @{}
$script:SourceNameByCopilotName = @{}
foreach ($entry in $DevelopmentSkillDefinition.skills) {
    $script:SourceEntryByName[[string]$entry.source_name] = $entry
    $script:SourceNameByCopilotName[[string]$entry.copilot_name] = [string]$entry.source_name
}
$escapedKnownSourceNames = @(
    $script:SourceEntryByName.Keys |
        Sort-Object Length -Descending |
        ForEach-Object { [regex]::Escape([string]$_) }
)
$script:KnownSourceSkillPattern = "(?<![a-z0-9-])(?:$($escapedKnownSourceNames -join '|'))(?![a-z0-9-])"

$trackedFiles = @(Get-TrackedSkillFiles)
$available = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($file in $trackedFiles) {
    $sourceName = Get-SourceSkillNameFromRelativePath -RelativePath $file
    if (-not $script:SourceEntryByName.ContainsKey($sourceName)) {
        throw "Tracked source skill is missing from $DefinitionRelativePath`: $sourceName"
    }
    [void]$available.Add($sourceName)
}
foreach ($entry in $DevelopmentSkillDefinition.skills) {
    if (-not $available.Contains([string]$entry.source_name)) {
        throw "Skill definition has no tracked source files: $($entry.source_name)"
    }
}

Assert-DeclaredDependenciesMatchContent -TrackedFiles $trackedFiles
$selectedSkillNames = @(Get-SelectedSkillNames -Available $available)
$selected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($name in $selectedSkillNames) {
    [void]$selected.Add($name)
}
$selectedFiles = @($trackedFiles | Where-Object { $selected.Contains((Get-SourceSkillNameFromRelativePath -RelativePath $_)) })

$currentManagedFiles = @(
    @($selectedFiles | ForEach-Object { ConvertTo-CopilotRelativePath -SourceRelativePath $_ })
    @($selectedSkillNames | Where-Object { $script:SourceEntryByName[$_].uses_development_workflow } | ForEach-Object { Get-CopilotDevelopmentWorkflowRelativePath -SourceSkillName $_ })
) | Sort-Object -Unique

$manifestPath = Get-ContainedPath -Root $CopilotSkillsHome -RelativePath $ManifestRelativePath -Purpose "managed manifest write"
$previousManifest = Read-ManagedManifest -ManifestPath $manifestPath
foreach ($relativePath in $previousManifest.ManagedFiles) {
    [void](Get-ContainedPath -Root $CopilotSkillsHome -RelativePath $relativePath -Purpose "managed ownership")
}
$nextManagedFiles = if ($Prune) {
    @($currentManagedFiles)
}
else {
    @($previousManifest.ManagedFiles + $currentManagedFiles | Sort-Object -Unique)
}
$nextManagedSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
foreach ($relativePath in $nextManagedFiles) {
    [void]$nextManagedSet.Add($relativePath)
}

$copyOperations = @()
$generatedTextByRelativePath = @{}
foreach ($relativePath in $selectedFiles) {
    $destinationRelativePath = ConvertTo-CopilotRelativePath -SourceRelativePath $relativePath
    $transform = Test-IsGeneratedTextRelativePath -RelativePath $relativePath
    $operation = New-CopyOperation -SourceRelativePath $relativePath -DestinationRelativePath $destinationRelativePath -Transform:$transform
    $copyOperations += $operation
    if ($transform) {
        $generatedTextByRelativePath[$destinationRelativePath] = $operation.Content
    }
}
foreach ($sourceSkillName in $selectedSkillNames | Where-Object { $script:SourceEntryByName[$_].uses_development_workflow }) {
    $destinationRelativePath = Get-CopilotDevelopmentWorkflowRelativePath -SourceSkillName $sourceSkillName
    $operation = New-CopyOperation -SourceRelativePath $DevelopmentWorkflowSourceRelativePath -DestinationRelativePath $destinationRelativePath -Transform
    $copyOperations += $operation
    $generatedTextByRelativePath[$destinationRelativePath] = $operation.Content
}

# Verify every known generated cross-reference resolves in the next managed set.
foreach ($relativePath in $nextManagedFiles | Where-Object { Test-IsGeneratedTextRelativePath -RelativePath $_ }) {
    $content = $generatedTextByRelativePath[$relativePath]
    if ($null -eq $content) {
        $existingPath = Get-ContainedPath -Root $CopilotSkillsHome -RelativePath $relativePath -Purpose "managed cross-reference read"
        if (Test-Path -LiteralPath $existingPath -PathType Leaf) {
            $content = Get-Content -LiteralPath $existingPath -Raw
        }
    }
    if ($null -eq $content) {
        continue
    }
    foreach ($match in [regex]::Matches($content, "\bcopilot-[a-z0-9-]+\b")) {
        $copilotName = $match.Value
        if (-not $script:SourceNameByCopilotName.ContainsKey($copilotName)) {
            continue
        }
        if (-not $nextManagedSet.Contains("$copilotName/SKILL.md")) {
            throw "Generated cross-reference '$copilotName' in '$relativePath' is not present in the next managed set"
        }
    }
}

$pruneOperations = @()
if ($Prune) {
    foreach ($relativePath in $previousManifest.ManagedFiles) {
        if ($nextManagedSet.Contains($relativePath)) {
            continue
        }
        $destination = Get-ContainedPath -Root $CopilotSkillsHome -RelativePath $relativePath -Purpose "managed prune"
        $exists = Test-Path -LiteralPath $destination
        if ($exists -and -not (Test-Path -LiteralPath $destination -PathType Leaf)) {
            throw "Refusing to prune managed path that is not a file: $destination"
        }
        $pruneOperations += [pscustomobject]@{ RelativePath = $relativePath; Destination = $destination; Exists = $exists }
    }
}

Assert-DirectoryPathCanBeCreated -DirectoryPath $CopilotSkillsHome
Assert-DirectoryPathCanBeCreated -DirectoryPath (Split-Path -Parent $manifestPath)
$backupRoot = $null
$needsBackup = $Backup -and (@($copyOperations | Where-Object { $_.Exists -and -not $_.Unchanged }).Count -gt 0 -or @($pruneOperations | Where-Object Exists).Count -gt 0)
if ($needsBackup) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $backupRoot = "${CopilotSkillsHome}.backup-$timestamp-$([System.Guid]::NewGuid().ToString('N'))"
    if (Test-Path -LiteralPath $backupRoot) {
        throw "Backup root already exists: $backupRoot"
    }
    Assert-DirectoryPathCanBeCreated -DirectoryPath $backupRoot
    foreach ($operation in $copyOperations | Where-Object { $_.Exists -and -not $_.Unchanged }) {
        [void](Get-ContainedPath -Root $backupRoot -RelativePath $operation.DestinationRelativePath -Purpose "backup preflight")
    }
    foreach ($operation in $pruneOperations | Where-Object Exists) {
        [void](Get-ContainedPath -Root $backupRoot -RelativePath $operation.RelativePath -Purpose "backup preflight")
    }
}

$desiredManifestContent = New-DesiredManifestContent -ManagedFiles $nextManagedFiles -PreviousManifest $previousManifest
$manifestChanged = $previousManifest.Raw -cne $desiredManifestContent

# Apply the fully preflighted plan. Copy first so a runtime copy failure cannot trigger pruning.
foreach ($operation in $copyOperations) {
    Invoke-CopyOperation -Operation $operation -BackupRoot $backupRoot
}
Invoke-PruneOperations -Operations $pruneOperations -BackupRoot $backupRoot
Remove-EmptyPrunedDirectories -PruneOperations $pruneOperations
if ($manifestChanged) {
    Write-ManagedManifestAtomic -ManifestPath $manifestPath -Content $desiredManifestContent
}

$installedSkillNames = @($selectedSkillNames | ForEach-Object { [string]$script:SourceEntryByName[$_].copilot_name })
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
