# 
# Usage: To re-create this platform project launch xsct with below options.
# xsct D:\code\ECE4810J\Lab1\vitis_workspace\platform_section4\platform.tcl
# 
# OR launch xsct and run below command.
# source D:\code\ECE4810J\Lab1\vitis_workspace\platform_section4\platform.tcl
# 
# To create the platform in a different location, modify the -out option of "platform create" command.
# -out option specifies the output directory of the platform project.

platform create -name {platform_section4}\
-hw {D:\code\ECE4810J\Lab1\exported\platform_section4.xsa}\
-out {D:/code/ECE4810J/Lab1/vitis_workspace}

platform write
domain create -name {standalone_ps7_cortexa9_0} -display-name {standalone_ps7_cortexa9_0} -os {standalone} -proc {ps7_cortexa9_0} -runtime {cpp} -arch {32-bit} -support-app {hello_world}
platform generate -domains 
platform active {platform_section4}
domain active {zynq_fsbl}
domain active {standalone_ps7_cortexa9_0}
platform generate -quick
platform generate
platform generate
platform clean
platform generate
