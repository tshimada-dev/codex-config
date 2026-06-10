param(
    [Parameter(Mandatory = $true)]
    [string] $Script,

    [string] $Distro = "",

    [string] $WorkingDirectory = ""
)

$ErrorActionPreference = "Stop"

function ConvertTo-WslPath {
    param([Parameter(Mandatory = $true)][string] $WindowsPath)

    $full = [System.IO.Path]::GetFullPath($WindowsPath)
    if ($full -notmatch "^[A-Za-z]:\\") {
        throw "Only drive-letter paths are supported: $full"
    }

    $drive = $full.Substring(0, 1).ToLowerInvariant()
    $rest = $full.Substring(2).Replace("\", "/")
    return "/mnt/$drive$rest"
}

function ConvertTo-BashSingleQuotedString {
    param([Parameter(Mandatory = $true)][string] $Value)

    return "'" + $Value.Replace("'", "'\''") + "'"
}

$tmp = [System.IO.Path]::GetTempFileName()

try {
    $body = $Script.Replace("`r`n", "`n").Replace("`r", "`n")
    if ($WorkingDirectory -ne "") {
        $quotedWorkingDirectory = ConvertTo-BashSingleQuotedString -Value $WorkingDirectory
        $body = "cd -- $quotedWorkingDirectory" + "`n" + $body
    }

    [System.IO.File]::WriteAllText(
        $tmp,
        $body,
        [System.Text.UTF8Encoding]::new($false)
    )

    $wslPath = ConvertTo-WslPath -WindowsPath $tmp
    $arguments = @()
    if ($Distro -ne "") {
        $arguments += @("-d", $Distro)
    }
    $arguments += @("bash", $wslPath)

    & wsl @arguments
    exit $LASTEXITCODE
}
finally {
    Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}
