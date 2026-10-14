set lab [file normalize [file join [file dirname [info script]] ..]]
if {[catch {
setws [file join $lab vitis_workspace]
repo -set [file join $lab vivado ip_repo]
set platform_file [file join $lab vitis_workspace platform_section4_divider platform.spr]
if {[file exists $platform_file]} {
platform read $platform_file
} else {
platform create -name platform_section4_divider -hw [file join $lab exported platform_section4_divider.xsa] -out [file join $lab vitis_workspace]
}
platform active platform_section4_divider
if {[catch {domain active standalone_ps7_cortexa9_0}]} {
domain create -name standalone_ps7_cortexa9_0 -os standalone -proc ps7_cortexa9_0 -runtime cpp -arch 32-bit -support-app hello_world
}
platform write
platform generate
if {![file exists [file join $lab vitis_workspace hello_rtl_divider .project]]} {
app create -name hello_rtl_divider -platform platform_section4_divider -domain standalone_ps7_cortexa9_0 -template {Hello World}
}
set src [file join $lab vitis_workspace hello_rtl_divider src]
set hello [file join $src helloworld.c]
if {[file exists $hello]} {
    file attributes $hello -readonly 0
    file delete $hello
}
file copy -force [file join $lab section4 lab1-divider.c] [file join $src lab1-divider.c]
app build -name hello_rtl_divider
puts "DIVIDER_SOFTWARE_BUILD_PASS"
} message]} {
    puts stderr "DIVIDER_SOFTWARE_BUILD_FAILED: $message"
    exit 1
}
exit 0
