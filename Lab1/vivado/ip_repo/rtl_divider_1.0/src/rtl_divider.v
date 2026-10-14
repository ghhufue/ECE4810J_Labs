`timescale 1ns / 1ps
// Unsigned restoring division: one quotient bit per cycle, 16 cycles total.
module rtl_divider(
    input wire clk, input wire resetn, input wire start,
    input wire [15:0] a, input wire [15:0] b,
    output reg [15:0] quotient, output reg [15:0] remainder,
    output reg busy, output reg done, output reg divide_by_zero
);
    reg [15:0] q_work, divisor;
    reg [16:0] r_work;
    reg [4:0] count;
    wire [16:0] shifted = {r_work[15:0], q_work[15]};
    wire subtract = shifted >= {1'b0, divisor};
    wire [16:0] next_r = subtract ? shifted - {1'b0, divisor} : shifted;
    wire [15:0] next_q = {q_work[14:0], subtract};
    always @(posedge clk) begin
        if (!resetn) begin
            quotient <= 0; remainder <= 0;
            busy <= 0; done <= 0; divide_by_zero <= 0;
            q_work <= 0; divisor <= 0; r_work <= 0; count <= 0;
        end else if (start && !busy) begin
            done <= 0;
            divide_by_zero <= (b == 0);
            if (b == 0) begin
                quotient <= 16'hffff;
                remainder <= a;
                done <= 1;
            end else begin
                q_work <= a; divisor <= b; r_work <= 0;
                count <= 16; busy <= 1;
            end
        end else if (busy) begin
            q_work <= next_q; r_work <= next_r; count <= count - 1'b1;
            if (count == 1) begin
                quotient <= next_q; remainder <= next_r[15:0];
                busy <= 0; done <= 1;
            end
        end
    end
endmodule
