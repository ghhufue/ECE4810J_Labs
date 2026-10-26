$ErrorActionPreference='Stop'
$labRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$simDir=Join-Path $labRoot 'build/add_axi_sim'
New-Item -ItemType Directory -Force -Path $simDir | Out-Null
Set-Content -LiteralPath "$simDir/run.tcl" -Value 'run all'
Push-Location $simDir
try {
    & D:/Xilinx/Vivado/2022.1/bin/xvlog.bat "$labRoot/build/add/solution1/syn/verilog/add.v" "$labRoot/build/add/solution1/syn/verilog/add_CTRL_s_axi.v" "$labRoot/tests/test_add_axi.v" *> "$labRoot/logs/add_axi_compile.txt"
    if($LASTEXITCODE -ne 0){throw 'AXI RTL compilation failed'}
    & D:/Xilinx/Vivado/2022.1/bin/xelab.bat test_add_axi -s lab3_add_test *> "$labRoot/logs/add_axi_elaborate.txt"
    if($LASTEXITCODE -ne 0){throw 'AXI RTL elaboration failed'}
    & D:/Xilinx/Vivado/2022.1/bin/xsim.bat lab3_add_test -tclbatch run.tcl *> "$labRoot/logs/add_axi_simulation.txt"
    if($LASTEXITCODE -ne 0 -or !(Select-String -Quiet -LiteralPath "$labRoot/logs/add_axi_simulation.txt" -Pattern 'LAB3_ADD_AXI_PASS')){throw 'AXI RTL test failed'}
    Write-Output 'LAB3_ADD_AXI_PASS'
} finally {Pop-Location}
