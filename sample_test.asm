# Memory test program for SlitherRISC
# Tests memory operations by writing different values to multiple locations

# First, set up some test values in registers
ADDI r1, r0, 0x42    # r1 = 0x42 (first value to store)
ADDI r2, r0, 0x100   # r2 = 0x100 (base memory address)
ADDI r3, r0, 0xFF    # r3 = 0xFF (second value to store)

# Store values at different memory locations
STR r1, [r2, 0]      # store 0x42 at memory[0x100]
STR r3, [r2, 4]      # store 0xFF at memory[0x104]
ADDI r4, r0, 0x55    # r4 = 0x55 (third value)
STR r4, [r2, 8]      # store 0x55 at memory[0x108]

# Read back values to verify
LDR r5, [r2, 0]      # r5 should get 0x42 from memory[0x100]
LDR r6, [r2, 4]      # r6 should get 0xFF from memory[0x104]
LDR r7, [r2, 8]      # r7 should get 0x55 from memory[0x108]
