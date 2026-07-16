[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [switch]$Execute,
    [Parameter(Mandatory = $true)]
    [string]$CodexHome,
    [Parameter(Mandatory = $true)]
    [string]$BaselinePlan,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [Parameter(Mandatory = $true)]
    [string]$Cutoff,
    [string]$CleanupScript = (Join-Path $PSScriptRoot 'cleanup_stale_codex_sessions.py'),
    [string]$StatusPath = ($BaselinePlan + '.status.txt'),
    [string]$RunnerLog = ($BaselinePlan + '.runner.log'),
    [int]$WaitHours = 12
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Execute) {
    throw 'The explicit -Execute switch is required.'
}
if (-not (Test-Path -LiteralPath $BaselinePlan -PathType Leaf)) {
    throw "Baseline plan not found: $BaselinePlan"
}
if (Test-Path -LiteralPath $OutputDir) {
    throw "Output already exists; refusing a duplicate run: $OutputDir"
}
$Python = (Get-Command python -ErrorAction Stop).Source

function Write-Status {
    param([string]$Message)
    $line = '{0} {1}' -f (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz'), $Message
    [System.IO.File]::WriteAllText($StatusPath, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Get-CodexAppProcesses {
    @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessName -in @('ChatGPT', 'codex', 'codex-code-mode-host')
    })
}

$deadline = (Get-Date).AddHours($WaitHours)
while ($true) {
    $running = @(Get-CodexAppProcesses)
    if ($running.Count -eq 0) { break }
    if ((Get-Date) -ge $deadline) {
        throw "Timed out waiting $WaitHours hours for the Codex app to exit."
    }
    Write-Status ("waiting-for-app-exit process_count={0}" -f $running.Count)
    Start-Sleep -Seconds 2
}

Write-Status 'app-exited; allowing file handles to settle'
Start-Sleep -Seconds 3
if (@(Get-CodexAppProcesses).Count -ne 0) {
    throw 'Codex restarted while cleanup was preparing; no changes were made.'
}

Write-Status 'cleanup-started'
& $Python $CleanupScript --root $CodexHome --cutoff $Cutoff --execute --ack-app-stopped --baseline $BaselinePlan --output-dir $OutputDir *> $RunnerLog
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Status ("cleanup-failed exit_code={0}" -f $exitCode)
    exit $exitCode
}
Write-Status 'cleanup-succeeded; quarantine retained pending post-restart verification'
exit 0
