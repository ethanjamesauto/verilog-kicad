//-----------------------------------------------------
// Design Name : up_counter
// File Name   : up_counter.v
// Function    : Up counter
// Coder      : Deepak
//-----------------------------------------------------
module up_counter    (
out     ,  // Output of the counter
clk     ,  // clock Input
);
//----------Output Ports--------------
    output [7:0] out;
//------------Input Ports--------------
     input clk;
//------------Internal Variables--------
    reg [7:0] out;
//-------------Code Starts Here-------
always @(posedge clk)
  out <= out + 1;


endmodule 
