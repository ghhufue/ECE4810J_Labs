$ErrorActionPreference = 'Stop'
$labRoot = Split-Path $PSScriptRoot -Parent
$simRoot = Join-Path $labRoot 'section4/simulation'
New-Item -ItemType Directory -Force -Path $simRoot | Out-Null
$reportLogs = Join-Path $labRoot 'report/logs'
New-Item -ItemType Directory -Force -Path $reportLogs | Out-Null
$vivadoBin = 'D:/Xilinx/Vivado/2022.1/bin'
Push-Location $simRoot
try {
    & "$vivadoBin/xvlog.bat" --sv "$labRoot/vivado/ip_repo/rtl_divider_1.0/src/rtl_divider.v" "$labRoot/vivado/ip_repo/rtl_divider_1.0/hdl/rtl_divider_v1_0_S00_AXI.v" "$labRoot/section4/tb_rtl_divider.sv"
    if ($LASTEXITCODE -ne 0) { throw 'Compile failed' }
    & "$vivadoBin/xelab.bat" tb_rtl_divider -s divider_sim -debug typical
    if ($LASTEXITCODE -ne 0) { throw 'Elaboration failed' }
    & "$vivadoBin/xsim.bat" divider_sim -runall -log "$reportLogs/section4_divider_simulation.txt"
    if ($LASTEXITCODE -ne 0) { throw 'Simulation failed' }
    if (!(Select-String -Quiet -Path "$reportLogs/section4_divider_simulation.txt" -Pattern 'DIVIDER_SIMULATION_PASS')) { throw 'Simulation did not pass' }
} finally { Pop-Location }
