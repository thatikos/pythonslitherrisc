# Example program for SlitherRISC
# This program demonstrates various instruction types

# Initialize registers
start:
    addi r1, r0, 10     # Load 10 into r1
    addi r2, r0, 20     # Load 20 into r2
    addi r3, r0, 0x100  # Load base address into r3

# Perform some arithmetic
    add r4, r1, r2      # r4 = r1 + r2
    sub r5, r2, r1      # r5 = r2 - r1
    mul r6, r1, r2      # r6 = r1 * r2

# Memory operations
    str r4, [r3, 0]     # Store r4 at base address
    str r5, [r3, 4]     # Store r5 at base + 4
    str r6, [r3, 8]     # Store r6 at base + 8
    ldr r7, [r3, 0]     # Load from base address into r7

# Control flow
loop:
    subi r1, r1, 1      # Decrement r1
    beq done            # Branch to done if r1 is zero
    jmp loop            # Jump back to loop

done:
    addi r8, r0, 0xFF   # Set completion flag 