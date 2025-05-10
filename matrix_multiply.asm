# Matrix Multiply Benchmark
# Multiplies two 10x10 matrices
# This will stress both cache and pipeline due to:
# 1. Regular memory access patterns
# 2. High computational intensity
# 3. Nested loops with data dependencies

# Initialize matrices A and B
    # Initialize matrix A with values 1 to 100
    MOVI r1, 0x1000  # r1 = matrix A base address
    MOVI r2, 10      # r2 = matrix size
    MOVI r3, 0       # r3 = i (row counter)
    MOVI r4, 0       # r4 = j (column counter)
    MOVI r5, 1       # r5 = value to store

init_matrix_a:
    CMP r3, r2
    BEQ init_matrix_b       # if i == size, done with A
    
    # Calculate address: A[i][j] = A + (i * size + j) * 4
    MUL r6, r3, r2         # r6 = i * size
    ADD r6, r6, r4         # r6 = i * size + j
    MUL r6, r6, 4          # r6 = (i * size + j) * 4
    ADD r6, r1, r6         # r6 = A + (i * size + j) * 4
    
    STR r5, [r6, 0]        # store value in A[i][j]
    ADDI r5, r5, 1         # increment value
    ADDI r4, r4, 1         # j++
    
    CMP r4, r2
    BLT init_matrix_a      # if j < size, continue row
    MOVI r4, 0             # reset j to 0
    ADDI r3, r3, 1         # i++
    JMP init_matrix_a

init_matrix_b:
    # Initialize matrix B with values 1 to 100
    MOVI r1, 0x1400  # r1 = matrix B base address
    MOVI r3, 0       # r3 = i (row counter)
    MOVI r4, 0       # r4 = j (column counter)
    MOVI r5, 1       # r5 = value to store

init_matrix_b_loop:
    CMP r3, r2
    BEQ matrix_multiply    # if i == size, done with B
    
    # Calculate address: B[i][j] = B + (i * size + j) * 4
    MUL r6, r3, r2         # r6 = i * size
    ADD r6, r6, r4         # r6 = i * size + j
    MUL r6, r6, 4          # r6 = (i * size + j) * 4
    ADD r6, r1, r6         # r6 = B + (i * size + j) * 4
    
    STR r5, [r6, 0]        # store value in B[i][j]
    ADDI r5, r5, 1         # increment value
    ADDI r4, r4, 1         # j++
    
    CMP r4, r2
    BLT init_matrix_b_loop # if j < size, continue row
    MOVI r4, 0             # reset j to 0
    ADDI r3, r3, 1         # i++
    JMP init_matrix_b_loop

matrix_multiply:
    # Matrix multiplication: C = A * B
    MOVI r1, 0x1000  # r1 = matrix A base address
    MOVI r2, 0x1400  # r2 = matrix B base address
    MOVI r3, 0x1800  # r3 = matrix C base address
    MOVI r4, 10      # r4 = matrix size
    MOVI r5, 0       # r5 = i (row counter)

outer_loop:
    CMP r5, r4
    BEQ done                # if i == size, done
    MOVI r6, 0              # r6 = j (column counter)

middle_loop:
    CMP r6, r4
    BEQ next_row           # if j == size, next row
    MOVI r7, 0              # r7 = k (inner loop counter)
    MOVI r8, 0              # r8 = sum (accumulator)

inner_loop:
    CMP r7, r4
    BEQ store_result      # if k == size, store result
    
    # Calculate A[i][k] address
    MUL r9, r5, r4        # r9 = i * size
    ADD r9, r9, r7        # r9 = i * size + k
    MUL r9, r9, 4         # r9 = (i * size + k) * 4
    ADD r9, r1, r9        # r9 = A + (i * size + k) * 4
    LDR r10, [r9, 0]      # r10 = A[i][k]
    
    # Calculate B[k][j] address
    MUL r11, r7, r4       # r11 = k * size
    ADD r11, r11, r6      # r11 = k * size + j
    MUL r11, r11, 4       # r11 = (k * size + j) * 4
    ADD r11, r2, r11      # r11 = B + (k * size + j) * 4
    LDR r12, [r11, 0]     # r12 = B[k][j]
    
    # Multiply and add to sum
    MUL r10, r10, r12     # r10 = A[i][k] * B[k][j]
    ADD r8, r8, r10       # sum += A[i][k] * B[k][j]
    
    ADDI r7, r7, 1        # k++
    JMP inner_loop

store_result:
    # Calculate C[i][j] address
    MUL r9, r5, r4        # r9 = i * size
    ADD r9, r9, r6        # r9 = i * size + j
    MUL r9, r9, 4         # r9 = (i * size + j) * 4
    ADD r9, r3, r9        # r9 = C + (i * size + j) * 4
    STR r8, [r9, 0]       # C[i][j] = sum
    
    ADDI r6, r6, 1        # j++
    JMP middle_loop

next_row:
    ADDI r5, r5, 1        # i++
    JMP outer_loop

done:
    FLUSH r0              # Halt the processor 