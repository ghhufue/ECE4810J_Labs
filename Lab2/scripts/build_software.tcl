set lab [file normalize [file join [file dirname [info script]] ..]]
if {[catch {
    setws [file join $lab vitis_workspace]
    repo -set [list [file join $lab ip_repo] \
        [file join $lab build hls_multiplier solution1 impl ip] \
        [file join $lab build hls_alu solution1 impl ip]]
    set platform_file [file join $lab vitis_workspace lab2_platform platform.spr]
    if {[file exists $platform_file]} {
        platform read $platform_file
        platform active lab2_platform
        platform config -updatehw [file join $lab exported lab2.xsa]
    } else {
        platform create -name lab2_platform -hw [file join $lab exported lab2.xsa] -out [file join $lab vitis_workspace]
    }
    platform active lab2_platform
    if {[catch {domain active standalone_ps7_cortexa9_0}]} {
        domain create -name standalone_ps7_cortexa9_0 -os standalone -proc ps7_cortexa9_0 -runtime cpp -arch 32-bit -support-app hello_world
    }
    platform write
    platform generate
    # Vitis 2022.1's headless Eclipse application-template creation can stall.
    # Use the same bundled ARM toolchain and the newly generated matching BSP.
    puts [exec python [file join $lab scripts build_arm.py] 2>@1]
    puts "LAB2_SOFTWARE_BUILD_PASS"
} message]} {
    puts stderr "LAB2_SOFTWARE_BUILD_FAILED: $message"
    exit 1
}
exit 0
