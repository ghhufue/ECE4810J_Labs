set lab [file normalize [file join [file dirname [info script]] ..]]
file mkdir [file join $lab build]
file mkdir [file join $lab logs]
cd [file join $lab build]
set task all
if {[info exists ::env(LAB3_HLS_TASK)]} {set task $::env(LAB3_HLS_TASK)}

proc save_reports {lab family solution} {
    set dest [file join $lab logs $family $solution]
    file mkdir $dest
    foreach f [glob -nocomplain [file join $lab build ${family}.prj $solution syn report *]] {
        file copy -force $f $dest
    }
}

if {$task in {all yuv}} {
    set src [file join $lab lab3_starter yuv_filter]
    open_project -reset yuv.prj
    set_top yuv_filter
    add_files [file join $src yuv_filter.c]
    add_files -tb [file join $src image_aux.c]
    add_files -tb [file join $lab tests test_yuv.c] -cflags "-I$src"
    add_files -tb [file join $src input.dat]
    add_files -tb [file join $src output.golden.dat]
    foreach solution {baseline_no_tripcount solution1 solution2 solution3_pipo solution3_fifo} {
        open_solution -reset $solution -flow_target vivado
        set_part xc7z020clg400-1
        create_clock -period 10 -name default
        if {$solution in {baseline_no_tripcount solution1}} {
            config_compile -pipeline_loops 0
            foreach func {rgb2yuv yuv_scale yuv2rgb} {
                set_directive_pipeline -off $func
                set_directive_pipeline -off "$func/[string toupper $func]_LOOP_Y"
            }
        } else {
            foreach func {rgb2yuv yuv_scale yuv2rgb} {
                set_directive_inline -off $func
                set_directive_pipeline -II 1 "$func/[string toupper $func]_LOOP_Y"
            }
        }
        if {$solution ne "baseline_no_tripcount"} {
            foreach func {rgb2yuv yuv_scale yuv2rgb} {
                # Header bounds are 512x512. Unlike the manual's generic 1920x1280
                # example, report the maximum that this supplied image_t can hold.
                set_directive_loop_tripcount -min 200 -max 512 "$func/[string toupper $func]_LOOP_X"
                set_directive_loop_tripcount -min 200 -max 512 "$func/[string toupper $func]_LOOP_Y"
            }
        }
        if {$solution in {solution3_pipo solution3_fifo}} {set_directive_dataflow yuv_filter}
        if {$solution eq "solution3_fifo"} {
            config_dataflow -default_channel fifo -fifo_depth 2
        }
        if {$solution eq "solution1"} {csim_design -clean}
        csynth_design
        save_reports $lab yuv $solution
    }
    close_project
}

if {$task in {all dct}} {
    set src [file join $lab lab3_starter dct]
    open_project -reset dct.prj
    set_top dct
    add_files [file join $src dct.c]
    add_files -tb [file join $lab tests test_dct.c] -cflags "-I$src"
    foreach solution {solution1 solution2 solution3 solution4 solution5} {
        open_solution -reset $solution -flow_target vivado
        set_part xc7z020clg400-1
        create_clock -period 10 -name default
        foreach loc {dct_2d/Xpose_Row_Inner_Loop dct_2d/Xpose_Col_Inner_Loop read_data/RD_Loop_Col write_data/WR_Loop_Col} {
            set_directive_pipeline $loc
        }
        if {$solution eq "solution1"} {set_directive_pipeline dct_1d/DCT_Inner_Loop}
        if {$solution in {solution3 solution4 solution5}} {
            set_directive_array_partition -type complete -dim 2 dct buf_2d_in
            set_directive_array_partition -type complete -dim 2 dct_2d col_inbuf
        }
        if {$solution in {solution4 solution5}} {set_directive_dataflow dct}
        if {$solution eq "solution5"} {set_directive_inline dct_2d}
        if {$solution eq "solution1"} {csim_design -clean}
        csynth_design
        if {$solution in {solution1 solution5}} {cosim_design -rtl verilog -tool xsim}
        save_reports $lab dct $solution
    }
    close_project
}
puts "LAB3_HLS_BUILD_PASS $task"
exit
