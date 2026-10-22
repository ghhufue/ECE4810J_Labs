$ErrorActionPreference = 'Stop'
$labRoot = Split-Path $PSScriptRoot -Parent
$simRoot = Join-Path $labRoot 'build/simulation'
New-Item -ItemType Directory -Force -Path $simRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $labRoot 'logs') | Out-Null
$vivadoBin = 'D:/Xilinx/Vivado/2022.1/bin'
Push-Location $simRoot
try {
    & "$vivadoBin/xvlog.bat" --sv "$labRoot/rtl/rtl_alu.sv" "$labRoot/rtl/rtl_pipe_alu.sv" "$labRoot/tests/tb_alu.sv"
    if ($LASTEXITCODE -ne 0) { throw 'RTL compile failed' }
    & "$vivadoBin/xelab.bat" tb_alu -s alu_sim -debug typical
    if ($LASTEXITCODE -ne 0) { throw 'RTL elaboration failed' }
    & "$vivadoBin/xsim.bat" alu_sim -runall -log "$labRoot/logs/rtl_simulation.txt"
    if ($LASTEXITCODE -ne 0) { throw 'RTL simulation failed' }
    if (!(Select-String -Quiet -LiteralPath "$labRoot/logs/rtl_simulation.txt" -Pattern 'RTL_ALU_PASS')) { throw 'RTL simulation did not pass' }
    & "$vivadoBin/xvlog.bat" --sv "$labRoot/ip_repo/rtl_pipe_alu_1.0/hdl/rtl_pipe_alu_v1_0_S00_AXI.v" "$labRoot/tests/tb_axi_alu.sv"
    if ($LASTEXITCODE -ne 0) { throw 'AXI compile failed' }
    & "$vivadoBin/xelab.bat" tb_axi_alu -s axi_alu_sim -debug typical
    if ($LASTEXITCODE -ne 0) { throw 'AXI elaboration failed' }
    & "$vivadoBin/xsim.bat" axi_alu_sim -runall -log "$labRoot/logs/axi_simulation.txt"
    if ($LASTEXITCODE -ne 0) { throw 'AXI simulation failed' }
    if (!(Select-String -Quiet -LiteralPath "$labRoot/logs/axi_simulation.txt" -Pattern 'AXI_ALU_PASS')) { throw 'AXI simulation did not pass' }
} finally { Pop-Location }
