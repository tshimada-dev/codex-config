[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$errors = [System.Collections.Generic.List[string]]::new()
$manifestPath = Join-Path $RepoRoot "config/development-skills.json"
$contractReference = "../../rules/development-workflow.md"
$allowedPhases = @(
    "intake", "scouting", "planning", "debugging", "implementation",
    "verification", "readiness", "paused", "handoff"
)

function Add-ValidationError {
    param([Parameter(Mandatory = $true)][string]$Message)
    $errors.Add($Message)
}

function Get-RepoPath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    Join-Path $RepoRoot ($RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
}

function Read-RequiredFile {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Get-RepoPath -RelativePath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-ValidationError "${RelativePath}: missing file"
        return $null
    }

    Get-Content -LiteralPath $path -Raw
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "config/development-skills.json is missing."
}

try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
}
catch {
    throw "config/development-skills.json is invalid JSON: $($_.Exception.Message)"
}

if ($manifest.schema_version -ne 1) {
    Add-ValidationError "config/development-skills.json: unsupported schema_version '$($manifest.schema_version)'"
}

$skills = @($manifest.skills)
if ($skills.Count -eq 0) {
    Add-ValidationError "config/development-skills.json: skills must not be empty"
}

$skillsBySource = @{}
$copilotNames = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($skill in $skills) {
    $sourceName = [string]$skill.source_name
    $copilotName = [string]$skill.copilot_name
    if ($sourceName -notmatch '^codex-[a-z0-9-]+$') {
        Add-ValidationError "config/development-skills.json: invalid source_name '$sourceName'"
        continue
    }
    if ($skillsBySource.ContainsKey($sourceName)) {
        Add-ValidationError "config/development-skills.json: duplicate source_name '$sourceName'"
        continue
    }
    $skillsBySource[$sourceName] = $skill

    $expectedCopilotName = $sourceName -replace '^codex-', 'copilot-'
    if ($copilotName -ne $expectedCopilotName) {
        Add-ValidationError "config/development-skills.json: $sourceName copilot_name must be '$expectedCopilotName'"
    }
    if (-not $copilotNames.Add($copilotName)) {
        Add-ValidationError "config/development-skills.json: duplicate copilot_name '$copilotName'"
    }

    $phase = [string]$skill.phase
    if ($phase -and $phase -notin $allowedPhases) {
        Add-ValidationError "config/development-skills.json: $sourceName has unsupported phase '$phase'"
    }
    if ([string]::IsNullOrWhiteSpace([string]$skill.role)) {
        Add-ValidationError "config/development-skills.json: $sourceName is missing role"
    }
}

$trackedSkillNames = @(
    Get-ChildItem -LiteralPath (Get-RepoPath -RelativePath "skills") -Directory -Filter "codex-*" |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "SKILL.md") -PathType Leaf } |
        ForEach-Object Name |
        Sort-Object
)
$declaredSkillNames = @($skillsBySource.Keys | Sort-Object)
if (($trackedSkillNames -join "`n") -ne ($declaredSkillNames -join "`n")) {
    Add-ValidationError "config/development-skills.json: declared source paths differ from tracked skills. Declared=[$($declaredSkillNames -join ', ')]; tracked=[$($trackedSkillNames -join ', ')]"
}

$durableOwners = @($skills | Where-Object { $_.owns_durable_product_edits -eq $true })
if ($durableOwners.Count -ne 1 -or $durableOwners[0].source_name -ne "codex-implementation-loop") {
    Add-ValidationError "config/development-skills.json: codex-implementation-loop must be the single durable product/repository edit owner"
}

$contractContent = Read-RequiredFile -RelativePath "rules/development-workflow.md"
if ($null -ne $contractContent) {
    foreach ($heading in @(
        "## Expected Outcome and Evidence",
        "## Implementation Feedback",
        "## Workflow Phases",
        "## Ownership and Transitions",
        "## Final Verification and Readiness",
        "## Repository Trust"
    )) {
        if (-not $contractContent.Contains($heading)) {
            Add-ValidationError "rules/development-workflow.md: missing required heading '$heading'"
        }
    }
    foreach ($phase in $allowedPhases) {
        if (-not $contractContent.Contains("``$phase``")) {
            Add-ValidationError "rules/development-workflow.md: missing workflow phase '$phase'"
        }
    }
    foreach ($readiness in @("ready", "conditionally-ready", "not-ready")) {
        if (-not $contractContent.Contains("``$readiness``")) {
            Add-ValidationError "rules/development-workflow.md: missing readiness state '$readiness'"
        }
    }
}

foreach ($skill in $skills) {
    $skillName = [string]$skill.source_name
    $relativePath = "skills/$skillName/SKILL.md"
    $content = Read-RequiredFile -RelativePath $relativePath
    if ($null -eq $content) { continue }

    $frontmatterMatch = [regex]::Match($content, "(?s)\A---\s*\r?\n(?<body>.*?)\r?\n---")
    if (-not $frontmatterMatch.Success) {
        Add-ValidationError "${relativePath}: missing YAML frontmatter"
        continue
    }

    $frontmatter = $frontmatterMatch.Groups["body"].Value
    $nameMatch = [regex]::Match($frontmatter, "(?m)^name:\s*(?<value>\S+)\s*$")
    if (-not $nameMatch.Success -or $nameMatch.Groups["value"].Value -ne $skillName) {
        Add-ValidationError "${relativePath}: frontmatter name must equal '$skillName'"
    }
    $descriptionMatch = [regex]::Match($frontmatter, "(?m)^description:\s*(?<value>.+?)\s*$")
    if (-not $descriptionMatch.Success -or [string]::IsNullOrWhiteSpace($descriptionMatch.Groups["value"].Value)) {
        Add-ValidationError "${relativePath}: missing non-empty description"
    }

    if ($skill.uses_development_workflow -eq $true -and -not $content.Contains($contractReference)) {
        Add-ValidationError "${relativePath}: manifest requires the shared development workflow reference"
    }
    if ($skill.uses_development_workflow -ne $true -and $content.Contains($contractReference)) {
        Add-ValidationError "${relativePath}: references the shared workflow but manifest does not declare it"
    }

    $actualDependencies = @(
        [regex]::Matches($content, "``(?<name>codex-[a-z0-9-]+)``") |
            ForEach-Object { $_.Groups["name"].Value } |
            Where-Object { $_ -ne $skillName } |
            Sort-Object -Unique
    )
    $declaredDependencies = @($skill.dependencies | ForEach-Object { [string]$_ } | Sort-Object -Unique)
    foreach ($dependency in $declaredDependencies) {
        if (-not $skillsBySource.ContainsKey($dependency)) {
            Add-ValidationError "${relativePath}: manifest dependency '$dependency' is not a declared skill"
        }
    }
    if (($actualDependencies -join "`n") -ne ($declaredDependencies -join "`n")) {
        Add-ValidationError "${relativePath}: exact skill references must equal manifest dependencies. Declared=[$($declaredDependencies -join ', ')]; actual=[$($actualDependencies -join ', ')]"
    }

    if ($skill.phase -eq "debugging" -and $descriptionMatch.Success -and
        $descriptionMatch.Groups["value"].Value -match '(?i)\b(fix|implement|patch)\b') {
        Add-ValidationError "${relativePath}: debugging description claims a durable-edit action"
    }
    if ($skill.phase -eq "readiness" -and $skill.owns_durable_product_edits -ne $true -and
        -not $declaredDependencies.Contains("codex-implementation-loop")) {
        Add-ValidationError "${relativePath}: readiness must hand durable corrections to codex-implementation-loop"
    }
    if ($skill.phase -eq "readiness" -and $skill.owns_durable_product_edits -ne $true -and
        $content -match '(?mi)^\s*\d+\.\s+(fix|patch|edit|change|update)\b') {
        Add-ValidationError "${relativePath}: readiness contains a numbered instruction that directly owns a durable edit"
    }
}

$readmeContent = Read-RequiredFile -RelativePath "README.md"
if ($null -ne $readmeContent) {
    foreach ($skill in @($skills | Where-Object { $_.default -eq $true })) {
        $shortName = ([string]$skill.source_name) -replace '^codex-', ''
        if (-not $readmeContent.Contains("``$shortName``")) {
            Add-ValidationError "README.md: missing manifest default Copilot skill '$shortName'"
        }
    }
}

$runTemplate = Read-RequiredFile -RelativePath "templates/agent-run.md"
if ($null -ne $runTemplate) {
    $phaseMatch = [regex]::Match($runTemplate, '(?m)^Phase:\s*`(?<phases>[^`]+)`\s*$')
    if (-not $phaseMatch.Success) {
        Add-ValidationError "templates/agent-run.md: missing parseable Phase taxonomy"
    }
    else {
        $templatePhases = @($phaseMatch.Groups["phases"].Value -split '\s*\|\s*' | Sort-Object -Unique)
        if (($templatePhases -join "`n") -ne (($allowedPhases | Sort-Object) -join "`n")) {
            Add-ValidationError "templates/agent-run.md: Phase taxonomy must match the development workflow"
        }
    }
}

$jaRoot = Get-RepoPath -RelativePath "docs/ja"
if (Test-Path -LiteralPath $jaRoot -PathType Container) {
    foreach ($doc in Get-ChildItem -LiteralPath $jaRoot -Recurse -File -Filter "*.md") {
        $content = Get-Content -LiteralPath $doc.FullName -Raw
        $sourceMatch = [regex]::Match($content, "(?m)^source:\s*(?<path>.+?)\s*$")
        if (-not $sourceMatch.Success) { continue }
        $sourceRelativePath = $sourceMatch.Groups["path"].Value.Trim()
        if (-not (Test-Path -LiteralPath (Get-RepoPath -RelativePath $sourceRelativePath) -PathType Leaf)) {
            $docRelativePath = [System.IO.Path]::GetRelativePath($RepoRoot, $doc.FullName).Replace("\", "/")
            Add-ValidationError "${docRelativePath}: source path does not exist: $sourceRelativePath"
        }
    }
}

foreach ($requiredJaDoc in @("docs/ja/rules/development-workflow.md", "docs/ja/AGENTS.md")) {
    if (-not (Test-Path -LiteralPath (Get-RepoPath -RelativePath $requiredJaDoc) -PathType Leaf)) {
        Add-ValidationError "${requiredJaDoc}: missing Japanese reference document"
    }
}

if ($errors.Count -gt 0) {
    foreach ($message in $errors) { Write-Error $message -ErrorAction Continue }
    throw "Development workflow validation failed with $($errors.Count) error(s)."
}

Write-Host "Development workflow validation passed for $($skills.Count) manifest-declared skills."
