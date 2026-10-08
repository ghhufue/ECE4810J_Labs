# 
# Usage: To re-create this platform project launch xsct with below options.
# xsct C:\Users\yht\workspace\arty_z7_platform\platform.tcl
# 
# OR launch xsct and run below command.
# source C:\Users\yht\workspace\arty_z7_platform\platform.tcl
# 
# To create the platform in a different location, modify the -out option of "platform create" command.
# -out option specifies the output directory of the platform project.

platform create -name {arty_z7_platform}\
-hw {D:\code\ECE4810J\Lab1\section2_basic\lab1_basic\Zynq_CPU_wrapper.xsa}\
-out {C:/Users/yht/workspace}

platform write
domain create -name {standalone_ps7_cortexa9_0} -display-name {standalone_ps7_cortexa9_0} -os {standalone} -proc {ps7_cortexa9_0} -runtime {cpp} -arch {32-bit} -support-app {hello_world}
platform generate -domains 
platform active {arty_z7_platform}
domain active {zynq_fsbl}
domain active {standalone_ps7_cortexa9_0}
platform generate -quick
platform generate
platform generate
