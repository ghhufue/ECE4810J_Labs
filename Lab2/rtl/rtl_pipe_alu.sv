`timescale 1ns/1ps
// Timing-safe hardware implementation used by the boot image. The Section 2
// combinational reference remains in rtl_alu.sv. One request may be outstanding.
module rtl_pipe_alu(
    input wire clk, resetn, start,
    input wire [31:0] opa, opb,
    input wire [4:0] func,
    output logic [31:0] result,
    output logic done
);
    wire signed_div = func == 14 || func == 16;
    wire neg_a = signed_div && opa[31];
    wire neg_b = signed_div && opb[31];
    logic [31:0] divisor [0:32];
    logic [31:0] quotient [0:32];
    logic [32:0] remainder [0:32];
    logic [32:0] valid, sign_q, sign_r, want_rem, zero_div;
    logic [31:0] original_a [0:32];
    logic [63:0] mul_product;
    logic [31:0] mul_a, mul_b;
    logic [4:0] mul_func;
    logic mul_valid;
    logic [31:0] simple_result;

    always_comb begin
        simple_result = 0;
        case (func)
            0: simple_result = opa + opb;
            1: simple_result = opa - opb;
            2: simple_result = {31'b0,$signed(opa) < $signed(opb)};
            3: simple_result = {31'b0,opa < opb};
            4: simple_result = opa & opb;
            5: simple_result = opa | opb;
            6: simple_result = opa ^ opb;
            7: simple_result = opa << opb[4:0];
            8: simple_result = opa >> opb[4:0];
            9: simple_result = $signed(opa) >>> opb[4:0];
            default: simple_result = 0;
        endcase
    end

    always_ff @(posedge clk) begin
        if (!resetn) begin
            valid[0] <= 0;
            mul_valid <= 0;
            done <= 0;
            result <= 0;
        end else begin
            valid[0] <= start && func >= 14 && func <= 17;
            mul_valid <= start && func >= 10 && func <= 13;
            done <= 0;
            if (start) begin
                divisor[0] <= neg_b ? -opb : opb;
                quotient[0] <= neg_a ? -opa : opa;
                remainder[0] <= 0;
                sign_q[0] <= neg_a ^ neg_b;
                sign_r[0] <= neg_a;
                want_rem[0] <= func == 16 || func == 17;
                zero_div[0] <= opb == 0;
                original_a[0] <= opa;
                mul_product <= {32'b0,opa} * {32'b0,opb};
                mul_a <= opa;
                mul_b <= opb;
                mul_func <= func;
                if (func < 10 || func > 17) begin
                    result <= simple_result;
                    done <= 1;
                end
            end
            if (mul_valid) begin
                case (mul_func)
                    10: result <= mul_product[31:0];
                    11: result <= mul_product[63:32] - (mul_a[31] ? mul_b : 0) - (mul_b[31] ? mul_a : 0);
                    12: result <= mul_product[63:32] - (mul_a[31] ? mul_b : 0);
                    13: result <= mul_product[63:32];
                    default: result <= 0;
                endcase
                done <= 1;
            end
            if (valid[32]) begin
                if (zero_div[32]) result <= want_rem[32] ? original_a[32] : 32'hffffffff;
                else if (want_rem[32]) result <= sign_r[32] ? -remainder[32][31:0] : remainder[32][31:0];
                else result <= sign_q[32] ? -quotient[32] : quotient[32];
                done <= 1;
            end
        end
    end
    for (genvar i=0; i<32; i=i+1) begin: divide_stage
        wire [32:0] trial = {remainder[i][31:0],quotient[i][31]};
        wire take = trial >= {1'b0,divisor[i]};
        always_ff @(posedge clk) begin
            if (!resetn) valid[i+1] <= 0;
            else begin
                valid[i+1] <= valid[i];
                if (valid[i]) begin
                    divisor[i+1] <= divisor[i];
                    remainder[i+1] <= take ? trial - {1'b0,divisor[i]} : trial;
                    quotient[i+1] <= {quotient[i][30:0],take};
                    sign_q[i+1] <= sign_q[i];
                    sign_r[i+1] <= sign_r[i];
                    want_rem[i+1] <= want_rem[i];
                    zero_div[i+1] <= zero_div[i];
                    original_a[i+1] <= original_a[i];
                end
            end
        end
    end
endmodule
