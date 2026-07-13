[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$errors = [System.Collections.Generic.List[string]]::new()

$coreSkillNames = @(
    "codex-task-intake",
    "codex-repo-scout",
    "codex-plan-slices",
    "codex-debug-discipline",
    "codex-implementation-loop",
    "codex-ui-quality-gate",
    "codex-pr-readiness"
)

$contractReference = "../../rules/development-workflow.md"
$requiredInvariantIds = @{
    "codex-task-intake" = @("shared-contract", "explicit-trust")
    "codex-repo-scout" = @("shared-contract", "explicit-trust")
    "codex-plan-slices" = @("shared-contract", "acceptance-evidence")
    "codex-debug-discipline" = @("shared-contract", "debug-handoff")
    "codex-implementation-loop" = @("shared-contract", "implementation-test-first")
    "codex-ui-quality-gate" = @("shared-contract", "ui-handoff")
    "codex-pr-readiness" = @("shared-contract", "readiness-states")
}

function Add-ValidationError {
    param([Parameter(Mandatory = $true)][string]$Message)

    $errors.Add($Message)
}

function Get-RepoPath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    return Join-Path $RepoRoot ($RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar)
}

function Read-RequiredFile {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Get-RepoPath -RelativePath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-ValidationError "$RelativePath`: missing file"
        return $null
    }

    return Get-Content -LiteralPath $path -Raw
}

$contractContent = Read-RequiredFile -RelativePath "rules/development-workflow.md"
if ($null -ne $contractContent) {
    foreach ($heading in @(
        "## Expected Outcome and Evidence",
        "## Implementation Feedback",
        "## Ownership and Transitions",
        "## Final Verification and Readiness",
        "## Repository Trust"
    )) {
        if (-not $contractContent.Contains($heading)) {
            Add-ValidationError "rules/development-workflow.md`: missing required heading '$heading'"
        }
    }

    foreach ($readiness in @("ready", "conditionally-ready", "not-ready")) {
        if (-not $contractContent.Contains("``$readiness``")) {
            Add-ValidationError "rules/development-workflow.md`: missing readiness state '$readiness'"
        }
    }
}

$skillContents = @{}
foreach ($skillName in $coreSkillNames) {
    $relativePath = "skills/$skillName/SKILL.md"
    $content = Read-RequiredFile -RelativePath $relativePath
    if ($null -eq $content) {
        continue
    }

    $skillContents[$skillName] = $content
    $frontmatterMatch = [regex]::Match($content, "(?s)\A---\s*\r?\n(?<body>.*?)\r?\n---")
    if (-not $frontmatterMatch.Success) {
        Add-ValidationError "$relativePath`: missing YAML frontmatter"
        continue
    }

    $frontmatter = $frontmatterMatch.Groups["body"].Value
    $nameMatch = [regex]::Match($frontmatter, "(?m)^name:\s*(?<value>\S+)\s*$")
    if (-not $nameMatch.Success -or $nameMatch.Groups["value"].Value -ne $skillName) {
        Add-ValidationError "$relativePath`: frontmatter name must equal '$skillName'"
    }

    $descriptionMatch = [regex]::Match($frontmatter, "(?m)^description:\s*(?<value>.+?)\s*$")
    if (-not $descriptionMatch.Success -or [string]::IsNullOrWhiteSpace($descriptionMatch.Groups["value"].Value)) {
        Add-ValidationError "$relativePath`: missing non-empty description"
    }

    if (-not $content.Contains($contractReference)) {
        Add-ValidationError "$relativePath`: missing shared development workflow reference"
    }

    foreach ($invariantId in $requiredInvariantIds[$skillName]) {
        if (-not $content.Contains("<!-- workflow-invariant: $invariantId -->")) {
            Add-ValidationError "$relativePath`: missing workflow invariant marker '$invariantId'"
        }
    }
}

foreach ($skillFile in Get-ChildItem -LiteralPath (Get-RepoPath -RelativePath "skills") -Directory -Filter "codex-*") {
    $skillPath = Join-Path $skillFile.FullName "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillPath -PathType Leaf)) {
        continue
    }

    $content = Get-Content -LiteralPath $skillPath -Raw
    foreach ($match in [regex]::Matches($content, "``(?<name>codex-[a-z0-9-]+)``")) {
        $referencedName = $match.Groups["name"].Value
        $referencedPath = Get-RepoPath -RelativePath "skills/$referencedName/SKILL.md"
        if (-not (Test-Path -LiteralPath $referencedPath -PathType Leaf)) {
            Add-ValidationError "skills/$($skillFile.Name)/SKILL.md`: references missing skill '$referencedName'"
        }
    }
}

if ($skillContents.ContainsKey("codex-debug-discipline")) {
    $debugContent = $skillContents["codex-debug-discipline"]
    if ($debugContent -match "(?mi)^\s*\d+\.\s+(Make the smallest fix|Fix the cause)\.?\s*$") {
        Add-ValidationError "skills/codex-debug-discipline/SKILL.md`: debug loop directly owns a durable fix"
    }
}

if ($skillContents.ContainsKey("codex-ui-quality-gate")) {
    $uiContent = $skillContents["codex-ui-quality-gate"]
    if ($uiContent.Contains("Fix issues found during the check")) {
        Add-ValidationError "skills/codex-ui-quality-gate/SKILL.md`: UI verifier still directly owns fixes"
    }
}

if ($skillContents.ContainsKey("codex-pr-readiness")) {
    $prContent = $skillContents["codex-pr-readiness"]
    foreach ($readiness in @("ready", "conditionally-ready", "not-ready")) {
        if (-not $prContent.Contains("``$readiness``")) {
            Add-ValidationError "skills/codex-pr-readiness/SKILL.md`: missing readiness state '$readiness'"
        }
    }
}

$copilotInstallerContent = Read-RequiredFile -RelativePath "scripts/install-copilot-skills.ps1"
$readmeContent = Read-RequiredFile -RelativePath "README.md"
if ($null -ne $copilotInstallerContent -and $null -ne $readmeContent) {
    $defaultBlock = [regex]::Match($copilotInstallerContent, '(?s)\$DefaultCopilotSkillNames\s*=\s*@\((?<body>.*?)\)')
    if (-not $defaultBlock.Success) {
        Add-ValidationError "scripts/install-copilot-skills.ps1`: cannot find default skill list"
    }
    else {
        foreach ($nameMatch in [regex]::Matches($defaultBlock.Groups["body"].Value, '"(?<name>codex-[a-z0-9-]+)"')) {
            $shortName = $nameMatch.Groups["name"].Value.Substring("codex-".Length)
            if (-not $readmeContent.Contains("``$shortName``")) {
                Add-ValidationError "README.md`: missing Copilot default skill '$shortName'"
            }
        }
    }
}

$jaRoot = Get-RepoPath -RelativePath "docs/ja"
if (Test-Path -LiteralPath $jaRoot -PathType Container) {
    foreach ($doc in Get-ChildItem -LiteralPath $jaRoot -Recurse -File -Filter "*.md") {
        $content = Get-Content -LiteralPath $doc.FullName -Raw
        $sourceMatch = [regex]::Match($content, "(?m)^source:\s*(?<path>.+?)\s*$")
        if (-not $sourceMatch.Success) {
            continue
        }

        $sourceRelativePath = $sourceMatch.Groups["path"].Value.Trim()
        if (-not (Test-Path -LiteralPath (Get-RepoPath -RelativePath $sourceRelativePath) -PathType Leaf)) {
            $docRelativePath = [System.IO.Path]::GetRelativePath($RepoRoot, $doc.FullName).Replace("\", "/")
            Add-ValidationError "$docRelativePath`: source path does not exist: $sourceRelativePath"
        }
    }
}

foreach ($requiredJaDoc in @(
    "docs/ja/rules/development-workflow.md",
    "docs/ja/AGENTS.md"
)) {
    if (-not (Test-Path -LiteralPath (Get-RepoPath -RelativePath $requiredJaDoc) -PathType Leaf)) {
        Add-ValidationError "$requiredJaDoc`: missing Japanese reference document"
    }
}

if ($errors.Count -gt 0) {
    foreach ($message in $errors) {
        Write-Error $message -ErrorAction Continue
    }
    throw "Development workflow validation failed with $($errors.Count) error(s)."
}

Write-Host "Development workflow validation passed for $($coreSkillNames.Count) core skills."
