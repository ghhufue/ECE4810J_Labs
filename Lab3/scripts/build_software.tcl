set lab [file normalize [file join [file dirname [info script]] ..]]
if {[catch {
    setws [file join $lab vitis_workspace]
    repo -set [list [file join $lab build dct_accel solution1 impl ip] \
        [file join $lab build fir_accel solution1 impl ip] [file join $lab build add solution1 impl ip]]
    set p [file join $lab vitis_workspace lab3_platform platform.spr]
    if {[file exists $p]} {
        platform read $p
        platform active lab3_platform
        platform config -updatehw [file join $lab exported lab3.xsa]
    } else {
        platform create -name lab3_platform -hw [file join $lab exported lab3.xsa] -out [file join $lab vitis_workspace]
    }
    platform active lab3_platform
    if {[catch {domain active standalone_ps7_cortexa9_0}]} {
        domain create -name standalone_ps7_cortexa9_0 -os standalone -proc ps7_cortexa9_0 -runtime cpp -arch 32-bit -support-app hello_world
    }
    platform write
    platform generate
    puts [exec python [file join $lab scripts build_arm.py] 2>@1]
    puts "LAB3_SOFTWARE_BUILD_PASS"
} message]} {
    puts stderr "LAB3_SOFTWARE_BUILD_FAILED: $message"
    exit 1
}
exit 0
