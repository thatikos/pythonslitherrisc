# Simple test program
# Initialize registers
    addi r1, r0, 10     # Load 10 into r1
    addi r2, r0, 20     # Load 20 into r2

# Do some arithmetic
    add r3, r1, r2      # r3 = r1 + r2 (should be 30)
    sub r4, r2, r1      # r4 = r2 - r1 (should be 10)

# Store results in memory
    addi r5, r0, 0x100  # Load base address
    str r3, [r5, 0]     # Store r3 at base address
    str r4, [r5, 4]     # Store r4 at base + 4

# Load back and verify
    ldr r6, [r5, 0]     # Load first value
    ldr r7, [r5, 4]     # Load second value 