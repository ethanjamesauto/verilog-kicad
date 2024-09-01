// bare bones synthesizable module
module test2(
    input [1:0] fs,
	input [7:0] a, b,
    output [7:0] c,
    input clk
);

parameter ADD = 2'd0;
parameter SUB = 2'd1;
parameter XOR = 2'd2;
parameter NAND = 2'd3;

always @(posedge clk) begin
    if (fs == 2'd0) c = a + b;
    else if (fs == 2'd1) c = a << 1;
    else if (fs == 2'd2) c = a >> 1;
    //else if (fs == SUB) c = a - b;
    //else if (fs == XOR) c = a ^ b;
    else if (fs == 2'd3) c = ~(a & b);
    else c = 8'dx;
end

endmodule
