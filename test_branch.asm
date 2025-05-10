# Test program for branch instructions
start:
    addi r1, 5          # Initialize counter to 5
loop:
    subi r1, 1          # Decrement counter
    beq done            # Branch to done if zero
    jmp r0              # Jump back to loop
done:
    addi r2, 0xFF       # Set completion flag 