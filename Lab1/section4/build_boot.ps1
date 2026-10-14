$ErrorActionPreference = 'Stop'
$labRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$reportLogs = Join-Path $labRoot 'report/logs'
New-Item -ItemType Directory -Force -Path $reportLogs | Out-Null
$platformBoot = Join-Path $labRoot 'vitis_workspace/platform_section4_divider/export/platform_section4_divider/sw/platform_section4_divider/boot/fsbl.elf'
$bitstream = Join-Path $labRoot 'vivado/section4_divider/lab1_section4_divider.runs/impl_1/Zynq_CPU_wrapper.bit'
$application = Join-Path $labRoot 'vitis_workspace/hello_rtl_divider/Debug/hello_rtl_divider.elf'
foreach ($inputFile in @($platformBoot, $bitstream, $application)) {
    if (!(Test-Path -LiteralPath $inputFile)) { throw "Missing build input: $inputFile" }
}
$bootDir = Join-Path $labRoot 'boot'
$bifPath = Join-Path $bootDir 'section4-divider.bif'
$binPath = Join-Path $bootDir 'section4-divider-BOOT.bin'
$bifText = @"
the_ROM_image:
{
    [bootloader] $($platformBoot.Replace('\', '/'))
    $($bitstream.Replace('\', '/'))
    $($application.Replace('\', '/'))
}
"@
Set-Content -LiteralPath $bifPath -Value $bifText -Encoding ascii
& D:/Xilinx/Vitis/2022.1/bin/bootgen.bat -arch zynq -image $bifPath -o $binPath -w on
if ($LASTEXITCODE -ne 0) { throw 'Boot image generation failed' }
& D:/Xilinx/Vitis/2022.1/bin/bootgen.bat -arch zynq -read $binPath *> (Join-Path $reportLogs 'section4_divider_boot_image.txt')
if ($LASTEXITCODE -ne 0) { throw 'Boot image inspection failed' }
python (Join-Path $PSScriptRoot 'verify_boot.py')
if ($LASTEXITCODE -ne 0) { throw 'Boot header validation failed' }
$bootHash = Get-FileHash -LiteralPath $binPath -Algorithm SHA256
Set-Content -LiteralPath (Join-Path $bootDir 'section4-divider-BOOT.sha256') -Value "$($bootHash.Hash.ToLower())  section4-divider-BOOT.bin" -Encoding ascii
Get-Item -LiteralPath $binPath | Select-Object FullName,Length
