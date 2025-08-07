# Define a 10ns clock (100 MHz)
create_clock -name clk -period 10 [get_ports clk]

# Set input delay from external source (5ns setup time)
set_input_delay 5 -clock clk [get_ports {A B opcode reset}]

# Set output delay to external sink (5ns hold time)
set_output_delay 5 -clock clk [get_ports {result zero carry}]
