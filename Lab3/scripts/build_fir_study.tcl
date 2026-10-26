set lab [file normalize [file join [file dirname [info script]] ..]]
cd [file join $lab build]
open_project -reset fir.prj
set_top fir
add_files [file join $lab lab3_starter fir fir.cpp]
add_files -tb [file join $lab tests test_fir.cpp]
add_files -tb [file join $lab lab3_starter fir input.dat]
add_files -tb [file join $lab lab3_starter fir out.gold.dat]
foreach sol {baseline pipeline} {
    open_solution -reset $sol -flow_target vivado
    set_part xc7z020clg400-1
    create_clock -period 10
    config_compile -pipeline_loops 0
    if {$sol eq "pipeline"} {set_directive_pipeline fir/FIR_TAPS}
    csynth_design
    set dest [file join $lab logs fir $sol]
    file mkdir $dest
    foreach f [glob -nocomplain [file join $lab build fir.prj $sol syn report *]] {file copy -force $f $dest}
}
puts "LAB3_FIR_STUDY_PASS"
exit
