# Combinational inputs – assume max delay of 5ns from driving circuit
set_input_delay 5 [get_ports {in en}]

# Outputs – assume max delay of 5ns to load
set_output_delay 5 [get_ports {out valid}]
