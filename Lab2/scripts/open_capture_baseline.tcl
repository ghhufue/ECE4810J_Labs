set lab [file normalize [file join [file dirname [info script]] ..]]
open_project [file join $lab vivado lab2_baseline lab2_baseline.xpr]
open_run impl_1
report_utilization -name baseline_utilization
report_timing_summary -name baseline_timing
report_utilization -file [file join $lab logs baseline_utilization.txt]
report_utilization -hierarchical -file [file join $lab logs baseline_utilization_hierarchical.txt]
report_timing_summary -file [file join $lab logs baseline_timing.txt]
highlight_objects -color red [get_cells -hierarchical -filter {NAME =~ "Zynq_CPU_i/rtl_alu_0/*" && IS_PRIMITIVE}]
highlight_objects -color yellow [get_cells -hierarchical -filter {NAME =~ "Zynq_CPU_i/hls_alu_0/*" && IS_PRIMITIVE}]
puts "LAB2_BASELINE_CAPTURE_READY"
