param([switch]$SkipHls, [switch]$SkipHardware)
$ErrorActionPreference = 'Stop'
$labRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$repoRoot = Split-Path $labRoot -Parent
New-Item -ItemType Directory -Force -Path (Join-Path $labRoot 'logs') | Out-Null
Push-Location $repoRoot
try {
    python "$PSScriptRoot/generate_vectors.py"
    if ($LASTEXITCODE -ne 0) { throw 'Vector generation failed' }
    python "$PSScriptRoot/create_alu_ip.py"
    if ($LASTEXITCODE -ne 0) { throw 'IP packaging failed' }
    & "$PSScriptRoot/run_simulation.ps1"
    if (!$SkipHls) {
        & D:/Xilinx/Vitis_HLS/2022.1/bin/vitis_hls.bat -f "$PSScriptRoot/build_hls.tcl" *> "$labRoot/logs/hls_build.txt"
        if ($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -LiteralPath "$labRoot/logs/hls_build.txt" -Pattern '^LAB2_HLS_BUILD_PASS$')) {
            Get-Content "$labRoot/logs/hls_build.txt" -Tail 40
            throw 'HLS build failed'
        }
    }
    if (!$SkipHardware) {
        & D:/Xilinx/Vivado/2022.1/bin/vivado.bat -mode batch -source "$PSScriptRoot/build_hardware.tcl" -log "$labRoot/logs/hardware_build.log" -journal "$labRoot/logs/hardware_build.jou" *> "$labRoot/logs/hardware_console.txt"
        if ($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -LiteralPath "$labRoot/logs/hardware_build.log" -Pattern '^LAB2_HARDWARE_BUILD_PASS$')) {
            Get-Content "$labRoot/logs/hardware_console.txt" -Tail 40
            throw 'Hardware build failed'
        }
    }
    & D:/Xilinx/Vitis/2022.1/bin/xsct.bat "$PSScriptRoot/build_software.tcl" *> "$labRoot/logs/software_build.txt"
    if ($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -LiteralPath "$labRoot/logs/software_build.txt" -Pattern '^LAB2_SOFTWARE_BUILD_PASS$')) {
        Get-Content "$labRoot/logs/software_build.txt" -Tail 40
        throw 'Software build failed'
    }
    & "$PSScriptRoot/build_boot.ps1"
    Write-Output "LAB2_BUILD_PASS: $labRoot/boot/BOOT.BIN"
} finally { Pop-Location }
