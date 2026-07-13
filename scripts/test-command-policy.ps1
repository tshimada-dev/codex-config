[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$RulesPath = Join-Path $RepoRoot "rules/command-policy.rules"

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "The Codex CLI is required to validate command-policy.rules with execpolicy."
}

function Assert-ExecPolicyDecision {
    param(
        [Parameter(Mandatory = $true)][string[]]$Command,
        [Parameter(Mandatory = $true)][ValidateSet("allow", "prompt", "forbidden")][string]$Expected
    )

    $output = & codex execpolicy check --pretty --rules $RulesPath -- @Command
    if ($LASTEXITCODE -ne 0) {
        throw "execpolicy failed for '$($Command -join ' ')' with exit code $LASTEXITCODE."
    }

    $result = $output | ConvertFrom-Json
    if ($result.decision -ne $Expected) {
        throw "Expected '$Expected' for '$($Command -join ' ')', got '$($result.decision)'."
    }
}

foreach ($command in @(
    , @("npm", "run", "build")
    , @("npm", "run", "lint")
    , @("npm", "run", "typecheck")
    , @("npm", "test")
    , @("uv", "run", "pytest")
    , @("uv", "run", "ruff", "check")
    , @("uv", "run", "mypy")
    , @("rg", "--pre", "pwsh", "workflow")
    , @("git", "diff", "--ext-diff")
    , @("git", "log", "-p", "--ext-diff")
    , @("git", "show", "--ext-diff")
    , @("pnpm", "test")
    , @("yarn", "test")
    , @("make", "test")
    , @("cargo", "test")
    , @("go", "test", "./...")
    , @("dotnet", "test")
    , @("mvn", "test")
    , @("gradlew", "test")
    , @("npx", "vitest")
)) {
    Assert-ExecPolicyDecision -Command $command -Expected "prompt"
}

foreach ($command in @(
    , @("git", "status")
)) {
    Assert-ExecPolicyDecision -Command $command -Expected "allow"
}

Assert-ExecPolicyDecision -Command @("git", "clean", "-fd") -Expected "prompt"
Assert-ExecPolicyDecision -Command @("git", "clean", "-n") -Expected "prompt"
Assert-ExecPolicyDecision -Command @("git", "restore", "--staged", "README.md") -Expected "prompt"

Write-Host "Command policy regression tests passed."
