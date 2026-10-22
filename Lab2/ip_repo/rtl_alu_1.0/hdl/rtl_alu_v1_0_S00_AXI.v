
`timescale 1 ns / 1 ps

	module rtl_alu_v1_0_S00_AXI #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line

		// Width of S_AXI data bus
		parameter integer C_S_AXI_DATA_WIDTH	= 32,
		// Width of S_AXI address bus
		parameter integer C_S_AXI_ADDR_WIDTH	= 4
	)
	(
		// Users to add ports here

		// User ports ends
		// Do not modify the ports beyond this line

		// Global Clock Signal
		input wire  S_AXI_ACLK,
		// Global Reset Signal. This Signal is Active LOW
		input wire  S_AXI_ARESETN,
		// Write address (issued by master, acceped by Slave)
		input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_AWADDR,
		// Write channel Protection type. This signal indicates the
    		// privilege and security level of the transaction, and whether
    		// the transaction is a data access or an instruction access.
		input wire [2 : 0] S_AXI_AWPROT,
		// Write address valid. This signal indicates that the master signaling
    		// valid write address and control information.
		input wire  S_AXI_AWVALID,
		// Write address ready. This signal indicates that the slave is ready
    		// to accept an address and associated control signals.
		output wire  S_AXI_AWREADY,
		// Write data (issued by master, acceped by Slave) 
		input wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_WDATA,
		// Write strobes. This signal indicates which byte lanes hold
    		// valid data. There is one write strobe bit for each eight
    		// bits of the write data bus.    
		input wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] S_AXI_WSTRB,
		// Write valid. This signal indicates that valid write
    		// data and strobes are available.
		input wire  S_AXI_WVALID,
		// Write ready. This signal indicates that the slave
    		// can accept the write data.
		output wire  S_AXI_WREADY,
		// Write response. This signal indicates the status
    		// of the write transaction.
		output wire [1 : 0] S_AXI_BRESP,
		// Write response valid. This signal indicates that the channel
    		// is signaling a valid write response.
		output wire  S_AXI_BVALID,
		// Response ready. This signal indicates that the master
    		// can accept a write response.
		input wire  S_AXI_BREADY,
		// Read address (issued by master, acceped by Slave)
		input wire [C_S_AXI_ADDR_WIDTH-1 : 0] S_AXI_ARADDR,
		// Protection type. This signal indicates the privilege
    		// and security level of the transaction, and whether the
    		// transaction is a data access or an instruction access.
		input wire [2 : 0] S_AXI_ARPROT,
		// Read address valid. This signal indicates that the channel
    		// is signaling valid read address and control information.
		input wire  S_AXI_ARVALID,
		// Read address ready. This signal indicates that the slave is
    		// ready to accept an address and associated control signals.
		output wire  S_AXI_ARREADY,
		// Read data (issued by slave)
		output wire [C_S_AXI_DATA_WIDTH-1 : 0] S_AXI_RDATA,
		// Read response. This signal indicates the status of the
    		// read transfer.
		output wire [1 : 0] S_AXI_RRESP,
		// Read valid. This signal indicates that the channel is
    		// signaling the required read data.
		output wire  S_AXI_RVALID,
		// Read ready. This signal indicates that the master can
    		// accept the read data and response information.
		input wire  S_AXI_RREADY
	);

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
reg done_reg;
reg [31:0] held_result;
wire [31:0] combinational_result;
rtl_alu core(
    .clk(S_AXI_ACLK), .opa(operand_a), .opb(operand_b),
    .func(ALU_FUNC'(selector)), .result(combinational_result)
);
assign done = done_reg;
assign result = held_result;
always @(posedge S_AXI_ACLK) begin
    if (!S_AXI_ARESETN) begin done_reg <= 0; held_result <= 0; end
    else begin
        done_reg <= start;
        if (start) held_result <= combinational_result;
    end
end
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
