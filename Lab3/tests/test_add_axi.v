`timescale 1ns/1ps
module test_add_axi;
reg clk=0;
always #5 clk=~clk;
reg resetn=0;
reg [5:0] awaddr=0,araddr=0;
reg awvalid=0,wvalid=0,bready=0,arvalid=0,rready=0;
reg [31:0] wdata=0;
reg [3:0] wstrb=15;
wire awready,wready,bvalid,arready,rvalid;
wire [1:0] bresp,rresp;
wire [31:0] rdata;
add dut(.ap_clk(clk),.ap_rst_n(resetn),
 .s_axi_CTRL_AWADDR(awaddr),.s_axi_CTRL_AWVALID(awvalid),.s_axi_CTRL_AWREADY(awready),
 .s_axi_CTRL_WDATA(wdata),.s_axi_CTRL_WSTRB(wstrb),.s_axi_CTRL_WVALID(wvalid),.s_axi_CTRL_WREADY(wready),
 .s_axi_CTRL_BRESP(bresp),.s_axi_CTRL_BVALID(bvalid),.s_axi_CTRL_BREADY(bready),
 .s_axi_CTRL_ARADDR(araddr),.s_axi_CTRL_ARVALID(arvalid),.s_axi_CTRL_ARREADY(arready),
 .s_axi_CTRL_RDATA(rdata),.s_axi_CTRL_RRESP(rresp),.s_axi_CTRL_RVALID(rvalid),.s_axi_CTRL_RREADY(rready));
task write_word(input [5:0] addr,input [31:0] value);
begin
 @(negedge clk); awaddr=addr; awvalid=1;
 @(posedge clk); while(!awready) @(posedge clk);
 @(negedge clk); awvalid=0; wdata=value; wvalid=1;
 @(posedge clk); while(!wready) @(posedge clk);
 @(negedge clk); wvalid=0; bready=1;
 @(posedge clk); while(!bvalid) @(posedge clk);
 if(bresp!==0)$fatal(1,"AXI write response");
 @(negedge clk); bready=0;
end
endtask
task read_word(input [5:0] addr,output [31:0] value);
begin
 @(negedge clk); araddr=addr; arvalid=1;
 @(posedge clk); while(!arready) @(posedge clk);
 @(negedge clk); arvalid=0; rready=1;
 @(posedge clk); while(!rvalid) @(posedge clk);
 if(rresp!==0)$fatal(1,"AXI read response");
 value=rdata;
 @(negedge clk); rready=0;
end
endtask
reg [31:0] vals[0:5];reg [31:0] got;
integer i,j,count=0;
initial begin
 vals[0]=0;vals[1]=1;vals[2]=32'hffffffff;vals[3]=32'h80000000;vals[4]=32'h7fffffff;vals[5]=12345;
 repeat(5)@(negedge clk);resetn=1;
 for(i=0;i<6;i=i+1)for(j=0;j<6;j=j+1)begin
  write_word('h10,vals[i]);write_word('h18,vals[j]);read_word('h20,got);
  if(got!==(vals[i]+vals[j]))$fatal(1,"ADD mismatch: %h + %h = %h",vals[i],vals[j],got);
  count=count+1;
 end
 $display("LAB3_ADD_AXI_PASS: %0d vectors, separated AW/W",count);$finish;
end
initial begin #100000;$fatal(1,"AXI timeout");end
endmodule
