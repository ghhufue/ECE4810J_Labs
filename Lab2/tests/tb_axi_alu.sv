`timescale 1ns/1ps
module tb_axi_alu;
    logic clk=0,resetn=0;
    logic [3:0] awaddr=0,araddr=0;
    logic awvalid=0,wvalid=0,bready=0,arvalid=0,rready=0;
    wire awready,wready,bvalid,arready,rvalid;
    logic [31:0] wdata=0;
    logic [3:0] wstrb=0;
    wire [31:0] rdata;
    wire [1:0] bresp,rresp;
    reg [127:0] vectors[0:7508];
    reg [31:0] value, a,b,op,expected;
    integer i;
    always #5 clk=~clk;
    rtl_pipe_alu_v1_0_S00_AXI dut(
        .S_AXI_ACLK(clk),.S_AXI_ARESETN(resetn),
        .S_AXI_AWADDR(awaddr),.S_AXI_AWPROT(3'b0),.S_AXI_AWVALID(awvalid),.S_AXI_AWREADY(awready),
        .S_AXI_WDATA(wdata),.S_AXI_WSTRB(wstrb),.S_AXI_WVALID(wvalid),.S_AXI_WREADY(wready),
        .S_AXI_BRESP(bresp),.S_AXI_BVALID(bvalid),.S_AXI_BREADY(bready),
        .S_AXI_ARADDR(araddr),.S_AXI_ARPROT(3'b0),.S_AXI_ARVALID(arvalid),.S_AXI_ARREADY(arready),
        .S_AXI_RDATA(rdata),.S_AXI_RRESP(rresp),.S_AXI_RVALID(rvalid),.S_AXI_RREADY(rready)
    );
    task automatic write_reg(input [3:0] addr,input [31:0] data,input [3:0] strobe,
                             input integer adelay,input integer ddelay,input [1:0] response);
        fork
            begin
                repeat(adelay) @(negedge clk);
                @(negedge clk); awaddr=addr; awvalid=1;
                @(posedge clk); while (!awready) @(posedge clk);
                @(negedge clk); awvalid=0;
            end
            begin
                repeat(ddelay) @(negedge clk);
                @(negedge clk); wdata=data; wstrb=strobe; wvalid=1;
                @(posedge clk); while (!wready) @(posedge clk);
                @(negedge clk); wvalid=0;
            end
        join
        while (!bvalid) @(negedge clk);
        repeat(3) begin
            @(negedge clk);
            if (!bvalid || bresp!==response) $fatal(1,"B response lost/incorrect addr=%h got=%b",addr,bresp);
        end
        bready=1;
        @(negedge clk); bready=0;
    endtask
    task automatic read_reg(input [3:0] addr,output [31:0] data,input [1:0] response);
        reg [31:0] held;
        begin
            @(negedge clk); araddr=addr; arvalid=1;
            @(posedge clk); while (!arready) @(posedge clk);
            @(negedge clk); arvalid=0;
            while (!rvalid) @(negedge clk);
            held=rdata;
            repeat(3) begin
                @(negedge clk);
                if (!rvalid || rresp!==response || rdata!==held) $fatal(1,"R response changed under backpressure");
            end
            data=rdata; rready=1;
            @(negedge clk); rready=0;
        end
    endtask
    initial begin
        $readmemh("../../tests/alu_vectors.hex",vectors);
        repeat(3) @(negedge clk);
        resetn=1;
        for (i=0;i<7509;i=i+1) begin
            {op,a,b,expected}=vectors[i];
            write_reg(0,a,15,i%3,0,0);
            write_reg(4,b,15,0,i%3,0);
            write_reg(8,op,15,0,0,0);
            read_reg(12,value,0);
            if (value!==expected) $fatal(1,"AXI result mismatch i=%0d op=%0d expected=%h got=%h",i,op,expected,value);
        end
        write_reg(0,32'h12345678,15,0,0,0);
        write_reg(0,32'haabbccdd,5,0,3,0);
        read_reg(0,value,0);
        if (value!==32'h12bb56dd) $fatal(1,"Byte write failed");
        write_reg(0,32'hffffffff,0,3,0,0);
        read_reg(0,value,0);
        if (value!==32'h12bb56dd) $fatal(1,"Zero strobe altered operand");
        write_reg(12,0,15,0,0,2);
        write_reg(1,0,15,0,0,2);
        read_reg(1,value,2);
        // A write during a division must fail and preserve its operands/result.
        write_reg(0,100,15,0,0,0);
        write_reg(4,3,15,0,0,0);
        write_reg(8,14,15,0,0,0);
        write_reg(0,999,15,0,0,2);
        read_reg(12,value,0);
        if (value!==33) $fatal(1,"Busy write corrupted division");
        // Selector with no byte enables must not launch anything.
        write_reg(8,0,0,0,0,0);
        read_reg(12,value,0);
        if (value!==33) $fatal(1,"Zero strobe started operation");
        // Reset clears both an incomplete transaction and its pipeline.
        write_reg(8,14,15,0,0,0);
        @(negedge clk); resetn=0;
        repeat(3) @(negedge clk);
        resetn=1;
        read_reg(12,value,0);
        if (value!==0) $fatal(1,"Reset result was not zero");
        repeat(40) @(negedge clk);
        read_reg(12,value,0);
        if (value!==0) $fatal(1,"Stale pipeline result after reset");
        $display("AXI_ALU_PASS: 7509 vectors; independent AW/W, B/R backpressure, byte strobes, access errors, busy rejection, reset PASS");
        $finish;
    end
    initial begin #20000000; $fatal(1,"AXI test timeout"); end
endmodule
