set lab [file normalize [file join [file dirname [info script]] ..]]
file mkdir [file join $lab build]
cd [file join $lab build]
foreach name {hls_multiplier hls_alu} {
    open_project -reset $name
    set_top $name
    add_files [file join $lab hls ${name}.cpp]
    add_files -tb [file join $lab hls test_${name}.cpp]
    open_solution -reset solution1 -flow_target vivado
    set_part xc7z020clg400-1
    create_clock -period 10 -name default
    csim_design -clean
    csynth_design
    cosim_design -rtl verilog -tool xsim -trace_level port
    export_design -format ip_catalog -rtl verilog
    file mkdir [file join $lab logs]
    foreach {subdir suffix output_suffix} {
        csim/report csim.log csim.txt
        syn/report csynth.rpt csynth.txt
        sim/report cosim.rpt cosim.txt
    } {
        file copy -force [file join $lab build $name solution1 $subdir ${name}_${suffix}] \
            [file join $lab logs ${name}_${output_suffix}]
    }
    close_project
}
puts "LAB2_HLS_BUILD_PASS"
exit
