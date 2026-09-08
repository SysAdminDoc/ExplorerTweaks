#requires -Version 7
[CmdletBinding()]
param([string]$Python = 'python', [switch]$ExecutableOnly)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
Push-Location $repo
try {
    foreach ($name in '.build-venv', 'build', 'dist') {
        $path = [IO.Path]::GetFullPath((Join-Path $repo $name))
        if ([IO.Path]::GetDirectoryName($path) -ne $repo) { throw 'Unexpected build cleanup path.' }
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
    }
    & $Python -m venv .build-venv
    if ($LASTEXITCODE -ne 0) { throw 'Build environment creation failed.' }
    $buildPython = Join-Path $repo '.build-venv/Scripts/python.exe'
    & $buildPython -m pip install --requirement requirements.txt --disable-pip-version-check
    if ($LASTEXITCODE -ne 0) { throw 'Pinned dependency installation failed.' }
    & $buildPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
    & $buildPython create_icon.py
    if ($LASTEXITCODE -ne 0) { throw 'Approved artwork export failed.' }
    & $buildPython -m unittest discover -s tests -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    & $buildPython -m compileall -q explorer_tweaks.py create_icon.py tools tests
    if ($LASTEXITCODE -ne 0) { throw 'Compilation failed.' }
    & $buildPython tools/package_release.py --provenance
    if ($LASTEXITCODE -ne 0) { throw 'Version or provenance validation failed.' }
    & $buildPython -m PyInstaller --noconfirm --clean ExplorerTweaks.spec
    if ($LASTEXITCODE -ne 0) { throw 'Executable build failed.' }
    $certificate = Get-ChildItem Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.HasPrivateKey -and $_.NotAfter -gt (Get-Date) } | Sort-Object NotAfter -Descending | Select-Object -First 1
    if ($certificate) {
        $signature = Set-AuthenticodeSignature -FilePath dist/ExplorerTweaks.exe -Certificate $certificate -TimestampServer 'http://timestamp.digicert.com'
        if ($signature.Status -ne 'Valid') { throw "Signing failed: $($signature.Status)" }
    } else { Write-Warning 'No code-signing certificate found. The executable is unsigned.' }
    $version = (Get-Content explorer_tweaks.py | Select-String '^APP_VERSION = "([0-9.]+)"$').Matches.Groups[1].Value
    $fileVersion = (Get-Item dist/ExplorerTweaks.exe).VersionInfo
    if ($fileVersion.FileVersion -ne "$version.0" -or $fileVersion.ProductVersion -ne "$version.0" -or "$($fileVersion.FileMajorPart).$($fileVersion.FileMinorPart).$($fileVersion.FileBuildPart)" -ne $version) { throw 'Executable version fields differ.' }
    if (-not $ExecutableOnly) {
        & $buildPython tools/package_release.py --package
        if ($LASTEXITCODE -ne 0) { throw 'Release packaging failed.' }
    }
    Write-Output "Built ExplorerTweaks v$version."
} finally { Pop-Location }
