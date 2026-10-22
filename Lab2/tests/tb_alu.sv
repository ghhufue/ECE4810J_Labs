`timescale 1ns/1ps
module tb_alu;
    logic clk=0, resetn=0, start=0;
    logic [31:0] a=0,b=0;
    logic [4:0] op=0;
    wire [31:0] baseline_result, pipe_result;
    wire done;
    reg [127:0] vectors[0:7508];
    reg [31:0] expected;
    integer i, cycles;
    always #5 clk=~clk;
    rtl_alu baseline(clk,a,b,ALU_FUNC'(op),baseline_result);
    rtl_pipe_alu pipelined(clk,resetn,start,a,b,op,pipe_result,done);
    initial begin
        $readmemh("../../tests/alu_vectors.hex",vectors);
        repeat (3) @(negedge clk);
        resetn=1;
        for (i=0;i<7509;i=i+1) begin
            @(negedge clk);
            {op,a,b,expected} = {vectors[i][100:96],vectors[i][95:0]};
            start=1;
            #1;
            if (baseline_result !== expected)
                $fatal(1,"Baseline mismatch i=%0d op=%0d a=%h b=%h expected=%h actual=%h",i,op,a,b,expected,baseline_result);
            @(negedge clk);
            start=0;
            cycles=0;
            while (!done && cycles<40) begin
                @(negedge clk);
                cycles=cycles+1;
            end
            if (!done || pipe_result !== expected)
                $fatal(1,"Pipeline mismatch i=%0d op=%0d a=%h b=%h expected=%h actual=%h done=%b",i,op,a,b,expected,pipe_result,done);
        end
        // Reset must discard a partially executed division.
        @(negedge clk); a=12345; b=7; op=14; start=1;
        @(negedge clk); start=0;
        repeat (7) @(negedge clk);
        resetn=0;
        repeat (2) @(negedge clk);
        resetn=1;
        repeat (40) begin
            @(negedge clk);
            if (done) $fatal(1,"Stale completion after reset");
        end
        $display("RTL_ALU_PASS: 7509 baseline + 7509 pipeline vectors; reset cancellation PASS");
        $finish;
    end
    initial begin #10000000; $fatal(1,"Test timeout"); end
endmodule
