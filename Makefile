.PHONY: all

DEST_PATH = /mnt/c/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test

all:
	yosys run.ys > log.txt
#	python3 python/count_chips_v2.py log.txt
	cp python/netlist.py $(DEST_PATH)/verilog-kicad.py

cp:
	cp python/netlist.py $(DEST_PATH)/verilog-kicad.py
