set lab [file normalize [file join [file dirname [info script]] ..]]
set work [file join $lab vivado section4_divider]
file mkdir $work
open_project [file join $lab vivado section4 lab1_section4.xpr]
open_bd_design [get_files Zynq_CPU.bd]
write_bd_tcl -force [file join $work base_design.tcl]
set board [get_property BOARD_PART [current_project]]
set board_repos [get_property BOARD_PART_REPO_PATHS [current_project]]
close_project
set_param board.repoPaths $board_repos
create_project -force lab1_section4_divider $work -part xc7z020clg400-1
set_property board_part $board [current_project]
set_property ip_repo_paths [list [file join $lab vivado ip_repo]] [current_project]
update_ip_catalog
source [file join $work base_design.tcl]
# Replace the multiplier while retaining the exact PS DDR/UART configuration.
delete_bd_objs [get_bd_cells rtl_multiplier_0]
create_bd_cell -type ip -vlnv xilinx.com:user:rtl_divider:1.0 rtl_divider_0
connect_bd_intf_net [get_bd_intf_pins ps7_0_axi_periph/M00_AXI] [get_bd_intf_pins rtl_divider_0/S00_AXI]
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins rtl_divider_0/s00_axi_aclk]
connect_bd_net [get_bd_pins rst_ps7_0_100M/peripheral_aresetn] [get_bd_pins rtl_divider_0/s00_axi_aresetn]
assign_bd_address -offset 0x43C00000 -range 64K [get_bd_addr_segs rtl_divider_0/S00_AXI/S00_AXI_reg]
validate_bd_design
regenerate_bd_layout
save_bd_design
set bd [get_files Zynq_CPU.bd]
generate_target all $bd
add_files -norecurse [make_wrapper -files $bd -top]
set_property top Zynq_CPU_wrapper [current_fileset]
update_compile_order -fileset sources_1
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "Hardware build failed"}
open_run impl_1
set report_logs [file join $lab report logs]
file mkdir $report_logs
report_utilization -file [file join $report_logs section4_divider_utilization.txt]
report_utilization -hierarchical -file [file join $report_logs section4_divider_utilization_hierarchical.txt]
report_timing_summary -file [file join $report_logs section4_divider_timing.txt]
set paths [get_timing_paths -max_paths 1 -nworst 1]
if {[llength $paths] == 0} {error "No constrained timing paths"}
if {[get_property SLACK $paths] < 0} {error "Design failed setup timing"}
write_hw_platform -fixed -include_bit -force -file [file join $lab exported platform_section4_divider.xsa]
puts "DIVIDER_HARDWARE_BUILD_PASS"
close_project
