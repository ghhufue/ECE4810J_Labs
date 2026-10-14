`timescale 1ns/1ps
module tb_rtl_divider;
    reg clk = 0, resetn = 0;
    always #5 clk = ~clk;
    reg [3:0] awaddr = 0, araddr = 0;
    reg awvalid = 0, wvalid = 0, bready = 0, arvalid = 0, rready = 0;
    reg [31:0] wdata = 0;
    reg [3:0] wstrb = 0;
    wire awready, wready, bvalid, arready, rvalid;
    wire [1:0] bresp, rresp;
    wire [31:0] rdata;
    integer tests = 0;
    rtl_divider_v1_0_S00_AXI dut (
        .S_AXI_ACLK(clk), .S_AXI_ARESETN(resetn),
        .S_AXI_AWADDR(awaddr), .S_AXI_AWPROT(3'b0),
        .S_AXI_AWVALID(awvalid), .S_AXI_AWREADY(awready),
        .S_AXI_WDATA(wdata), .S_AXI_WSTRB(wstrb),
        .S_AXI_WVALID(wvalid), .S_AXI_WREADY(wready),
        .S_AXI_BRESP(bresp), .S_AXI_BVALID(bvalid), .S_AXI_BREADY(bready),
        .S_AXI_ARADDR(araddr), .S_AXI_ARPROT(3'b0),
        .S_AXI_ARVALID(arvalid), .S_AXI_ARREADY(arready),
        .S_AXI_RDATA(rdata), .S_AXI_RRESP(rresp),
        .S_AXI_RVALID(rvalid), .S_AXI_RREADY(rready)
    );
    task automatic write_reg(input [3:0] addr, input [31:0] data,
                             input [3:0] strb, input integer aw_delay,
                             input integer w_delay, input [1:0] expected_resp);
        fork
            begin
                repeat (aw_delay) @(negedge clk);
                @(negedge clk); awaddr = addr; awvalid = 1;
                do @(posedge clk); while (!awready);
                @(negedge clk); awvalid = 0;
            end
            begin
                repeat (w_delay) @(negedge clk);
                @(negedge clk); wdata = data; wstrb = strb; wvalid = 1;
                do @(posedge clk); while (!wready);
                @(negedge clk); wvalid = 0;
            end
        join
        wait (bvalid);
        repeat (3) begin
            @(negedge clk);
            if (!bvalid || bresp !== expected_resp) $fatal(1, "Write response/backpressure");
        end
        bready = 1;
        @(posedge clk); @(negedge clk); bready = 0;
    endtask
    task automatic read_reg(input [3:0] addr, output [31:0] data,
                            input [1:0] expected_resp);
        @(negedge clk); araddr = addr; arvalid = 1;
        do @(posedge clk); while (!arready);
        @(negedge clk); arvalid = 0;
        wait (rvalid); data = rdata;
        repeat (3) begin
            @(negedge clk);
            if (!rvalid || rdata !== data || rresp !== expected_resp)
                $fatal(1, "Read response/backpressure");
        end
        rready = 1;
        @(posedge clk); @(negedge clk); rready = 0;
    endtask
    task automatic check_result(input [15:0] a, input [15:0] b);
        reg [31:0] status, q, r;
        integer poll_count;
        begin
            status = 0; poll_count = 0;
            while ((status & 3) != 2 && poll_count < 30) begin
                read_reg(12, status, 0); poll_count = poll_count + 1;
            end
            if (poll_count == 30) $fatal(1, "Divider timeout");
            read_reg(4, q, 0); read_reg(8, r, 0);
            if (b == 0) begin
                if (q !== 65535 || r !== {16'b0,a} || status !== 6)
                    $fatal(1, "Divide by zero result");
            end else begin
                if (q !== a/b || r !== a%b || status !== 2)
                    $fatal(1, "%0d/%0d: q=%0d r=%0d status=%0d", a, b, q, r, status);
                if (a != q*b+r || r >= b) $fatal(1, "Division invariant");
            end
            tests = tests + 1;
        end
    endtask
    task automatic test_case(input [15:0] a, input [15:0] b, input integer skew);
        write_reg(0, {a,b}, 15, skew % 3, (skew + 1) % 3, 0);
        check_result(a,b);
    endtask
    reg [31:0] value;
    reg [15:0] a, b;
    integer i;
    initial begin
        repeat (5) @(negedge clk); resetn = 1;
        read_reg(12, value, 0);
        if (value !== 0) $fatal(1, "Reset status");
        test_case(17,5,0); test_case(100,7,1);
        test_case(65535,1,2); test_case(65535,65535,0);
        test_case(65535,255,1); test_case(3,7,2); test_case(0,7,0);
        test_case(32768,3,1); test_case(12345,0,2); test_case(0,0,0);
        test_case(42,6,1);
        for (i=0; i<256; i=i+1) begin
            a = $random; b = $random; test_case(a,b,i);
        end
        // Byte lanes preserve the untouched operand bits.
        test_case(16'h1234,16'h5678,0);
        write_reg(0, 32'h00000005, 1, 3, 0, 0); check_result(16'h1234,16'h5605);
        write_reg(0, 32'h00110000, 12, 0, 3, 0); check_result(17,16'h5605);
        write_reg(0, 32'hdeadbeef, 0, 0, 0, 0);
        read_reg(0,value,0);
        if (value !== 32'h00115605) $fatal(1, "Zero strobe altered operands");
        write_reg(4,0,15,0,2,2); write_reg(8,0,15,2,0,2);
        read_reg(1,value,2);
        // A second operation during busy must be rejected and preserve the first.
        write_reg(0,{16'd65535,16'd7},15,0,0,0);
        write_reg(0,{16'd42,16'd2},15,0,0,2);
        check_result(65535,7);
        // Reset aborts a running operation and flushes pending bus responses.
        write_reg(0,{16'd65535,16'd3},15,0,0,0);
        @(negedge clk); resetn = 0;
        repeat (3) @(negedge clk); resetn = 1;
        read_reg(12,value,0); if (value !== 0) $fatal(1,"Reset during division");
        read_reg(0,value,0); if (value !== 0) $fatal(1,"Reset operands");
        test_case(99,8,2);
        $display("DIVIDER_SIMULATION_PASS: %0d arithmetic cases; AXI skew, backpressure, strobes, busy rejection, reset",tests);
        $finish;
    end
    initial begin #2000000; $fatal(1,"Global simulation timeout"); end
endmodule
