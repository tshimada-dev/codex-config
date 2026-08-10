[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

$expectedSandboxModes = [ordered]@{
    "config/config.base.toml" = "workspace-write"
    "config/profiles/safe.config.toml" = "read-only"
    "config/profiles/local-check.config.toml" = "workspace-write"
    "config/profiles/workspace.config.toml" = "workspace-write"
}

function Assert-ConfigValue {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Key,
        [Parameter(Mandatory = $true)][string]$ExpectedValue
    )

    $pattern = "^\s*$([regex]::Escape($Key))\s*=\s*`"$([regex]::Escape($ExpectedValue))`"\s*$"
    $matches = @($Lines | Where-Object { $_ -match $pattern })
    if ($matches.Count -ne 1) {
        throw "Expected exactly one '$Key = `"$ExpectedValue`"' entry in $Path, found $($matches.Count)."
    }
}

foreach ($entry in $expectedSandboxModes.GetEnumerator()) {
    $relativePath = $entry.Key
    $path = Join-Path $RepoRoot $relativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing config template: $relativePath"
    }

    $lines = @(Get-Content -LiteralPath $path)
    Assert-ConfigValue -Lines $lines -Path $relativePath -Key "approval_policy" -ExpectedValue "on-request"
    Assert-ConfigValue -Lines $lines -Path $relativePath -Key "approvals_reviewer" -ExpectedValue "auto_review"
    Assert-ConfigValue -Lines $lines -Path $relativePath -Key "sandbox_mode" -ExpectedValue $entry.Value

    if ($lines -match '^\s*sandbox_mode\s*=\s*"danger-full-access"\s*$') {
        throw "Auto-review config must retain a sandbox boundary: $relativePath"
    }
}

Write-Host "Auto-review config regression tests passed."
