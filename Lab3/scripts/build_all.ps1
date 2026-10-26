param([switch]$SkipHls, [switch]$SkipHardware, [switch]$SkipSoftware)
$ErrorActionPreference='Stop'
$labRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
New-Item -ItemType Directory -Force -Path "$labRoot/logs","$labRoot/build" | Out-Null
function Check-Step([string]$Name) {if($LASTEXITCODE -ne 0){throw "$Name failed: exit $LASTEXITCODE"}}
function Invoke-Hls([string]$Script,[string]$Log,[string]$Marker) {
    # Vivado's Windows patcher may create a text file at D:/dev/null.
    # HLS make includes this path as a makefile. Preserve and clear only the
    # recognized runtime log, never an arbitrary existing file.
    $nullLog='D:/dev/null'
    if((Test-Path -LiteralPath $nullLog -PathType Leaf) -and (Get-Item -LiteralPath $nullLog).Length -gt 0) {
        $nullText=Get-Content -LiteralPath $nullLog -Raw
        if($nullText -notmatch '^\[Patcher\]' -or ($nullText -split "`n" | Where-Object {$_ -and $_ -notmatch '^\[Patcher\]'})) {
            throw 'HLS sees a nonempty D:/dev/null with unrecognized content. Inspect it before rebuilding.'
        }
        Copy-Item -LiteralPath $nullLog -Destination "$labRoot/logs/hls_dev_null_before.txt" -Force
        Clear-Content -LiteralPath $nullLog
    }
    & D:/Xilinx/Vitis_HLS/2022.1/bin/vitis_hls.bat -f "$PSScriptRoot/$Script" *> "$labRoot/logs/$Log"
    Check-Step $Script
    if(!(Select-String -Quiet -LiteralPath "$labRoot/logs/$Log" -Pattern $Marker)){throw "Missing completion marker: $Marker"}
}
Push-Location $labRoot
try {
    python "$PSScriptRoot/prepare_data.py"; Check-Step 'Reference generation'
    python "$PSScriptRoot/verify_native.py"; Check-Step 'Native verification'
    python "$PSScriptRoot/make_notebooks.py"; Check-Step 'Notebook generation'
    if(!$SkipHls) {
        Remove-Item Env:LAB3_HLS_TASK -ErrorAction SilentlyContinue
        Remove-Item Env:LAB3_BOARD_IP -ErrorAction SilentlyContinue
        Invoke-Hls 'build_hls.tcl' 'hls_build.txt' 'LAB3_HLS_BUILD_PASS'
        Invoke-Hls 'build_board_hls.tcl' 'hls_board_build.txt' 'LAB3_BOARD_HLS_PASS'
        Invoke-Hls 'build_fir_study.tcl' 'hls_fir_study.txt' 'LAB3_FIR_STUDY_PASS'
    }
    & "$PSScriptRoot/test_add_axi.ps1"
    if(!$SkipHardware) {
        & D:/Xilinx/Vivado/2022.1/bin/vivado.bat -mode batch -source "$PSScriptRoot/build_hardware.tcl" -log "$labRoot/logs/hardware_build.log" -journal "$labRoot/logs/hardware_build.jou" *> "$labRoot/logs/hardware_console.txt"
        Check-Step 'Vivado'
        if(!(Select-String -Quiet -LiteralPath "$labRoot/logs/hardware_console.txt" -Pattern '^LAB3_HARDWARE_BUILD_PASS$')){throw 'Hardware completion missing'}
    }
    if(!$SkipSoftware) {
        & D:/Xilinx/Vitis/2022.1/bin/xsct.bat "$PSScriptRoot/build_software.tcl" *> "$labRoot/logs/software_build.txt"
        Check-Step 'Vitis software'
        if(!(Select-String -Quiet -LiteralPath "$labRoot/logs/software_build.txt" -Pattern '^LAB3_SOFTWARE_BUILD_PASS$')){throw 'Software completion missing'}
    }
    & "$PSScriptRoot/build_boot.ps1"
    python "$PSScriptRoot/summarize_reports.py";Check-Step 'Report extraction'
    Write-Output "LAB3_BUILD_PASS: $labRoot/boot/BOOT.BIN"
} finally {Pop-Location}
