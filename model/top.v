// This module models the computer as a whole
// and as such has no IOs. However, future IOs may be
// added for simulating user IO.
`timescale 1us/1us

module top;


// Below are any wires from card external
// IO for debugging purposes
// (nothing here right now)


// The main bus wires (31 total)
wire VCC;
wire GND;
wire clk;			// generated by motherboard clock generator
wire rst_n;			// probably a button on the motherboard
wire we;			// active high
wire oe;			// active high
wire [7:0] data;
wire [15:0] addr;	// 64k address space is suppored by default. More address bits may be added later
wire int_n;			// pulled up by motherboard; driven down by any peripheral (could be used for interrupts)

// Below are where test cards are instantiated
simple_card simple_card0(
	.VCC(VCC),
	.GND(GND),
	.clk(clk),
	.rst_n(rst_n),
	.we(we),
	.oe(oe),
	.data(data),
	.addr(addr),
	.int_n(int_n)
);

cpu_card cpu_card0(
	.VCC(VCC),
	.GND(GND),
	.clk(clk),
	.rst_n(rst_n),
	.we(we),
	.oe(oe),
	.data(data),
	.addr(addr),
	.int_n(int_n)
);

alu_card alu_card0(
	.VCC(VCC),
	.GND(GND),
	.clk(clk),
	.rst_n(rst_n),
	.we(we),
	.oe(oe),
	.data(data),
	.addr(addr),
	.int_n(int_n)
);

// Below is motherboard logic (most of it is simulated and non-synthesizable)
assign VCC = 1'b1;
assign GND = 1'b0;

reg clk_gen, rst_n_gen;
assign clk = clk_gen;
assign rst_n = rst_n_gen;

// clock
initial begin
	clk_gen = 1'b0;
	forever #1 clk_gen = ~clk_gen;
end

// reset
initial begin
	rst_n_gen = 1'b1;
	#2 rst_n_gen = 1'b0;
	#2 rst_n_gen = 1'b1;
end

endmodule