# ECE4810J Lab 1 Section 6
# Group 2: Yuan Haotong and Zhao Tong

proc avg {numbers} {
    set count [llength $numbers]
    if {$count == 0} {
        error "avg requires at least one number"
    }
    set sum 0.0
    foreach number $numbers {
        set sum [expr {$sum + $number}]
    }
    return [expr {$sum / $count}]
}

proc factorial {n} {
    if {![string is integer -strict $n] || $n < 0} {
        error "factorial requires a nonnegative integer"
    }
    set result 1
    for {set i 2} {$i <= $n} {incr i} {
        set result [expr {$result * $i}]
    }
    return $result
}

proc two-fer {{name main.c}} {return "C source: $name"}
