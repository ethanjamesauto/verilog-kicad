// bare bones synthesizable module
module test_tmp(
	input  [7:0] a,
	input  [7:0] b,
	output [7:0] c
);

always @(*) c = a + b;

endmodule

module test(
	input  [7:0] x,
	input  [2:0] sel,
	input dir,
	output [7:0] y
);

integer i;
always @(*) begin
	for (i = 0; i < 8; i = i + 1) begin
		if (i < sel) begin
			// if (dir) x = {x << 1, x[7]};
			// else     x = {x[0], x >> 1};
			if (dir) x = x << 1;
			else     x = x >> 1;
		end
	end
	y = x;
end

endmodule
