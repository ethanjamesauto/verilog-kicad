# Current Bus spec
```verilog
// The main bus wires (32+8=40 wires total)
// On the bus connector, all buses have LSBs closer to the power pins and MSBs farther away
wire VCC_5V;
wire GND;
wire clk;			      // generated by motherboard clock generator
wire rst_n;			    // probably a button on the motherboard
wire VCC_3V3;
wire we;			      // active high
wire oe;			      // active high
wire int_n;			    // pulled up by motherboard; driven down by any peripheral (could be used for interrupts)
wire [7:0] data;
wire [15:0] addr;	  // 64k address space is suppored by default. More address bits may be added later
wire [7:0] aux_bus;
```

# Verilog to Kicad Converter
and card-based computer project

### Some notes:
* Yosys fully supports only Verilog - VHDL and SV are supported with some extensions, but I haven't tested these
* It seems like yosys can only map to individual gates on 74-series chips as well as single flops on 74x273
* It's going to be necessary to recursively elaborate and search for 74-series chips probably
