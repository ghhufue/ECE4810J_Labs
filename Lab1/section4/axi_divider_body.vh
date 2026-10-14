// Four 32-bit registers: operands, quotient, remainder, status.
// AW and W are buffered independently; only one response is outstanding.
reg aw_pending, w_pending;
reg [C_S_AXI_ADDR_WIDTH-1:0] awaddr;
reg [31:0] wdata;
reg [3:0] wstrb;
reg bvalid;
reg [1:0] bresp;
reg rvalid;
reg [31:0] rdata;
reg [1:0] rresp;
reg [31:0] operands;
wire busy, done, divide_by_zero;
wire [15:0] quotient, remainder;
wire commit = aw_pending && w_pending && !bvalid;
wire valid_input_write = (awaddr == 0) && !busy;
wire start = commit && valid_input_write && (|wstrb);
reg [31:0] merged;
integer byte_index;
always @* begin
    merged = operands;
    for (byte_index = 0; byte_index < 4; byte_index = byte_index + 1)
        if (wstrb[byte_index])
            merged[8*byte_index +: 8] = wdata[8*byte_index +: 8];
end
assign S_AXI_AWREADY = S_AXI_ARESETN && !aw_pending && !bvalid;
assign S_AXI_WREADY = S_AXI_ARESETN && !w_pending && !bvalid;
assign S_AXI_BVALID = bvalid;
assign S_AXI_BRESP = bresp;
assign S_AXI_ARREADY = S_AXI_ARESETN && !rvalid;
assign S_AXI_RVALID = rvalid;
assign S_AXI_RDATA = rdata;
assign S_AXI_RRESP = rresp;
rtl_divider divider_core (
    .clk(S_AXI_ACLK), .resetn(S_AXI_ARESETN), .start(start),
    .a(merged[31:16]), .b(merged[15:0]),
    .quotient(quotient), .remainder(remainder),
    .busy(busy), .done(done), .divide_by_zero(divide_by_zero)
);
always @(posedge S_AXI_ACLK) begin
    if (!S_AXI_ARESETN) begin
        aw_pending <= 0; w_pending <= 0;
        awaddr <= 0; wdata <= 0; wstrb <= 0; operands <= 0;
        bvalid <= 0; bresp <= 0;
        rvalid <= 0; rdata <= 0; rresp <= 0;
    end else begin
        if (S_AXI_AWVALID && S_AXI_AWREADY) begin
            awaddr <= S_AXI_AWADDR; aw_pending <= 1;
        end
        if (S_AXI_WVALID && S_AXI_WREADY) begin
            wdata <= S_AXI_WDATA; wstrb <= S_AXI_WSTRB; w_pending <= 1;
        end
        if (bvalid && S_AXI_BREADY) bvalid <= 0;
        if (commit) begin
            aw_pending <= 0; w_pending <= 0; bvalid <= 1;
            bresp <= valid_input_write ? 2'b00 : 2'b10;
            if (start) operands <= merged;
        end
        if (rvalid && S_AXI_RREADY) rvalid <= 0;
        if (S_AXI_ARVALID && S_AXI_ARREADY) begin
            rvalid <= 1; rresp <= 0;
            case (S_AXI_ARADDR)
                0: rdata <= operands;
                4: rdata <= {16'b0, quotient};
                8: rdata <= {16'b0, remainder};
                12: rdata <= {29'b0, divide_by_zero, done, busy};
                default: begin rdata <= 0; rresp <= 2'b10; end
            endcase
        end
    end
end
endmodule
