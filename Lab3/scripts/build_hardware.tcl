set lab [file normalize [file join [file dirname [info script]] ..]]
set work [file join $lab vivado lab3]
file mkdir $work
open_project [file join $lab .. Lab1 vivado section4 lab1_section4.xpr]
open_bd_design [get_files Zynq_CPU.bd]
write_bd_tcl -force [file join $work base_design.tcl]
set board [get_property BOARD_PART [current_project]]
set repos [get_property BOARD_PART_REPO_PATHS [current_project]]
close_project
set_param board.repoPaths $repos
create_project -force lab3 $work -part xc7z020clg400-1
set_property board_part $board [current_project]
set_property ip_repo_paths [list [file join $lab .. Lab1 vivado ip_repo] \
    [file join $lab build dct_accel solution1 impl ip] \
    [file join $lab build fir_accel solution1 impl ip] \
    [file join $lab build add solution1 impl ip]] [current_project]
update_ip_catalog
source [file join $work base_design.tcl]
# Preserve the known board's PS/DDR/UART setup and replace the Lab1 peripheral.
delete_bd_objs [get_bd_cells rtl_multiplier_0]
set_property CONFIG.NUM_MI 3 [get_bd_cells ps7_0_axi_periph]
foreach {name type idx offset} {
    dct_accel_0 dct_accel 0 0x43C00000
    fir_accel_0 fir_accel 1 0x43C10000
    scalar_add add 2 0x43C20000
} {
    create_bd_cell -type ip -vlnv xilinx.com:hls:${type}:1.0 $name
    connect_bd_intf_net [get_bd_intf_pins ps7_0_axi_periph/[format M%02d_AXI $idx]] [get_bd_intf_pins $name/s_axi_CTRL]
    connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins $name/ap_clk] \
        [get_bd_pins ps7_0_axi_periph/M0${idx}_ACLK]
    connect_bd_net [get_bd_pins rst_ps7_0_100M/peripheral_aresetn] [get_bd_pins $name/ap_rst_n] \
        [get_bd_pins ps7_0_axi_periph/M0${idx}_ARESETN]
    assign_bd_address -offset $offset -range 64K [get_bd_addr_segs $name/s_axi_CTRL/*]
}
validate_bd_design
regenerate_bd_layout
save_bd_design
write_bd_tcl -force [file join $lab scripts lab3_block_design.tcl]
set bd [get_files Zynq_CPU.bd]
generate_target all $bd
add_files -norecurse [make_wrapper -files $bd -top]
set_property top Zynq_CPU_wrapper [current_fileset]
update_compile_order -fileset sources_1
launch_runs impl_1 -to_step write_bitstream -jobs 4
wait_on_run impl_1
if {[get_property PROGRESS [get_runs impl_1]] ne "100%"} {error "Hardware build failed"}
open_run impl_1
report_utilization -file [file join $lab logs utilization.txt]
report_timing_summary -file [file join $lab logs timing.txt]
report_drc -file [file join $lab logs drc.txt]
set setup [get_timing_paths -max_paths 1]
set hold [get_timing_paths -delay_type min -max_paths 1]
if {[llength $setup]==0 || [get_property SLACK $setup]<0} {error "Setup timing failed"}
if {[llength $hold]==0 || [get_property SLACK $hold]<0} {error "Hold timing failed"}
write_hw_platform -fixed -include_bit -force -file [file join $lab exported lab3.xsa]
file copy -force [file join $work lab3.runs impl_1 Zynq_CPU_wrapper.bit] [file join $lab exported lab3.bit]
file copy -force [file join $work lab3.gen sources_1 bd Zynq_CPU hw_handoff Zynq_CPU.hwh] [file join $lab exported lab3.hwh]
puts "LAB3_HARDWARE_BUILD_PASS"
close_project
exit
