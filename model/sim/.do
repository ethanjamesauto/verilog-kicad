vlib work
vlog ../*.v
vopt +acc top -o top_opt
vsim top_opt
add wave *
run 100us