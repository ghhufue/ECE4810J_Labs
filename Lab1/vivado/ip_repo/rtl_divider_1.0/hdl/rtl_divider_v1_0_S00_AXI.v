
`timescale 1 ns / 1 ps

	module rtl_divider_v1_0_S00_AXI #
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
