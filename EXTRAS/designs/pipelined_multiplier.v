module pipelined_mult(
    input clk,
    input [3:0] A, B,
    output reg [7:0] result
);
    reg [3:0] A_reg, B_reg;
    reg [7:0] mult_stage1, mult_stage2;

    always @(posedge clk) begin
        A_reg <= A;
        B_reg <= B;
        mult_stage1 <= A_reg * B_reg;
        mult_stage2 <= mult_stage1;
        result <= mult_stage2;
    end
endmodule
