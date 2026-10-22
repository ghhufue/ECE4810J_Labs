// Four registers: A @ 0, B @ 4, selector/start @ 8, result @ 12.
// Result reads are held until completion; no software delay is required.
reg aw_pending, w_pending, bvalid, rvalid, busy, start;
reg [C_S_AXI_ADDR_WIDTH-1:0] awaddr;
reg [31:0] wdata, rdata, operand_a, operand_b;
reg [3:0] wstrb;
reg [4:0] selector;
reg [1:0] bresp, rresp;
wire done;
wire [31:0] result;
wire commit = aw_pending && w_pending && !bvalid;
wire write_ok = !busy && awaddr[1:0] == 0 && awaddr <= 8;
integer j;
assign S_AXI_AWREADY = S_AXI_ARESETN && !aw_pending && !bvalid;
assign S_AXI_WREADY = S_AXI_ARESETN && !w_pending && !bvalid;
assign S_AXI_BVALID = bvalid;
assign S_AXI_BRESP = bresp;
assign S_AXI_ARREADY = S_AXI_ARESETN && !rvalid && !busy && !commit;
assign S_AXI_RVALID = rvalid;
assign S_AXI_RDATA = rdata;
assign S_AXI_RRESP = rresp;
rtl_pipe_alu core(
    .clk(S_AXI_ACLK), .resetn(S_AXI_ARESETN), .start(start),
    .opa(operand_a), .opb(operand_b), .func(selector), .result(result), .done(done)
);
always @(posedge S_AXI_ACLK) begin
    if (!S_AXI_ARESETN) begin
        aw_pending <= 0; w_pending <= 0; bvalid <= 0; rvalid <= 0;
        busy <= 0; start <= 0; operand_a <= 0; operand_b <= 0; selector <= 0;
        awaddr <= 0; wdata <= 0; wstrb <= 0; rdata <= 0; bresp <= 0; rresp <= 0;
    end else begin
        start <= 0;
        if (done) busy <= 0;
        if (S_AXI_AWVALID && S_AXI_AWREADY) begin aw_pending <= 1; awaddr <= S_AXI_AWADDR; end
        if (S_AXI_WVALID && S_AXI_WREADY) begin w_pending <= 1; wdata <= S_AXI_WDATA; wstrb <= S_AXI_WSTRB; end
        if (bvalid && S_AXI_BREADY) bvalid <= 0;
        if (commit) begin
            aw_pending <= 0; w_pending <= 0; bvalid <= 1;
            bresp <= write_ok ? 2'b00 : 2'b10;
            if (write_ok) begin
                for (j=0;j<4;j=j+1) begin
                    if (wstrb[j] && awaddr == 0) operand_a[j*8+:8] <= wdata[j*8+:8];
                    if (wstrb[j] && awaddr == 4) operand_b[j*8+:8] <= wdata[j*8+:8];
                end
                if (awaddr == 8 && wstrb[0]) begin
                    selector <= wdata[4:0]; start <= 1; busy <= 1;
                end
            end
        end
        if (rvalid && S_AXI_RREADY) rvalid <= 0;
        if (S_AXI_ARVALID && S_AXI_ARREADY) begin
            rvalid <= 1; rresp <= 0;
            case (S_AXI_ARADDR)
                0: rdata <= operand_a;
                4: rdata <= operand_b;
                8: rdata <= {27'b0,selector};
                12: rdata <= result;
                default: begin rdata <= 0; rresp <= 2'b10; end
            endcase
        end
    end
end
endmodule
