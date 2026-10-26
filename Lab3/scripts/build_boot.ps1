$ErrorActionPreference = 'Stop'
$labRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$fsbl = Join-Path $labRoot 'vitis_workspace/lab3_platform/export/lab3_platform/sw/lab3_platform/boot/fsbl.elf'
$bitstream = Join-Path $labRoot 'vivado/lab3/lab3.runs/impl_1/Zynq_CPU_wrapper.bit'
$application = Join-Path $labRoot 'vitis_workspace/lab3_app/Debug/lab3_app.elf'
foreach ($inputFile in @($fsbl,$bitstream,$application)) {
    if (!(Test-Path -LiteralPath $inputFile)) { throw "Missing build input: $inputFile" }
}
$bootDir = Join-Path $labRoot 'boot'
New-Item -ItemType Directory -Force -Path $bootDir | Out-Null
$bifPath = Join-Path $bootDir 'lab3.bif'
$binPath = Join-Path $bootDir 'BOOT.BIN'
$bifText = @"
the_ROM_image:
{
    [bootloader] $($fsbl.Replace('\','/'))
    $($bitstream.Replace('\','/'))
    $($application.Replace('\','/'))
}
"@
Set-Content -LiteralPath $bifPath -Value $bifText -Encoding ascii
& D:/Xilinx/Vitis/2022.1/bin/bootgen.bat -arch zynq -image $bifPath -o $binPath -w on
if ($LASTEXITCODE -ne 0) { throw 'Boot image generation failed' }
& D:/Xilinx/Vitis/2022.1/bin/bootgen.bat -arch zynq -read $binPath *> (Join-Path $labRoot 'logs/boot_image.txt')
if ($LASTEXITCODE -ne 0) { throw 'Boot image inspection failed' }
python (Join-Path $PSScriptRoot 'verify_boot.py')
if ($LASTEXITCODE -ne 0) { throw 'Boot image verification failed' }
Get-Item -LiteralPath $binPath | Select-Object FullName,Length
