[CmdletBinding()]
param(
    [string]$Configuration = "Release",
    [string]$BuildDir = "",
    [string]$VcpkgRoot = "",
    [switch]$InstallVcpkg,
    [switch]$RunSmokeTest
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

$repoRoot = $PSScriptRoot
$projectDir = Join-Path $repoRoot "external\cvAutoTrack"
if (-not $BuildDir) {
    $BuildDir = Join-Path $projectDir "build-windows"
}

if (-not (Test-Path $projectDir)) {
    throw "cvAutoTrack project was not found at $projectDir"
}

$candidateVcpkgRoots = @()
if ($VcpkgRoot) {
    $candidateVcpkgRoots += $VcpkgRoot
}
if ($env:VCPKG_ROOT) {
    $candidateVcpkgRoots += $env:VCPKG_ROOT
}
if ($env:VCPKG_INSTALLATION_ROOT) {
    $candidateVcpkgRoots += $env:VCPKG_INSTALLATION_ROOT
}
$candidateVcpkgRoots += (Join-Path $repoRoot "external\vcpkg")
$candidateVcpkgRoots += "C:\vcpkg"
$candidateVcpkgRoots += "C:\Users\Public\vcpkg"

$resolvedVcpkgRoot = $null
foreach ($candidate in $candidateVcpkgRoots) {
    if (-not $candidate) {
        continue
    }

    $toolchain = Join-Path $candidate "scripts\buildsystems\vcpkg.cmake"
    if (Test-Path $toolchain) {
        $resolvedVcpkgRoot = (Resolve-Path $candidate).Path
        break
    }
}

if (-not $resolvedVcpkgRoot) {
    $localVcpkgRoot = Join-Path $repoRoot "external\vcpkg"
    if ($InstallVcpkg) {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            throw "git is required to install vcpkg automatically."
        }

        Write-Host "Installing vcpkg into $localVcpkgRoot"
        Invoke-Checked -FilePath git -Arguments @("clone", "https://github.com/microsoft/vcpkg.git", $localVcpkgRoot)
        Invoke-Checked -FilePath (Join-Path $localVcpkgRoot "bootstrap-vcpkg.bat") -Arguments @("-disableMetrics")
        $resolvedVcpkgRoot = (Resolve-Path $localVcpkgRoot).Path
    }
    else {
        throw "vcpkg was not found. Re-run with -InstallVcpkg, or set VCPKG_ROOT to an existing vcpkg checkout."
    }
}
elseif (-not (Test-Path (Join-Path $resolvedVcpkgRoot "vcpkg.exe"))) {
    Write-Host "Bootstrapping vcpkg at $resolvedVcpkgRoot"
    Invoke-Checked -FilePath (Join-Path $resolvedVcpkgRoot "bootstrap-vcpkg.bat") -Arguments @("-disableMetrics")
}

$env:VCPKG_ROOT = $resolvedVcpkgRoot

Write-Host "Using vcpkg: $env:VCPKG_ROOT"
Write-Host "Configuring cvAutoTrack..."
Invoke-Checked -FilePath cmake -Arguments @("-S", $projectDir, "-B", $BuildDir, "-A", "x64", "-DBUILD_CVAUTOTRACK_TESTS=ON")

Write-Host "Building cvAutoTrack.dll and test_impl_cpp.exe..."
Invoke-Checked -FilePath cmake -Arguments @("--build", $BuildDir, "--config", $Configuration, "--target", "cvAutoTrack", "test_impl_cpp")

$outputDir = Join-Path $BuildDir "bin\$Configuration"
$exePath = Join-Path $outputDir "test_impl_cpp.exe"
$dllPath = Join-Path $outputDir "cvAutoTrack.dll"

if (-not (Test-Path $exePath)) {
    throw "Expected executable was not created: $exePath"
}
if (-not (Test-Path $dllPath)) {
    throw "Expected DLL was not created: $dllPath"
}

if ($RunSmokeTest) {
    Write-Host "Running smoke test..."
    Invoke-Checked -FilePath $exePath -Arguments @("-test")
}

Write-Host ""
Write-Host "Build complete."
Write-Host "Executable: $exePath"
Write-Host "DLL:        $dllPath"
