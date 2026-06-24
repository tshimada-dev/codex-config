[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$CopilotInstructionsHome,

    [string]$VSCodeUserSettingsPath,

    [switch]$ApplyVSCodeSettings,

    [switch]$AllowJsoncRewrite,

    [switch]$OverwriteInstruction,

    [switch]$Backup
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir
$GuardrailsRoot = Join-Path $RepoRoot "config\copilot\guardrails"
$InstructionSource = Join-Path $GuardrailsRoot "copilot-destructive-ops.instructions.md"
$SettingsSource = Join-Path $GuardrailsRoot "vscode-settings.json"

if (-not $CopilotInstructionsHome) {
    $CopilotInstructionsHome = Join-Path $HOME ".copilot\instructions"
}

if (-not $VSCodeUserSettingsPath) {
    if ($IsWindows -or $env:APPDATA) {
        $VSCodeUserSettingsPath = Join-Path $env:APPDATA "Code\User\settings.json"
    }
    elseif ($IsMacOS) {
        $VSCodeUserSettingsPath = Join-Path $HOME "Library/Application Support/Code/User/settings.json"
    }
    else {
        $VSCodeUserSettingsPath = Join-Path $HOME ".config/Code/User/settings.json"
    }
}

if ($Backup -and -not ($OverwriteInstruction -or $ApplyVSCodeSettings)) {
    throw "-Backup can only be used with -OverwriteInstruction or -ApplyVSCodeSettings."
}

function Test-SameFileContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Left,

        [Parameter(Mandatory = $true)]
        [string]$Right
    )

    return (Get-FileHash -LiteralPath $Left).Hash -eq (Get-FileHash -LiteralPath $Right).Hash
}

function Copy-WithGuard {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination,

        [Parameter(Mandatory = $true)]
        [bool]$Overwrite
    )

    $destinationExists = Test-Path -LiteralPath $Destination
    if ($destinationExists) {
        if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
            throw "Destination exists and is not a file: $Destination"
        }

        if (Test-SameFileContent -Left $Source -Right $Destination) {
            Write-Host "Unchanged: $Destination"
            return
        }

        if (-not $Overwrite) {
            throw "Refusing to overwrite existing file with different content: $Destination. Re-run with -OverwriteInstruction to replace it."
        }

        if ($Backup) {
            $backupPath = "$Destination.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            if ($PSCmdlet.ShouldProcess($backupPath, "Back up existing instruction")) {
                Copy-Item -LiteralPath $Destination -Destination $backupPath -Force
            }
        }
    }

    $parent = Split-Path -Parent $Destination
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        if ($PSCmdlet.ShouldProcess($parent, "Create directory")) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    if ($PSCmdlet.ShouldProcess($Destination, "Install Copilot guardrail instruction")) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }
}

function ConvertFrom-JsonCFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [ordered]@{}
    }

    $content = Get-Content -LiteralPath $Path -Raw
    if (-not $content.Trim()) {
        return [ordered]@{}
    }

    $options = [System.Text.Json.JsonDocumentOptions]::new()
    $options.CommentHandling = [System.Text.Json.JsonCommentHandling]::Skip
    $options.AllowTrailingCommas = $true

    try {
        $document = [System.Text.Json.JsonDocument]::Parse($content, $options)
    }
    catch {
        throw "Could not parse VS Code settings as JSON/JSONC: $Path. Fix the file or pass a different -VSCodeUserSettingsPath."
    }

    try {
        return ConvertFrom-JsonElement -Element $document.RootElement
    }
    finally {
        $document.Dispose()
    }
}

function Test-JsoncComment {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    $inString = $false
    $escaped = $false
    for ($i = 0; $i -lt $Content.Length - 1; $i++) {
        $char = $Content[$i]
        if ($inString) {
            if ($escaped) {
                $escaped = $false
                continue
            }
            if ($char -eq "\") {
                $escaped = $true
                continue
            }
            if ($char -eq '"') {
                $inString = $false
            }
            continue
        }

        if ($char -eq '"') {
            $inString = $true
            continue
        }

        if ($char -eq "/" -and ($Content[$i + 1] -eq "/" -or $Content[$i + 1] -eq "*")) {
            return $true
        }
    }

    return $false
}

function ConvertFrom-JsonElement {
    param(
        [Parameter(Mandatory = $true)]
        [System.Text.Json.JsonElement]$Element
    )

    switch ($Element.ValueKind) {
        "Object" {
            $result = [ordered]@{}
            foreach ($property in $Element.EnumerateObject()) {
                $result[$property.Name] = ConvertFrom-JsonElement -Element $property.Value
            }
            return $result
        }
        "Array" {
            $items = @()
            foreach ($item in $Element.EnumerateArray()) {
                $items += ConvertFrom-JsonElement -Element $item
            }
            return $items
        }
        "String" { return $Element.GetString() }
        "Number" {
            $number = 0L
            if ($Element.TryGetInt64([ref]$number)) {
                return $number
            }
            return $Element.GetDouble()
        }
        "True" { return $true }
        "False" { return $false }
        "Null" { return $null }
        default { throw "Unsupported JSON value kind: $($Element.ValueKind)" }
    }
}

function Merge-Hashtable {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Target,

        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Patch
    )

    foreach ($key in $Patch.Keys) {
        if ($Target.Contains($key) -and $Target[$key] -is [System.Collections.IDictionary] -and $Patch[$key] -is [System.Collections.IDictionary]) {
            Merge-Hashtable -Target $Target[$key] -Patch $Patch[$key]
            continue
        }

        $Target[$key] = $Patch[$key]
    }
}

function ConvertTo-PlainObject {
    param(
        $Value
    )

    if ($null -eq $Value) {
        return $null
    }

    if ($Value -is [System.Collections.IDictionary]) {
        $object = [ordered]@{}
        foreach ($key in $Value.Keys) {
            $object[$key] = ConvertTo-PlainObject -Value $Value[$key]
        }
        return $object
    }

    if ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        return @($Value | ForEach-Object { ConvertTo-PlainObject -Value $_ })
    }

    return $Value
}

function Merge-VSCodeSettings {
    $template = ConvertFrom-JsonCFile -Path $SettingsSource
    $settingsContent = ""
    if (Test-Path -LiteralPath $VSCodeUserSettingsPath -PathType Leaf) {
        $settingsContent = Get-Content -LiteralPath $VSCodeUserSettingsPath -Raw
    }
    if ($settingsContent -and (Test-JsoncComment -Content $settingsContent) -and -not $AllowJsoncRewrite) {
        throw "VS Code settings contain JSONC comments. Merging would rewrite settings.json as plain JSON and remove comments. Re-run with -AllowJsoncRewrite if you accept that, or copy settings from config/copilot/guardrails/vscode-settings.json manually."
    }

    $settings = ConvertFrom-JsonCFile -Path $VSCodeUserSettingsPath
    Merge-Hashtable -Target $settings -Patch $template

    $parent = Split-Path -Parent $VSCodeUserSettingsPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        if ($PSCmdlet.ShouldProcess($parent, "Create VS Code user settings directory")) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
    }

    if ((Test-Path -LiteralPath $VSCodeUserSettingsPath -PathType Leaf) -and $Backup) {
        $backupPath = "$VSCodeUserSettingsPath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        if ($PSCmdlet.ShouldProcess($backupPath, "Back up VS Code user settings")) {
            Copy-Item -LiteralPath $VSCodeUserSettingsPath -Destination $backupPath -Force
        }
    }

    $json = ConvertTo-PlainObject -Value $settings | ConvertTo-Json -Depth 20
    if ($PSCmdlet.ShouldProcess($VSCodeUserSettingsPath, "Merge Copilot guardrail settings")) {
        Set-Content -LiteralPath $VSCodeUserSettingsPath -Value $json -Encoding utf8NoBOM
    }
}

if (-not (Test-Path -LiteralPath $InstructionSource -PathType Leaf)) {
    throw "Missing guardrail instruction template: $InstructionSource"
}
if ($ApplyVSCodeSettings -and -not (Test-Path -LiteralPath $SettingsSource -PathType Leaf)) {
    throw "Missing VS Code settings template: $SettingsSource"
}

$instructionDestination = Join-Path $CopilotInstructionsHome "codex-config\copilot-destructive-ops.instructions.md"
Copy-WithGuard -Source $InstructionSource -Destination $instructionDestination -Overwrite ([bool]$OverwriteInstruction)

if ($ApplyVSCodeSettings) {
    Merge-VSCodeSettings
}
else {
    Write-Host "Skipped VS Code settings merge. Re-run with -ApplyVSCodeSettings to apply terminal approval guardrails."
}

Write-Host "Installed Copilot guardrail instruction to $instructionDestination"
if ($ApplyVSCodeSettings) {
    Write-Host "Merged Copilot guardrail settings into $VSCodeUserSettingsPath"
}
