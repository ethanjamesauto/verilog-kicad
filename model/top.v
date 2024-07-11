// This module models the computer as a whole
// and as such has no IOs. However, future IOs may be
// added for simulating user IO.
`timescale 1us/1ns

module top;


// Below are any wires from card external
// IO for debugging purposes
// (nothing here right now)


// The main bus wires (31 total)
wire VCC;
wire GND;
reg  clk;			// generated by motherboard clock generator
reg  rst_n;			// probably a button on the motherboard
wire we;			// active high
wire oe;			// active high
wire [7:0] data;
wire [15:0] addr;	// 64k address space is suppored by default. More address bits may be added later
wire int_n;			// pulled up by motherboard; driven down by any peripheral (could be used for interrupts)

// Below are where test cards are instantiated
// (nothing here right now)


// Below is motherboard logic (most of it is simulated and non-synthesizable)
assign VCC = 1'b1;
assign GND = 1'b0;

// clock
initial begin
	clk = 1'b0;
	forever #1 clk = ~clk;
end

// reset
initial begin
	rst_n = 1'b1;
	#2 rst_n = 1'b0;
	#2 rst_n = 1'b1;
end




endmodule