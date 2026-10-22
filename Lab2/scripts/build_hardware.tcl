set lab [file normalize [file join [file dirname [info script]] ..]]
set work [file join $lab vivado lab2]
file mkdir $work
file mkdir [file join $lab logs]
file mkdir [file join $lab exported]
# Clone the original PS, DDR, UART and board setup; do not modify Lab 1.
open_project [file join $lab .. Lab1 vivado section4 lab1_section4.xpr]
open_bd_design [get_files Zynq_CPU.bd]
write_bd_tcl -force [file join $work base_design.tcl]
set board [get_property BOARD_PART [current_project]]
set board_repos [get_property BOARD_PART_REPO_PATHS [current_project]]
close_project
set_param board.repoPaths $board_repos
create_project -force lab2 $work -part xc7z020clg400-1
set_property board_part $board [current_project]
set_property ip_repo_paths [list [file join $lab .. Lab1 vivado ip_repo] \
    [file join $lab ip_repo] [file join $lab build hls_multiplier solution1 impl ip] \
    [file join $lab build hls_alu solution1 impl ip]] [current_project]
update_ip_catalog
source [file join $work base_design.tcl]
set_property CONFIG.NUM_MI {4} [get_bd_cells ps7_0_axi_periph]
foreach {name vlnv port index offset} {
    hls_multiplier_0 xilinx.com:hls:hls_multiplier:1.0 s_axi_CRTLS 1 0x43C10000
    rtl_pipe_alu_0 xilinx.com:user:rtl_pipe_alu:1.0 S00_AXI 2 0x43C20000
    hls_alu_0 xilinx.com:hls:hls_alu:1.0 s_axi_CTRL 3 0x43C30000
} {
    create_bd_cell -type ip -vlnv $vlnv $name
    set bus [format M%02d_AXI $index]
    connect_bd_intf_net [get_bd_intf_pins ps7_0_axi_periph/$bus] [get_bd_intf_pins $name/$port]
    if {$name eq "rtl_pipe_alu_0"} { set clk s00_axi_aclk; set rst s00_axi_aresetn } \
    else { set clk ap_clk; set rst ap_rst_n }
    connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins $name/$clk] \
        [get_bd_pins ps7_0_axi_periph/M0${index}_ACLK]
    connect_bd_net [get_bd_pins rst_ps7_0_100M/peripheral_aresetn] [get_bd_pins $name/$rst] \
        [get_bd_pins ps7_0_axi_periph/M0${index}_ARESETN]
    assign_bd_address -offset $offset -range 64K [get_bd_addr_segs $name/$port/*]
}
validate_bd_design
regenerate_bd_layout
save_bd_design
write_bd_tcl -force [file join $lab scripts lab2_block_design.tcl]
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
report_utilization -hierarchical -file [file join $lab logs utilization_hierarchical.txt]
report_timing_summary -file [file join $lab logs timing.txt]
report_drc -file [file join $lab logs drc.txt]
set paths [get_timing_paths -max_paths 1 -nworst 1]
if {[llength $paths] == 0} {error "No constrained timing paths"}
if {[get_property SLACK $paths] < 0} {error "Design failed setup timing"}
set hold_paths [get_timing_paths -delay_type min -max_paths 1 -nworst 1]
if {[get_property SLACK $hold_paths] < 0} {error "Design failed hold timing"}
write_hw_platform -fixed -include_bit -force -file [file join $lab exported lab2.xsa]
puts "LAB2_HARDWARE_BUILD_PASS"
close_project
