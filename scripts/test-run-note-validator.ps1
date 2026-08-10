[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$Validator = Join-Path $ScriptDir "validate-run-note.ps1"
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-run-note-validator-" + [guid]::NewGuid().ToString("N"))

function Set-Utf8NoBomContent {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Value
    )

    [System.IO.File]::WriteAllText($Path, $Value, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-ValidatorCase {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Content,
        [Parameter(Mandatory = $true)][bool]$ShouldPass,
        [string]$ExpectedCode
    )

    $path = Join-Path $TempRoot "$Name.md"
    Set-Utf8NoBomContent -Path $path -Value $Content

    $output = @(& pwsh -NoProfile -File $Validator -Path $path 2>&1)
    $exitCode = $LASTEXITCODE
    if ($ShouldPass -and $exitCode -ne 0) {
        throw "${Name}: expected validator success, got exit $exitCode`n$($output -join "`n")"
    }
    if (-not $ShouldPass -and $exitCode -eq 0) {
        throw "${Name}: expected validator failure"
    }
    if ($ExpectedCode -and ($output -join "`n") -notmatch [regex]::Escape($ExpectedCode)) {
        throw "${Name}: expected diagnostic $ExpectedCode`n$($output -join "`n")"
    }
}

$validNote = @'
# Agent Run: valid-note

Location: `$HOME\.codex\runs\sample\20260728-1600-valid-note.md`
Started: `2026-07-28 16:00 +09:00`
Last updated: `2026-07-28 16:10 +09:00`
Phase: `readiness`

## Goal

Keep a structurally valid run note.

## Scope

- In scope: validator regression.
- Out of scope: unrelated changes.

## Expected Outcome and Evidence

| ID | Acceptance criterion | Evidence | Status |
| --- | --- | --- | --- |
| AC1 | The validator accepts this note. | Focused test. | passed |

- Non-goals and constraints: none.
- Open decisions or authority conflicts: none.

## Skills Used

| Skill | Purpose | Observable effect | Evidence |
| --- | --- | --- | --- |
| `codex-implementation` | Exercise the implementation contract. | Added focused regression evidence. | This test. |

## Research

- The validator has a deterministic seam.

## Decisions

- Keep the fixture minimal.

## Implementation Plan

- Run the validator.

## Changes

- Added a fixture.

## Verification

- Implementation feedback: passed.
- Format: passed.
- Lint: passed.
- Typecheck: not applicable.
- Test: passed.
- Build: not applicable.
- CI: local equivalent passed.
- Readiness: `ready`
- Residual risk or skipped optional evidence: none.

## Current State

- Complete.

## Handoff

- None.

## Next Step

- None.
'@

$validNoteLf = $validNote -replace "`r`n", "`n"
$validNoteCrLf = $validNoteLf -replace "`n", "`r`n"

try {
    if (-not (Test-Path -LiteralPath $Validator -PathType Leaf)) {
        throw "Validator is missing: $Validator"
    }

    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null

    Invoke-ValidatorCase -Name "valid-lf" -Content $validNoteLf -ShouldPass $true
    Invoke-ValidatorCase -Name "valid-crlf" -Content $validNoteCrLf -ShouldPass $true
    Invoke-ValidatorCase -Name "invalid-phase" -Content ($validNote -replace 'Phase: `readiness`', 'Phase: `research`') -ShouldPass $false -ExpectedCode "RUN003"
    Invoke-ValidatorCase -Name "placeholder" -Content ($validNote -replace 'valid-note', '<task-name>') -ShouldPass $false -ExpectedCode "RUN004"
    Invoke-ValidatorCase -Name "escaped-newline" -Content ($validNote -replace '- Test: passed\.', '- Test: passed.\n\n- Build: passed.') -ShouldPass $false -ExpectedCode "RUN005"
    Invoke-ValidatorCase -Name "missing-skills" -Content ($validNote -replace '(?s)## Skills Used.*?(?=## Research)', '') -ShouldPass $false -ExpectedCode "RUN006"
    Invoke-ValidatorCase -Name "pending-ac-ready" -Content ($validNote -replace '\| AC1 \| The validator accepts this note\. \| Focused test\. \| passed \|', '| AC1 | The validator accepts this note. | Focused test. | pending |') -ShouldPass $false -ExpectedCode "RUN009"
    Invoke-ValidatorCase -Name "pending-check-ready" -Content ($validNote -replace '- Test: passed\.', '- Test: pending.') -ShouldPass $false -ExpectedCode "RUN010"
    $conditionalNote = (($validNote -replace '- Readiness: `ready`', '- Readiness: `conditionally-ready`') -replace '- Test: passed\.', '- Test: pending.') -replace '- Residual risk or skipped optional evidence: none\.', '- Residual risk or skipped optional evidence: remote CI remains pending.'
    Invoke-ValidatorCase -Name "conditional-with-risk" -Content $conditionalNote -ShouldPass $true
    Invoke-ValidatorCase -Name "conditional-without-risk" -Content ($conditionalNote -replace '- Residual risk or skipped optional evidence: remote CI remains pending\.', '- Residual risk or skipped optional evidence:') -ShouldPass $false -ExpectedCode "RUN011"

    Write-Host "Run-note validator regression tests passed."
}
finally {
    $tempFullPath = [System.IO.Path]::GetFullPath($TempRoot)
    $systemTemp = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $tempPrefix = $systemTemp + [System.IO.Path]::DirectorySeparatorChar
    if (-not $tempFullPath.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove test directory outside the temp root: $tempFullPath"
    }
    if (Test-Path -LiteralPath $tempFullPath) {
        Remove-Item -LiteralPath $tempFullPath -Recurse -Force
    }
}
