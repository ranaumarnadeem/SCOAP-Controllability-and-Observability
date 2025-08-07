set_db init_lib_search_path /home/advancedresearch/shares/vm_shared/DFT_Research/sky130_scl_9T_0.0.5/sky130_scl_9T_0.0.5/lib
set_db init_hdl_search_path ./designs

read_libs sky130_tt_1.8_25_nldm.lib
read_hdl priority_enc.v
elaborate 
read_sdc ./sdc/priority_encoder.sdc


set_db syn_generic_effort medium
syn_generic
set_db syn_map_effort medium
syn_map
set_db syn_opt_effort medium
syn_opt

syn_opt -incr

write_hdl > synthesized_designs/priority_encoder.v

