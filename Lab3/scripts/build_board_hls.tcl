set lab [file normalize [file join [file dirname [info script]] ..]]
cd [file join $lab build]
foreach {name macro extra} {
    dct_accel TEST_DCT dct
    fir_accel TEST_FIR fir
    add TEST_ADD none
} {
    if {[info exists ::env(LAB3_BOARD_IP)] && $name ne $::env(LAB3_BOARD_IP)} {continue}
    open_project -reset $name
    set_top $name
    add_files [file join $lab hls ${name}.cpp]
    if {$extra eq "dct"} {
        file copy -force [file join $lab lab3_starter dct dct.c] [file join $lab build dct_kernel.cpp]
        add_files [file join $lab build dct_kernel.cpp] -cflags "-I[file join $lab lab3_starter dct]"
    }
    if {$extra eq "fir"} {add_files [file join $lab lab3_starter fir fir.cpp]}
    add_files -tb [file join $lab tests test_board_ip.cpp] -cflags "-D$macro"
    open_solution -reset solution1 -flow_target vivado
    set_part xc7z020clg400-1
    create_clock -period 10
    if {$extra eq "dct"} {
        set_directive_pipeline dct_1d/DCT_Inner_Loop
        set_directive_pipeline idct_1d/IDCT_Inner_Loop
    }
    if {$extra eq "fir"} {
        set_directive_pipeline fir/FIR_TAPS
    }
    csim_design -clean
    csynth_design
    # Vitis 2022.1 generates an invalid ap_done reference for ap_ctrl_none.
    # add is verified by tests/test_add_axi.v against the actual generated RTL.
    if {$name ne "add"} {cosim_design -rtl verilog -tool xsim}
    export_design -format ip_catalog -rtl verilog
    set dest [file join $lab logs board_ip $name]
    file mkdir $dest
    foreach f [glob -nocomplain [file join $lab build $name solution1 syn report *]] {file copy -force $f $dest}
    close_project
}
puts "LAB3_BOARD_HLS_PASS"
exit
