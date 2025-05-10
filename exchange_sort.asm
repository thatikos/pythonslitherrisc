# Exchange Sort (Bubble Sort) Benchmark
# Sorts an array of 100 integers in descending order
# This will stress both cache and pipeline due to:
# 1. Multiple memory accesses in the inner loop
# 2. Branch prediction challenges
# 3. Data dependencies between iterations

# Initialize array with values
    MOVI r1, 0x1000   # r1 = array base address
    MOVI r2, 100      # r2 = array size
    MOVI r3, 0        # r3 = counter

init_loop:
    CMP r3, r2
    BEQ init_done     # if counter == size, done
    MOVI r4, 100      # r4 = array size
    SUB r4, r4, r3    # r4 = array size - counter
    STR r4, [r1, r3]  # store (array size - counter) at array[counter]
    ADDI r3, r3, 1    # increment counter
    JMP init_loop

init_done:
    # Start bubble sort
    MOVI r1, 0x1000   # r1 = array base address
    MOVI r2, 100      # r2 = array size
    MOVI r3, 0        # r3 = i (outer loop counter)

outer_loop:
    MOVI r4, 0        # r4 = j (inner loop counter)
    MOVI r5, 100      # r5 = array size
    SUB r5, r5, r3    # r5 = array size - i
    SUBI r5, r5, 1    # r5 = array size - i - 1

inner_loop:
    CMP r4, r5
    BEQ inner_done    # if j == (array size - i - 1), done with inner loop

    # Load array[j] and array[j+1]
    LDR r6, [r1, r4]  # r6 = array[j]
    ADDI r7, r4, 1    # r7 = j + 1
    LDR r8, [r1, r7]  # r8 = array[j+1]

    # Compare and swap if needed
    CMP r6, r8
    BLT no_swap       # if array[j] < array[j+1], no swap needed

    # Swap elements
    STR r8, [r1, r4]  # array[j] = array[j+1]
    STR r6, [r1, r7]  # array[j+1] = array[j]

no_swap:
    ADDI r4, r4, 1    # j++
    JMP inner_loop

inner_done:
    ADDI r3, r3, 1    # i++
    CMP r3, r2
    BLT outer_loop    # if i < array size, continue outer loop

# Sort complete
    MOVI r1, 0xFFFF   # Signal completion with a special value
    MOVI r2, 0        # Store at address 0
    STR r1, [r2, 0]   # This will be detected as the end condition 