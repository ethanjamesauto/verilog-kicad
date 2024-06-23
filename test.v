// bare bones synthesizable module
module test(
	input a,
	input b,
	output c
);

always @(*) c = a ^ b;

endmodule
