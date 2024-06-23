.PHONY: all

all:
	yosys run.ys > log.txt
	python3 python/count_chips_v2.py log.txt