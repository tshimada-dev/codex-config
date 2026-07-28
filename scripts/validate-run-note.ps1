[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = "Stop"

$allowedPhases = @(
    "intake", "scouting", "planning", "debugging", "implementation",
    "verification", "readiness", "paused", "handoff"
)
$requiredSections = @(
    "Goal",
    "Scope",
    "Expected Outcome and Evidence",
    "Skills Used",
    "Verification",
    "Current State",
    "Handoff",
    "Next Step"
)
$errors = [System.Collections.Generic.List[string]]::new()

function Add-RunNoteError {
    param(
        [Parameter(Mandatory = $true)][string]$Code,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Message
    )

    $errors.Add("${Code} ${RelativePath}: $Message")
}

function Get-SectionBody {
    param(
        [Parameter(Mandatory = $true)][string]$Content,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $match = [regex]::Match(
        $Content,
        "(?ms)^## $([regex]::Escape($Heading))\s*\r?\n(?<body>.*?)(?=^## |\z)"
    )
    if (-not $match.Success) {
        return $null
    }

    return $match.Groups["body"].Value.Trim()
}

$resolvedPath = Resolve-Path -LiteralPath $Path -ErrorAction Stop
$target = Get-Item -LiteralPath $resolvedPath.Path -Force
if ($target.PSIsContainer) {
    $files = @(Get-ChildItem -LiteralPath $target.FullName -Recurse -File -Filter "*.md")
    $displayRoot = $target.FullName
}
else {
    $files = @($target)
    $displayRoot = Split-Path -Parent $target.FullName
}

if ($files.Count -eq 0) {
    throw "No Markdown files found under $($target.FullName)"
}

$validated = 0
foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    $relativePath = [System.IO.Path]::GetRelativePath($displayRoot, $file.FullName)
    if ($files.Count -eq 1) {
        $relativePath = $file.Name
    }

    if ($content -notmatch '(?m)^# Agent Run:\s*\S') {
        if (-not $target.PSIsContainer) {
            Add-RunNoteError -Code "RUN001" -RelativePath $relativePath -Message "missing '# Agent Run:' title"
        }
        continue
    }
    $validated++

    $phaseMatches = [regex]::Matches($content, '(?m)^Phase:\s*`?(?<phase>[^`\r\n]+)`?\s*$')
    if ($phaseMatches.Count -ne 1) {
        Add-RunNoteError -Code "RUN002" -RelativePath $relativePath -Message "expected exactly one parseable Phase line"
    }
    elseif ($phaseMatches[0].Groups["phase"].Value.Trim() -notin $allowedPhases) {
        Add-RunNoteError -Code "RUN003" -RelativePath $relativePath -Message "Phase must be one of: $($allowedPhases -join ', ')"
    }

    if ($content -match '<[^>\r\n]+>') {
        Add-RunNoteError -Code "RUN004" -RelativePath $relativePath -Message "contains an unresolved angle-bracket placeholder"
    }
    if ($content -match '\\n\\n') {
        Add-RunNoteError -Code "RUN005" -RelativePath $relativePath -Message "contains literal escaped paragraph breaks"
    }

    foreach ($heading in $requiredSections) {
        $sectionBody = Get-SectionBody -Content $content -Heading $heading
        if ($null -eq $sectionBody) {
            $code = if ($heading -eq "Skills Used") { "RUN006" } else { "RUN012" }
            Add-RunNoteError -Code $code -RelativePath $relativePath -Message "missing required section '## $heading'"
            continue
        }
        if (-not $sectionBody -or $sectionBody -eq "-") {
            Add-RunNoteError -Code "RUN014" -RelativePath $relativePath -Message "section '## $heading' has no resolved content"
        }
    }

    $skillsBody = Get-SectionBody -Content $content -Heading "Skills Used"
    if ($null -ne $skillsBody) {
        if ($skillsBody -notmatch '(?m)^\|\s*Skill\s*\|\s*Purpose\s*\|\s*Observable effect\s*\|\s*Evidence\s*\|\s*$') {
            Add-RunNoteError -Code "RUN007" -RelativePath $relativePath -Message "Skills Used table must contain Skill, Purpose, Observable effect, and Evidence columns"
        }

        $skillRows = @(
            [regex]::Matches($skillsBody, '(?m)^\|\s*`?(?<skill>[a-z0-9][a-z0-9.-]*|None)`?\s*\|') |
                Where-Object { $_.Groups["skill"].Value -notin @("Skill", "---") }
        )
        if ($skillRows.Count -eq 0) {
            Add-RunNoteError -Code "RUN008" -RelativePath $relativePath -Message "Skills Used must contain at least one applied skill or an explicit None row"
        }
    }

    $readinessMatches = [regex]::Matches(
        $content,
        '(?m)^-\s*Readiness:\s*`?(?<state>ready|conditionally-ready|not-ready)`?(?:[.;]\s*.*)?$'
    )
    if ($readinessMatches.Count -ne 1) {
        Add-RunNoteError -Code "RUN013" -RelativePath $relativePath -Message "expected exactly one readiness classification"
        continue
    }

    $readiness = $readinessMatches[0].Groups["state"].Value
    if ($readiness -eq "ready") {
        if ($content -match '(?mi)^\|[^|\r\n]+\|[^|\r\n]*\|[^|\r\n]*\|\s*(pending|partial|blocked|fail(?:ed)?)\s*\|\s*$') {
            Add-RunNoteError -Code "RUN009" -RelativePath $relativePath -Message "ready note contains an unresolved acceptance-criterion status"
        }
        if ($content -match '(?mi)^-\s*(Implementation feedback|Format|Lint|Typecheck|Test|Build|CI):\s*(pending|blocked|fail(?:ed)?)\b') {
            Add-RunNoteError -Code "RUN010" -RelativePath $relativePath -Message "ready note contains an unresolved verification field"
        }
    }
    elseif ($readiness -eq "conditionally-ready") {
        $riskMatch = [regex]::Match(
            $content,
            '(?mi)^-[ \t]*Residual risk or skipped optional evidence:[ \t]*(?<risk>.*)$'
        )
        $risk = if ($riskMatch.Success) { $riskMatch.Groups["risk"].Value.Trim() } else { "" }
        if (-not $risk -or $risk -match '^(none|n/?a)[.!]?$') {
            Add-RunNoteError -Code "RUN011" -RelativePath $relativePath -Message "conditionally-ready requires a concrete residual risk or skipped optional evidence"
        }
    }
}

if ($validated -eq 0 -and $target.PSIsContainer) {
    throw "No Agent Run notes found under $($target.FullName)"
}

if ($errors.Count -gt 0) {
    foreach ($message in $errors) {
        Write-Error $message -ErrorAction Continue
    }
    throw "Run-note validation failed with $($errors.Count) error(s)."
}

Write-Host "Run-note validation passed for $validated note(s)."
