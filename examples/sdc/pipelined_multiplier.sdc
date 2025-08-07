# Define a 10ns clock (100 MHz)
create_clock -name clk -period 10 [get_ports clk]

# Set input delay (assumes external environment drives A and B)
set_input_delay 5 -clock clk [get_ports {A B}]

# Set output delay (to external environment)
set_output_delay 5 -clock clk [get_ports result]
