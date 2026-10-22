set lab [file normalize [file join [file dirname [info script]] ..]]
open_project [file join $lab vivado lab2 lab2.xpr]
open_run impl_1
report_utilization -name lab2_utilization
report_timing_summary -name lab2_timing_summary
puts "LAB2_CAPTURE_DESIGN_READY"
