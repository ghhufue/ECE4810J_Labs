# Separate Section 2 baseline. This does not rebuild the released boot image.
set lab [file normalize [file join [file dirname [info script]] ..]]
set work [file join $lab vivado lab2_baseline]
file mkdir $work
create_project -force lab2_baseline $work -part xc7z020clg400-1
set_property ip_repo_paths [list [file join $lab .. Lab1 vivado ip_repo] \
    [file join $lab ip_repo] [file join $lab build hls_multiplier solution1 impl ip] \
    [file join $lab build hls_alu solution1 impl ip]] [current_project]
update_ip_catalog
source [file join $lab scripts lab2_block_design.tcl]
delete_bd_objs [get_bd_cells rtl_pipe_alu_0]
create_bd_cell -type ip -vlnv xilinx.com:user:rtl_alu:1.0 rtl_alu_0
connect_bd_intf_net [get_bd_intf_pins ps7_0_axi_periph/M02_AXI] [get_bd_intf_pins rtl_alu_0/S00_AXI]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins rtl_alu_0/s00_axi_aclk]
connect_bd_net [get_bd_pins rst_ps7_0_100M/peripheral_aresetn] [get_bd_pins rtl_alu_0/s00_axi_aresetn]
assign_bd_address -offset 0x43C20000 -range 64K [get_bd_addr_segs rtl_alu_0/S00_AXI/S00_AXI_reg]
validate_bd_design
regenerate_bd_layout
save_bd_design
set bd [get_files Zynq_CPU.bd]
generate_target all $bd
add_files -norecurse [make_wrapper -files $bd -top]
set_property top Zynq_CPU_wrapper [current_fileset]
update_compile_order -fileset sources_1
launch_runs impl_1 -to_step route_design -jobs 4
wait_on_run impl_1
if {![string match "route_design Complete*" [get_property STATUS [get_runs impl_1]]]} {
    error "Baseline implementation failed: [get_property STATUS [get_runs impl_1]]"
}
open_run impl_1
report_utilization -file [file join $lab logs baseline_utilization.txt]
report_utilization -hierarchical -file [file join $lab logs baseline_utilization_hierarchical.txt]
report_timing_summary -file [file join $lab logs baseline_timing.txt]
puts "LAB2_BASELINE_IMPLEMENTATION_COMPLETE"
close_project
