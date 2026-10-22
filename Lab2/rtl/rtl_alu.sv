`timescale 1ns/1ps
// Selector values match lab2_starter/rtl_alu.sv and the lab manual.
typedef enum logic [4:0] {
    ALU_ADD=0, ALU_SUB=1, ALU_SLT=2, ALU_SLTU=3,
    ALU_AND=4, ALU_OR=5, ALU_XOR=6, ALU_SLL=7,
    ALU_SRL=8, ALU_SRA=9, ALU_MUL=10, ALU_MULH=11,
    ALU_MULHSU=12, ALU_MULHU=13, ALU_DIV=14, ALU_DIVU=15,
    ALU_REM=16, ALU_REMU=17
} ALU_FUNC;

module rtl_alu(
    input wire clk,
    input wire [31:0] opa, opb,
    input ALU_FUNC func,
    output logic [31:0] result
);
    wire [63:0] unsigned_mul = {32'b0, opa} * {32'b0, opb};
    wire [31:0] mixed_high = unsigned_mul[63:32] - (opa[31] ? opb : 32'b0);
    wire [31:0] signed_high = mixed_high - (opb[31] ? opa : 32'b0);
    wire signed_op = (func == ALU_DIV || func == ALU_REM);
    wire neg_a = signed_op && opa[31];
    wire neg_b = signed_op && opb[31];
    wire [31:0] magnitude_a = neg_a ? -opa : opa;
    wire [31:0] magnitude_b = neg_b ? -opb : opb;
    wire [31:0] quotient_mag = magnitude_a / magnitude_b;
    wire [31:0] remainder_mag = magnitude_a % magnitude_b;
    wire [31:0] quotient = (opb == 0) ? 32'hffffffff :
                          ((neg_a ^ neg_b) ? -quotient_mag : quotient_mag);
    wire [31:0] remainder = (opb == 0) ? opa :
                           (neg_a ? -remainder_mag : remainder_mag);
    // Section 2 baseline is combinational; clk is retained for starter compatibility.
    always_comb begin
        result = 32'b0;
        case (func)
        ALU_ADD: result = opa + opb;
        ALU_SUB: result = opa - opb;
        ALU_SLT: result = {31'b0, $signed(opa) < $signed(opb)};
        ALU_SLTU: result = {31'b0, opa < opb};
        ALU_AND: result = opa & opb;
        ALU_OR: result = opa | opb;
        ALU_XOR: result = opa ^ opb;
        ALU_SLL: result = opa << opb[4:0];
        ALU_SRL: result = opa >> opb[4:0];
        ALU_SRA: result = $signed(opa) >>> opb[4:0];
        ALU_MUL: result = unsigned_mul[31:0];
        ALU_MULH: result = signed_high;
        ALU_MULHSU: result = mixed_high;
        ALU_MULHU: result = unsigned_mul[63:32];
        ALU_DIV, ALU_DIVU: result = quotient;
        ALU_REM, ALU_REMU: result = remainder;
        default: result = 32'b0;
        endcase
    end
endmodule
