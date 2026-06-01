[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CodexHome = (Join-Path $HOME ".codex")
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

function Copy-ManagedItem {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Missing source: $Source"
    }

    $destinationParent = Split-Path -Parent $Destination
    if ($destinationParent -and -not (Test-Path -LiteralPath $destinationParent)) {
        if ($PSCmdlet.ShouldProcess($destinationParent, "Create directory")) {
            New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($Destination, "Copy from $Source")) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
}

$managedDirectories = @(
    "rules",
    "templates"
)

if (-not (Test-Path -LiteralPath $CodexHome)) {
    if ($PSCmdlet.ShouldProcess($CodexHome, "Create Codex home")) {
        New-Item -ItemType Directory -Path $CodexHome -Force | Out-Null
    }
}

Copy-ManagedItem `
    -Source (Join-Path $RepoRoot "AGENTS.md") `
    -Destination (Join-Path $CodexHome "AGENTS.md")

foreach ($directory in $managedDirectories) {
    Copy-ManagedItem `
        -Source (Join-Path $RepoRoot $directory) `
        -Destination (Join-Path $CodexHome $directory)
}

$sourceSkills = Join-Path $RepoRoot "skills"
$targetSkills = Join-Path $CodexHome "skills"

if (-not (Test-Path -LiteralPath $targetSkills)) {
    if ($PSCmdlet.ShouldProcess($targetSkills, "Create skills directory")) {
        New-Item -ItemType Directory -Path $targetSkills -Force | Out-Null
    }
}

Get-ChildItem -Path $sourceSkills -Directory -Filter "codex-*" | ForEach-Object {
    Copy-ManagedItem `
        -Source $_.FullName `
        -Destination (Join-Path $targetSkills $_.Name)
}

Write-Host "Installed Codex config to $CodexHome"
