module serial_alu(
    input clk, reset,
    input [3:0] A, B,
    input [1:0] opcode, // 00=ADD, 01=SUB, 10=AND, 11=OR
    output reg [3:0] result,
    output reg zero, carry
);
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            result <= 0;
            carry <= 0;
            zero <= 0;
        end else begin
            case (opcode)
                2'b00: {carry, result} <= A + B;
                2'b01: {carry, result} <= A - B;
                2'b10: result <= A & B;
                2'b11: result <= A | B;
            endcase
            zero <= (result == 0);
        end
    end
    endmodule
/*
    // Simulation-only block
    `ifdef COCOTB_SIM
    initial begin
        $dumpfile("serial_alu.vcd");
        $dumpvars(0, serial_alu);
        #100 $finish;
    end
    `endif
endmodule
*/