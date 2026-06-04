[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CodexHome = (Join-Path $HOME ".codex"),

    [switch]$Overwrite,

    [switch]$Backup,

    [switch]$AcceptThirdPartySkillRisk,

    [string]$DevelopmentEstimationRef = "67056a9ee2277905166e2769fe91bb4e7104dc63",

    [string]$PlanEstimateEffortRef = "003d3acd0e5679bd41ce012aecd06b42b8b466f5",

    [string]$CostEstimateRef = "db8d8689b14ccc0ae63fe68e80d6342a4a4bb798"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$TargetSkills = Join-Path $CodexHome "skills"
$script:ProvenanceEntries = @()

if (-not $AcceptThirdPartySkillRisk) {
    throw "This installer downloads third-party skill instructions into Codex. Review the pinned source commits, then re-run with -AcceptThirdPartySkillRisk."
}

function Assert-PinnedCommitRef {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Ref
    )

    if ($Ref -notmatch "^[0-9a-fA-F]{40}$") {
        throw "$Name must be a pinned 40-character git commit SHA, not a branch, tag, or short ref: $Ref"
    }
}

Assert-PinnedCommitRef -Name "DevelopmentEstimationRef" -Ref $DevelopmentEstimationRef
Assert-PinnedCommitRef -Name "PlanEstimateEffortRef" -Ref $PlanEstimateEffortRef
Assert-PinnedCommitRef -Name "CostEstimateRef" -Ref $CostEstimateRef

function Get-TextSha256 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace "-", "").ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Assert-ChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Parent
    )

    $trimChars = [char[]]@(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd($trimChars)
    $fullParent = [System.IO.Path]::GetFullPath($Parent).TrimEnd($trimChars)
    $parentPrefix = $fullParent + [System.IO.Path]::DirectorySeparatorChar

    if ($fullPath -ne $fullParent -and -not $fullPath.StartsWith($parentPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside target skills directory: $Path"
    }
}

function Assert-SkillName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if ($Name -notmatch "^[a-z0-9][a-z0-9-]*$") {
        throw "Refusing unsafe skill name: $Name"
    }
}

function Assert-ThirdPartySkillMarkdown {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $blockedPatterns = @(
        @{ Pattern = "(?i)\bInvoke-Expression\b|\biex\b"; Reason = "PowerShell dynamic execution" },
        @{ Pattern = "(?i)\birm\b|\biwr\b|Invoke-WebRequest|curl|wget"; Reason = "network command instruction" },
        @{ Pattern = "(?i)Remove-Item\s+.*-Recurse|rm\s+-rf"; Reason = "recursive deletion instruction" },
        @{ Pattern = "(?i)\bgit\s+push\b|\bgh\s+(release|pr|repo|auth)\b"; Reason = "remote-changing GitHub instruction" },
        @{ Pattern = "(?i)\.env|private[_ -]?key|api[_ -]?key|token|password|secret|credential|cookie"; Reason = "secret-sensitive instruction" },
        @{ Pattern = "(?i)upload|exfiltrat|webhook"; Reason = "data egress instruction" }
    )

    $hits = @()
    foreach ($blocked in $blockedPatterns) {
        if ($Content -match $blocked.Pattern) {
            $hits += "$($blocked.Reason): $($blocked.Pattern)"
        }
    }

    if ($hits.Count -gt 0) {
        throw "Downloaded SKILL.md for $Name failed the third-party instruction audit: $($hits -join '; ')"
    }
}

function Get-UrlText {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    Write-Host "Downloading $Url"
    return (Invoke-WebRequest -Uri $Url -UseBasicParsing).Content
}

function Normalize-SkillMarkdown {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Markdown
    )

    if (-not $Markdown.StartsWith("---")) {
        return $Markdown
    }

    $lines = $Markdown -split "`r?`n"
    $endIndex = $null
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -eq "---") {
            $endIndex = $i
            break
        }
    }

    if ($null -eq $endIndex) {
        return $Markdown
    }

    $frontmatter = $lines[1..($endIndex - 1)] | Where-Object {
        $_ -match "^(name|description):"
    }
    $body = $lines[($endIndex + 1)..($lines.Count - 1)]

    return (@("---") + $frontmatter + @("---") + $body) -join "`n"
}

function Write-TextFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        if ($PSCmdlet.ShouldProcess($parent, "Create directory")) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($Path, "Write text file")) {
        Set-Content -LiteralPath $Path -Value $Content -Encoding utf8
    }
}

function Install-Skill {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [array]$Files
    )

    Assert-SkillName -Name $Name
    $target = Join-Path $TargetSkills $Name
    Assert-ChildPath -Path $target -Parent $TargetSkills

    if (Test-Path -LiteralPath $target) {
        if (-not $Overwrite) {
            Write-Host "Skipping existing skill $Name at $target. Use -Overwrite to replace it."
            return
        }

        if ($Backup) {
            $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $backupRoot = "${CodexHome}.estimation-skills-backup-$timestamp"
            $backupTarget = Join-Path (Join-Path $backupRoot "skills") $Name
            Assert-ChildPath -Path $backupTarget -Parent $backupRoot

            if ($PSCmdlet.ShouldProcess($backupTarget, "Back up existing skill $Name")) {
                New-Item -ItemType Directory -Path (Split-Path -Parent $backupTarget) -Force | Out-Null
                Copy-Item -LiteralPath $target -Destination $backupTarget -Recurse -Force
            }
        }

        if ($PSCmdlet.ShouldProcess($target, "Remove existing skill before reinstall")) {
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }

    foreach ($file in $Files) {
        $content = $null
        $downloadedHash = $null
        if ($file.ContainsKey("Url")) {
            $content = Get-UrlText -Url $file.Url
            $downloadedHash = Get-TextSha256 -Text $content
        }
        elseif ($file.ContainsKey("Content")) {
            $content = $file.Content
        }
        elseif ($file.ContainsKey("Source")) {
            $content = Get-Content -LiteralPath (Join-Path $RepoRoot $file.Source) -Raw
        }
        else {
            throw "File spec for $Name/$($file.Path) must include Url, Content, or Source."
        }

        if ($file.NormalizeSkillMarkdown) {
            $content = Normalize-SkillMarkdown -Markdown $content
        }

        if ($file.ContainsKey("AuditAsSkillMarkdown") -and $file.AuditAsSkillMarkdown) {
            Assert-ThirdPartySkillMarkdown -Name $Name -Content $content
        }

        if ($file.ContainsKey("Replace")) {
            foreach ($replacement in $file.Replace) {
                $content = $content.Replace($replacement.From, $replacement.To)
            }
        }

        Write-TextFile -Path (Join-Path $target $file.Path) -Content $content

        if ($file.ContainsKey("Url")) {
            $script:ProvenanceEntries += [ordered]@{
                skill = $Name
                path = $file.Path
                source_url = $file.Url
                downloaded_sha256 = $downloadedHash
                installed_sha256 = Get-TextSha256 -Text $content
                normalized_skill_markdown = [bool]$file.NormalizeSkillMarkdown
                audited_as_skill_markdown = [bool]$file.AuditAsSkillMarkdown
            }
        }
    }

    if ($WhatIfPreference) {
        Write-Host "Would install $Name to $target"
    }
    else {
        Write-Host "Installed $Name to $target"
    }
}

$developmentEstimateReference = @'
# Development Estimation Reference

Use this reference to create a structured, defensible estimate for a software feature, subsystem, or project.

## Workflow

1. Define scope, non-goals, source basis, estimate unit, and target audience.
2. Break the scope into WBS components small enough to explain.
3. Estimate low / likely / high effort for each component.
4. Identify assumptions, exclusions, risks, and what would materially change the estimate.
5. Summarize the recommended range and confidence.

## Default WBS Categories

- Requirements and business analysis
- Basic and detailed design
- Foundation and shared UX
- Data import/export and migration
- Business logic and calculations
- Integrations
- Reports, documents, spreadsheets, and PDF output
- Testing and acceptance support
- Training, manuals, deployment, handoff, and management

## Output Shape

Return a WBS table with low / likely / high person-days, plus assumptions, exclusions, risks, confidence, and validation notes.
'@

$dependencies = @(
    @{
        Name = "development-estimation"
        Files = @(
            @{
                Path = "SKILL.md"
                Url = "https://raw.githubusercontent.com/majiayu000/claude-skill-registry/$DevelopmentEstimationRef/skills/data/development-estimation/SKILL.md"
                NormalizeSkillMarkdown = $true
                AuditAsSkillMarkdown = $true
                Replace = @(
                    @{
                        From = "skills/development-estimation/references/estimate.md"
                        To = "references/estimate.md"
                    }
                )
            },
            @{
                Path = "references/estimate.md"
                Content = $developmentEstimateReference
            },
            @{
                Path = "agents/openai.yaml"
                Content = @'
interface:
  display_name: "Development Estimation"
  short_description: "Estimate feature effort with risk ranges."
  default_prompt: "Use this skill to estimate a feature or project with WBS breakdown, low/likely/high ranges, assumptions, risks, and confidence."
'@
            }
        )
    },
    @{
        Name = "plan-estimateeffort"
        Files = @(
            @{
                Path = "SKILL.md"
                Url = "https://raw.githubusercontent.com/zhongadamwang/AI_Slowcooker/$PlanEstimateEffortRef/.github/skills/plan-estimateeffort/SKILL.md"
                NormalizeSkillMarkdown = $true
                AuditAsSkillMarkdown = $true
            },
            @{
                Path = "agents/openai.yaml"
                Content = @'
interface:
  display_name: "Plan Estimate Effort"
  short_description: "Estimate tasks with PERT and risk factors."
  default_prompt: "Use this skill to estimate a decomposed task list with optimistic, most-likely, pessimistic, expected effort, confidence, and risk factors."
'@
            }
        )
    },
    @{
        Name = "cost-estimate"
        Files = @(
            @{
                Path = "SKILL.md"
                Url = "https://raw.githubusercontent.com/uwe-schwarz/skills/$CostEstimateRef/skills/cost-estimate/SKILL.md"
                NormalizeSkillMarkdown = $true
                AuditAsSkillMarkdown = $true
            },
            @{
                Path = "agents/openai.yaml"
                Content = @'
interface:
  display_name: "Cost Estimate"
  short_description: "Estimate rebuild cost and delivery effort."
  default_prompt: "Use this skill to estimate replacement cost, engineering effort, calendar time, and delivery maturity from repository facts. Keep measured facts separate from inference."
'@
            }
        )
    }
)

if (-not (Test-Path -LiteralPath $CodexHome)) {
    if ($PSCmdlet.ShouldProcess($CodexHome, "Create Codex home")) {
        New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
    }
}

if (-not (Test-Path -LiteralPath $TargetSkills)) {
    if ($PSCmdlet.ShouldProcess($TargetSkills, "Create skills directory")) {
        New-Item -ItemType Directory -Path $TargetSkills -Force | Out-Null
    }
}

foreach ($dependency in $dependencies) {
    Install-Skill -Name $dependency.Name -Files $dependency.Files
}

if ($script:ProvenanceEntries.Count -gt 0) {
    $provenancePath = Join-Path $TargetSkills ".codex-estimation-skill-dependencies.json"
    $manifest = [ordered]@{
        schema_version = 1
        tool = "install-estimation-skills.ps1"
        installed_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        third_party_skill_risk_accepted = [bool]$AcceptThirdPartySkillRisk
        refs = [ordered]@{
            development_estimation = $DevelopmentEstimationRef
            plan_estimateeffort = $PlanEstimateEffortRef
            cost_estimate = $CostEstimateRef
        }
        entries = @($script:ProvenanceEntries)
    }

    if ($PSCmdlet.ShouldProcess($provenancePath, "Write third-party estimation skill provenance manifest")) {
        Set-Content -LiteralPath $provenancePath -Value ($manifest | ConvertTo-Json -Depth 6) -Encoding utf8
    }
}

if ($WhatIfPreference) {
    Write-Host "Would install estimation skill dependencies to $TargetSkills"
}
else {
    Write-Host "Installed estimation skill dependencies to $TargetSkills"
}
