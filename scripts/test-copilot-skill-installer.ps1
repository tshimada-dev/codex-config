[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$InstallerPath = Join-Path $ScriptDir "install-copilot-skills.ps1"
$DefinitionPath = Join-Path $RepoRoot "config/development-skills.json"
$TestRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-config-copilot-installer-test-" + [System.Guid]::NewGuid().ToString("N"))

function Assert-True {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw "Assertion failed: $Message"
    }
}

function Assert-SequenceEqual {
    param(
        [object[]]$Expected,
        [object[]]$Actual,
        [string]$Message
    )

    $expectedJson = @($Expected) | ConvertTo-Json -Compress
    $actualJson = @($Actual) | ConvertTo-Json -Compress
    if ($expectedJson -cne $actualJson) {
        throw "Assertion failed: $Message`nExpected: $expectedJson`nActual:   $actualJson"
    }
}

function Invoke-TestInstaller {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DestinationRoot,
        [string[]]$Arguments = @()
    )

    $parameters = @{ CopilotSkillsHome = $DestinationRoot }
    for ($index = 0; $index -lt $Arguments.Count; $index++) {
        switch ($Arguments[$index]) {
            "-SkillName" {
                $index++
                $parameters.SkillName = $Arguments[$index]
            }
            "-Prune" { $parameters.Prune = $true }
            "-Overwrite" { $parameters.Overwrite = $true }
            "-Backup" { $parameters.Backup = $true }
            "-AllSkills" { $parameters.AllSkills = $true }
            default { throw "Unknown test installer argument: $($Arguments[$index])" }
        }
    }
    & $InstallerPath @parameters
}

function Read-InstallManifest {
    param([string]$DestinationRoot)

    $path = Join-Path $DestinationRoot ".codex-config-copilot-managed-files"
    Assert-True -Condition (Test-Path -LiteralPath $path -PathType Leaf) -Message "managed manifest should exist at $path"
    return Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
}

function Get-TreeSnapshot {
    param([string]$DestinationRoot)

    $snapshot = [ordered]@{}
    foreach ($file in Get-ChildItem -LiteralPath $DestinationRoot -Recurse -Force -File | Sort-Object FullName) {
        $relative = [System.IO.Path]::GetRelativePath($DestinationRoot, $file.FullName).Replace("\", "/")
        $snapshot[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    }

    return $snapshot
}

function Assert-SnapshotEqual {
    param(
        [System.Collections.IDictionary]$Expected,
        [System.Collections.IDictionary]$Actual,
        [string]$Message
    )

    Assert-SequenceEqual -Expected @($Expected.Keys) -Actual @($Actual.Keys) -Message "$Message (paths)"
    foreach ($path in $Expected.Keys) {
        Assert-True -Condition ($Expected[$path] -ceq $Actual[$path]) -Message "$Message (content: $path)"
    }
}

function Get-ExpectedManagedPaths {
    param([string[]]$SourceNames)

    $definition = Get-Content -LiteralPath $DefinitionPath -Raw | ConvertFrom-Json
    $bySource = @{}
    foreach ($entry in $definition.skills) {
        $bySource[$entry.source_name] = $entry
    }

    $closure = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $queue = [System.Collections.Generic.Queue[string]]::new()
    foreach ($sourceName in $SourceNames) {
        if ($closure.Add($sourceName)) {
            $queue.Enqueue($sourceName)
        }
    }
    while ($queue.Count -gt 0) {
        $sourceName = $queue.Dequeue()
        foreach ($dependency in @($bySource[$sourceName].dependencies)) {
            if ($closure.Add([string]$dependency)) {
                $queue.Enqueue([string]$dependency)
            }
        }
    }

    $paths = @(
        & git -C $RepoRoot ls-files -- "skills/codex-*" |
            Where-Object {
                if ($_ -notmatch "^skills/(?<source>codex-[^/]+)/") {
                    return $false
                }
                return $_ -notmatch "/agents/" -and $closure.Contains($Matches["source"])
            } |
            ForEach-Object {
                [void]($_ -match "^skills/(?<source>codex-[^/]+)/(?<inner>.+)$")
                "$($bySource[$Matches['source']].copilot_name)/$($Matches['inner'])"
            }
    )
    foreach ($sourceName in $closure) {
        $entry = $bySource[$sourceName]
        if ($entry.uses_development_workflow) {
            $paths += "$($entry.copilot_name)/references/development-workflow.md"
        }
    }

    return @($paths | Sort-Object -Unique)
}

function Assert-CrossReferencesResolve {
    param([string]$DestinationRoot)

    $definition = Get-Content -LiteralPath $DefinitionPath -Raw | ConvertFrom-Json
    $knownTargets = @($definition.skills.copilot_name)
    $knownSourcePattern = "(?<![a-z0-9-])(?:$(@($definition.skills.source_name | Sort-Object Length -Descending | ForEach-Object { [regex]::Escape([string]$_) }) -join '|'))(?![a-z0-9-])"
    $textExtensions = @(".md", ".ps1", ".py", ".json", ".yaml", ".yml", ".toml", ".txt")
    $installed = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($skillFile in Get-ChildItem -LiteralPath $DestinationRoot -Recurse -File -Filter "SKILL.md") {
        [void]$installed.Add((Split-Path -Leaf (Split-Path -Parent $skillFile.FullName)))
    }

    foreach ($file in Get-ChildItem -LiteralPath $DestinationRoot -Recurse -File | Where-Object { $textExtensions -contains $_.Extension.ToLowerInvariant() }) {
        $content = Get-Content -LiteralPath $file.FullName -Raw
        Assert-True -Condition ($content -cnotmatch $knownSourcePattern) -Message "generated text still contains a known source skill identifier: $($file.FullName)"
        foreach ($match in [regex]::Matches($content, "\bcopilot-[a-z0-9-]+\b")) {
            $target = $match.Value
            if ($target -in $knownTargets) {
                Assert-True -Condition $installed.Contains($target) -Message "generated reference '$target' does not resolve for $($file.FullName)"
            }
        }
    }
}

if (-not (Test-Path -LiteralPath $DefinitionPath -PathType Leaf)) {
    throw "Missing development skill definition: $DefinitionPath"
}

$definition = Get-Content -LiteralPath $DefinitionPath -Raw | ConvertFrom-Json
$trackedSkillNames = @(
    & git -C $RepoRoot ls-files -- "skills/codex-*/SKILL.md" |
        Where-Object { Test-Path -LiteralPath (Join-Path $RepoRoot ($_ -replace "/", [System.IO.Path]::DirectorySeparatorChar)) -PathType Leaf } |
        ForEach-Object { if ($_ -match "^skills/(codex-[^/]+)/SKILL\.md$") { $Matches[1] } } |
        Sort-Object -Unique
)
Assert-SequenceEqual -Expected $trackedSkillNames -Actual @($definition.skills.source_name | Sort-Object) -Message "definition should map every tracked codex-* skill"
Assert-SequenceEqual -Expected @("codex-cloud-ops-intake") -Actual @($definition.skills | Where-Object support | ForEach-Object source_name | Sort-Object) -Message "support skills"
Assert-SequenceEqual -Expected @("codex-implementation") -Actual @($definition.skills | Where-Object owns_durable_product_edits | ForEach-Object source_name) -Message "durable edit owner"
foreach ($entry in $definition.skills) {
    $skillPath = Join-Path $RepoRoot "skills/$($entry.source_name)/SKILL.md"
    $content = Get-Content -LiteralPath $skillPath -Raw
    $declaredDependencies = @($entry.dependencies | Sort-Object -Unique)
    $referencedDependencies = @(
        [regex]::Matches($content, "``(?<name>codex-[a-z0-9-]+)``") |
            ForEach-Object { $_.Groups["name"].Value } |
            Where-Object { $_ -cne $entry.source_name } |
            Sort-Object -Unique
    )
    Assert-SequenceEqual -Expected $referencedDependencies -Actual $declaredDependencies -Message "declared dependencies for $($entry.source_name)"
}

$defaultSources = @($definition.skills | Where-Object default | ForEach-Object source_name)
$expectedDefaultPaths = Get-ExpectedManagedPaths -SourceNames $defaultSources

try {
    New-Item -ItemType Directory -Path $TestRoot | Out-Null

    Write-Host "TEST: default install, manifest paths, and cross-reference closure"
    $defaultHome = Join-Path $TestRoot "default"
    Invoke-TestInstaller -DestinationRoot $defaultHome
    $defaultManifest = Read-InstallManifest -DestinationRoot $defaultHome
    Assert-SequenceEqual -Expected $expectedDefaultPaths -Actual @($defaultManifest.managed_files) -Message "default managed paths"
    Assert-CrossReferencesResolve -DestinationRoot $defaultHome

    Write-Host "TEST: idempotent reinstall"
    $beforeIdempotent = Get-TreeSnapshot -DestinationRoot $defaultHome
    Invoke-TestInstaller -DestinationRoot $defaultHome
    $afterIdempotent = Get-TreeSnapshot -DestinationRoot $defaultHome
    Assert-SnapshotEqual -Expected $beforeIdempotent -Actual $afterIdempotent -Message "second default install should be idempotent"

    Write-Host "TEST: partial install without prune preserves ownership union"
    $partialHome = Join-Path $TestRoot "partial"
    Invoke-TestInstaller -DestinationRoot $partialHome
    Invoke-TestInstaller -DestinationRoot $partialHome -Arguments @("-SkillName", "effort-estimator")
    $partialManifest = Read-InstallManifest -DestinationRoot $partialHome
    $expectedUnion = @($expectedDefaultPaths + (Get-ExpectedManagedPaths -SourceNames @("codex-effort-estimator")) | Sort-Object -Unique)
    Assert-SequenceEqual -Expected $expectedUnion -Actual @($partialManifest.managed_files) -Message "partial no-prune ownership union"

    Write-Host "TEST: partial prune makes selected closure authoritative"
    Invoke-TestInstaller -DestinationRoot $partialHome -Arguments @("-SkillName", "effort-estimator", "-Prune")
    $prunedManifest = Read-InstallManifest -DestinationRoot $partialHome
    $expectedPruned = Get-ExpectedManagedPaths -SourceNames @("codex-effort-estimator")
    Assert-SequenceEqual -Expected $expectedPruned -Actual @($prunedManifest.managed_files) -Message "partial prune managed paths"
    Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $partialHome "copilot-implementation/SKILL.md"))) -Message "prune should remove previously managed unselected files"

    Write-Host "TEST: conflict plus prune performs no mutation"
    $conflictHome = Join-Path $TestRoot "conflict"
    Invoke-TestInstaller -DestinationRoot $conflictHome
    $conflictPath = Join-Path $conflictHome "copilot-pr-readiness/SKILL.md"
    [System.IO.File]::AppendAllText($conflictPath, "`nconflict-marker`n")
    $beforeConflict = Get-TreeSnapshot -DestinationRoot $conflictHome
    $failedAsExpected = $false
    try {
        Invoke-TestInstaller -DestinationRoot $conflictHome -Arguments @("-SkillName", "pr-readiness", "-Prune")
    }
    catch {
        $failedAsExpected = $true
    }
    Assert-True -Condition $failedAsExpected -Message "conflicting prune install should fail"
    $afterConflict = Get-TreeSnapshot -DestinationRoot $conflictHome
    Assert-SnapshotEqual -Expected $beforeConflict -Actual $afterConflict -Message "conflict plus prune should not mutate files or manifest"

    Write-Host "TEST: managed path containment fails before mutation"
    $containmentHome = Join-Path $TestRoot "containment"
    New-Item -ItemType Directory -Path $containmentHome | Out-Null
    $outsidePath = Join-Path $TestRoot "outside-sentinel.txt"
    [System.IO.File]::WriteAllText($outsidePath, "outside-sentinel")
    $maliciousManifestPath = Join-Path $containmentHome ".codex-config-copilot-managed-files"
    [System.IO.File]::WriteAllText($maliciousManifestPath, '{"schema_version":1,"managed_files":["../outside-sentinel.txt"]}')
    $beforeContainment = Get-TreeSnapshot -DestinationRoot $containmentHome
    $outsideHash = (Get-FileHash -LiteralPath $outsidePath -Algorithm SHA256).Hash
    $containmentFailed = $false
    try {
        Invoke-TestInstaller -DestinationRoot $containmentHome -Arguments @("-SkillName", "repo-scout", "-Prune")
    }
    catch {
        $containmentFailed = $true
    }
    Assert-True -Condition $containmentFailed -Message "out-of-root managed path should fail preflight"
    Assert-SnapshotEqual -Expected $beforeContainment -Actual (Get-TreeSnapshot -DestinationRoot $containmentHome) -Message "path containment failure should not mutate the managed root"
    Assert-True -Condition ($outsideHash -ceq (Get-FileHash -LiteralPath $outsidePath -Algorithm SHA256).Hash) -Message "path containment failure should not mutate the outside file"

    Write-Host "TEST: symbolic-link or junction ancestor fails before mutation"
    $linkHome = Join-Path $TestRoot "link-containment"
    $linkOutside = Join-Path $TestRoot "link-outside"
    New-Item -ItemType Directory -Path $linkHome, $linkOutside | Out-Null
    $linkPath = Join-Path $linkHome "copilot-repo-scout"
    $linkCreated = $false
    try {
        New-Item -ItemType SymbolicLink -Path $linkPath -Target $linkOutside -ErrorAction Stop | Out-Null
        $linkCreated = $true
    }
    catch {
        if ($IsWindows) {
            try {
                New-Item -ItemType Junction -Path $linkPath -Target $linkOutside -ErrorAction Stop | Out-Null
                $linkCreated = $true
            }
            catch {
                Write-Warning "Skipping reparse-point regression because neither a symbolic link nor junction could be created: $($_.Exception.Message)"
            }
        }
        else {
            throw "Linux/macOS CI must support the symbolic-link containment regression: $($_.Exception.Message)"
        }
    }

    if ($linkCreated) {
        $linkFailed = $false
        try {
            Invoke-TestInstaller -DestinationRoot $linkHome -Arguments @("-SkillName", "repo-scout")
        }
        catch {
            $linkFailed = $true
        }
        Assert-True -Condition $linkFailed -Message "destination ancestor symlink or junction should fail preflight"
        Assert-True -Condition (-not (Test-Path -LiteralPath (Join-Path $linkHome ".codex-config-copilot-managed-files"))) -Message "link containment failure should not write a manifest"
        Assert-True -Condition (@(Get-ChildItem -LiteralPath $linkOutside -Force).Count -eq 0) -Message "link containment failure should not write outside the managed root"
    }

    Write-Host "TEST: conflict followed by overwrite succeeds"
    $overwriteHome = Join-Path $TestRoot "overwrite"
    Invoke-TestInstaller -DestinationRoot $overwriteHome -Arguments @("-SkillName", "pr-readiness")
    $overwritePath = Join-Path $overwriteHome "copilot-pr-readiness/SKILL.md"
    [System.IO.File]::AppendAllText($overwritePath, "`noverwrite-marker`n")
    Invoke-TestInstaller -DestinationRoot $overwriteHome -Arguments @("-SkillName", "pr-readiness", "-Overwrite")
    Assert-True -Condition ((Get-Content -LiteralPath $overwritePath -Raw) -notmatch "overwrite-marker") -Message "overwrite should replace conflicting content"

    Write-Host "TEST: overwrite with backup preserves original"
    [System.IO.File]::AppendAllText($overwritePath, "`nbackup-marker`n")
    Invoke-TestInstaller -DestinationRoot $overwriteHome -Arguments @("-SkillName", "pr-readiness", "-Overwrite", "-Backup")
    $backupRoots = @(Get-ChildItem -LiteralPath $TestRoot -Directory -Filter "overwrite.backup-*")
    Assert-True -Condition ($backupRoots.Count -eq 1) -Message "overwrite with backup should create one backup root"
    $backedUpSkill = Join-Path $backupRoots[0].FullName "copilot-pr-readiness/SKILL.md"
    Assert-True -Condition (Test-Path -LiteralPath $backedUpSkill -PathType Leaf) -Message "backup should contain the overwritten path"
    Assert-True -Condition ((Get-Content -LiteralPath $backedUpSkill -Raw) -match "backup-marker") -Message "backup should preserve original conflicting content"
    Assert-True -Condition ((Get-Content -LiteralPath $overwritePath -Raw) -notmatch "backup-marker") -Message "destination should contain regenerated content"

    Write-Host "TEST: all skills install expected paths and resolved cross-references"
    $allHome = Join-Path $TestRoot "all"
    Invoke-TestInstaller -DestinationRoot $allHome -Arguments @("-AllSkills")
    $allManifest = Read-InstallManifest -DestinationRoot $allHome
    $expectedAllPaths = Get-ExpectedManagedPaths -SourceNames @($definition.skills.source_name)
    Assert-SequenceEqual -Expected $expectedAllPaths -Actual @($allManifest.managed_files) -Message "all-skills managed paths"
    Assert-CrossReferencesResolve -DestinationRoot $allHome
    $manifestExternalPrefixPath = Join-Path $allHome "copilot-claude-code-reviewer/scripts/invoke-claude-review.ps1"
    Assert-True -Condition ((Get-Content -LiteralPath $manifestExternalPrefixPath -Raw).Contains("codex-claude-code-review-")) -Message "manifest-external codex-* prefix should not be transformed or rejected"

    Write-Host "Copilot skill installer regression tests passed."
}
finally {
    if (Test-Path -LiteralPath $TestRoot) {
        $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
        $testRootFull = [System.IO.Path]::GetFullPath($TestRoot)
        if (-not $testRootFull.StartsWith($tempRoot + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove test directory outside the system temp root: $testRootFull"
        }
        Remove-Item -LiteralPath $TestRoot -Recurse -Force
    }
}
