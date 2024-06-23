// bare bones synthesizable module
module test2(
    input [1:0] fs,
	input [15:0] a, b,
    output [15:0] c
);

parameter ADD = 2'd0;
parameter SUB = 2'd1;
parameter XOR = 2'd2;
parameter NAND = 2'd3;

always @(*) begin
    if (fs == ADD) c = a + b;
    else if (fs == SUB) c = a - b;
    else if (fs == XOR) c = a ^ b;
    else if (fs == NAND) c = ~(a & b);
    else c = 8'bx;
end

endmodule
