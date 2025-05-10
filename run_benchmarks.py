# Add this to run_benchmarks.py before loading benchmarks
import os
os.makedirs('benchmarks', exist_ok=True)

import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path to import simulator modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import MemorySystem
from pipeline import Pipeline, PipelineStage
from registers import RegisterFile
from assembler import assemble_file
from isa import Instruction

class BenchmarkRunner:
    def __init__(self):
        self.results = {}
        self.benchmarks = {
            'exchange_sort': 'benchmarks/exchange_sort.asm',
            'matrix_multiply': 'benchmarks/matrix_multiply.asm'
        }
        self.modes = {
            'no_cache_no_pipe': {'cache_enabled': False, 'pipeline_enabled': False},
            'cache_only': {'cache_enabled': True, 'pipeline_enabled': False},
            'pipe_only': {'cache_enabled': False, 'pipeline_enabled': True},
            'cache_and_pipe': {'cache_enabled': True, 'pipeline_enabled': True}
        }
        
        # Create benchmarks directory if it doesn't exist
        os.makedirs('benchmarks', exist_ok=True)
        
        # Write exchange sort benchmark if it doesn't exist
        if not os.path.exists(self.benchmarks['exchange_sort']):
            with open(self.benchmarks['exchange_sort'], 'w') as f:
                f.write(self.get_exchange_sort_code())
                
        # Write matrix multiply benchmark if it doesn't exist
        if not os.path.exists(self.benchmarks['matrix_multiply']):
            with open(self.benchmarks['matrix_multiply'], 'w') as f:
                f.write(self.get_matrix_multiply_code())

    def get_exchange_sort_code(self):
        """Return the exchange sort benchmark code."""
        return """# Exchange Sort (Bubble Sort) Benchmark
# Sorts an array of 100 integers in descending order

# Initialize array with values
    MOVI r1, 0x100    # r1 = array base address (reduced from 0x1000)
    MOVI r2, 10       # r2 = array size (reduced from 100)
    MOVI r3, 0        # r3 = counter

init_loop:
    CMP r3, r2
    BEQ init_done     # if counter == size, done
    MOVI r4, 10       # r4 = array size
    SUB r4, r4, r3    # r4 = array size - counter
    STR r4, [r1, r3]  # store (array size - counter) at array[counter]
    ADDI r3, r3, 1    # increment counter
    JMP init_loop

init_done:
    # Start bubble sort
    MOVI r1, 0x100    # r1 = array base address
    MOVI r2, 10       # r2 = array size
    MOVI r3, 0        # r3 = i (outer loop counter)

outer_loop:
    MOVI r4, 0        # r4 = j (inner loop counter)
    MOVI r5, 10       # r5 = array size
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
"""

    def get_matrix_multiply_code(self):
        """Return the matrix multiply benchmark code."""
        return """# Matrix Multiplication Benchmark
# Multiplies two 4x4 matrices

# Initialize matrices at addresses 0x100 and 0x200
# Result will be at address 0x300
    MOVI r1, 0x100    # r1 = matrix A base address
    MOVI r2, 0x200    # r2 = matrix B base address
    MOVI r3, 0x300    # r3 = matrix C (result) base address
    
    # Initialize matrix A with values 1,2,3,4...
    MOVI r4, 0        # r4 = counter
    MOVI r5, 16       # r5 = total elements (4x4)
init_a_loop:
    CMP r4, r5
    BEQ init_b        # if counter == 16, done with A
    ADDI r6, r4, 1    # r6 = counter + 1
    STR r6, [r1, r4]  # store counter+1 at A[counter]
    ADDI r4, r4, 1    # increment counter
    JMP init_a_loop

init_b:
    # Initialize matrix B with values 1,1,1,1...
    MOVI r4, 0        # r4 = counter
init_b_loop:
    CMP r4, r5
    BEQ init_c        # if counter == 16, done with B
    MOVI r6, 1        # r6 = 1
    STR r6, [r2, r4]  # store 1 at B[counter]
    ADDI r4, r4, 1    # increment counter
    JMP init_b_loop

init_c:
    # Initialize matrix C with zeros
    MOVI r4, 0        # r4 = counter
init_c_loop:
    CMP r4, r5
    BEQ matrix_mult   # if counter == 16, done with C
    MOVI r6, 0        # r6 = 0
    STR r6, [r3, r4]  # store 0 at C[counter]
    ADDI r4, r4, 1    # increment counter
    JMP init_c_loop

# Matrix multiplication C = A * B
matrix_mult:
    MOVI r4, 0        # r4 = i (row index for A)
    MOVI r5, 4        # r5 = matrix dimension
    
outer_loop_mm:
    CMP r4, r5        # if i == 4, done
    BEQ mm_done
    
    MOVI r6, 0        # r6 = j (column index for B)
middle_loop_mm:
    CMP r6, r5        # if j == 4, done with this row-column pair
    BEQ next_row
    
    MOVI r7, 0        # r7 = accumulator for dot product
    MOVI r8, 0        # r8 = k (iteration through row/column)
    
inner_loop_mm:
    CMP r8, r5        # if k == 4, done with dot product
    BEQ store_result
    
    # Calculate A index: i*4 + k
    MULI r9, r4, 4    # r9 = i * 4
    ADD r9, r9, r8    # r9 = i * 4 + k
    
    # Calculate B index: k*4 + j
    MULI r10, r8, 4   # r10 = k * 4
    ADD r10, r10, r6  # r10 = k * 4 + j
    
    # Load values
    LDR r11, [r1, r9] # r11 = A[i][k]
    LDR r12, [r2, r10] # r12 = B[k][j]
    
    # Multiply and accumulate
    MUL r13, r11, r12 # r13 = A[i][k] * B[k][j]
    ADD r7, r7, r13   # accumulator += A[i][k] * B[k][j]
    
    # Next k
    ADDI r8, r8, 1
    JMP inner_loop_mm
    
store_result:
    # Calculate C index: i*4 + j
    MULI r9, r4, 4    # r9 = i * 4
    ADD r9, r9, r6    # r9 = i * 4 + j
    
    # Store dot product result in C
    STR r7, [r3, r9]  # C[i][j] = dot product result
    
    # Next column
    ADDI r6, r6, 1
    JMP middle_loop_mm
    
next_row:
    # Next row
    ADDI r4, r4, 1
    JMP outer_loop_mm
    
mm_done:
    # Computation complete
    MOVI r1, 0xFFFF   # Signal completion with a special value
    MOVI r2, 0        # Store at address 0
    STR r1, [r2, 0]   # This will be detected as the end condition
"""

    def run_benchmark(self, benchmark_name: str, mode: str, config: Dict[str, bool]) -> Dict[str, Any]:
        """Run a single benchmark in a specific mode."""
        print(f"\nRunning {benchmark_name} in {mode} mode...")
        
        # Initialize components
        memory = MemorySystem(**config)
        registers = RegisterFile()
        pipeline = Pipeline(memory, registers)
        
        # Configure pipeline mode
        pipeline.enabled = config['pipeline_enabled']
        
        # Load and assemble benchmark
        try:
            program, errors = assemble_file(self.benchmarks[benchmark_name])
            if errors:
                print(f"Assembly errors in {benchmark_name}:")
                for error in errors:
                    print(error)
                return None
            
            if not program:
                print(f"No instructions were assembled for {benchmark_name}")
                return None
                
            print(f"Successfully assembled {len(program)} instructions")
            
            # Debug: Print first few instructions
            for i, instr in enumerate(program[:5]):
                decoded = Instruction.decode(instr)
                print(f"{i*4:04x}: {instr:08x}  # {decoded}")
            
        except Exception as e:
            print(f"Error assembling benchmark {benchmark_name}: {str(e)}")
            return None
        
        # Load program into memory
        try:
            memory.load_program(program)
            print(f"Program loaded into memory")
        except Exception as e:
            print(f"Error loading program: {str(e)}")
            return None
        
        # Run benchmark
        cycles = 0
        instructions = 0
        max_cycles = 100000  # Increased to prevent premature termination
        
        try:
            # Set up end condition detection
            # We'll check memory address 0 for the completion signal (0xFFFF)
            end_detected = False
            
            print(f"Starting execution with {'pipelined' if config['pipeline_enabled'] else 'sequential'} mode")
            
            while cycles < max_cycles and not end_detected:
                # Check for end condition
                try:
                    end_value, _ = memory.read(0)
                    if end_value == 0xFFFF:
                        print(f"End condition detected at cycle {cycles}")
                        end_detected = True
                        break
                except:
                    pass
                
                if config['pipeline_enabled']:
                    # Pipelined execution
                    pipeline.step()
                    cycles += 1
                    
                    # Count completed instructions
                    if pipeline.stages[PipelineStage.WRITEBACK].instruction:
                        instructions += 1
                        if instructions % 100 == 0:
                            print(f"Completed {instructions} instructions after {cycles} cycles")
                else:
                    # Sequential execution
                    old_instructions = pipeline.instructions
                    pipeline.step()  # Use regular step but with pipeline disabled
                    cycles += 1
                    
                    # Check if instruction completed
                    if pipeline.instructions > old_instructions:
                        instructions = pipeline.instructions
                        if instructions % 100 == 0:
                            print(f"Completed {instructions} instructions after {cycles} cycles")
            
            if cycles >= max_cycles:
                print(f"Warning: Benchmark exceeded maximum cycles ({max_cycles})")
                print(f"Current PC: {pipeline.pc}")
                # Debug instruction at current PC
                try:
                    instr_data, _ = memory.read(pipeline.pc)
                    instr = Instruction.decode(instr_data)
                    print(f"Current instruction: {instr}")
                except:
                    print("Could not decode current instruction")
            
            print(f"Execution completed with {instructions} instructions in {cycles} cycles")
            
        except Exception as e:
            print(f"Error during benchmark execution: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
        # Collect statistics
        stats = {
            'cycles': cycles,
            'instructions': instructions,
            'pipeline_stalls': pipeline.stall_count if config['pipeline_enabled'] else 0,
            'pipeline_flushes': pipeline.flush_count if config['pipeline_enabled'] else 0
        }
        
        # Calculate derived metrics
        stats['cycles_per_instruction'] = cycles / instructions if instructions > 0 else 0
        stats['instructions_per_cycle'] = instructions / cycles if cycles > 0 else 0
        
        print(f"Benchmark completed: {stats}")
        return stats

    def run_all_benchmarks(self) -> None:
        """Run all benchmarks in all modes."""
        for benchmark_name in self.benchmarks:
            print(f"\n\n===== Running benchmark: {benchmark_name} =====")
            self.results[benchmark_name] = {}
            for mode, config in self.modes.items():
                result = self.run_benchmark(benchmark_name, mode, config)
                if result:
                    self.results[benchmark_name][mode] = result
                else:
                    print(f"Skipping {mode} for {benchmark_name} due to errors")

    def save_results(self) -> None:
        """Save benchmark results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'benchmark_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to {filename}")

    def print_summary(self) -> None:
        """Print a summary of the benchmark results."""
        print("\nBenchmark Results Summary:")
        print("=" * 80)
        
        for benchmark_name in self.benchmarks:
            if benchmark_name not in self.results:
                print(f"\n{benchmark_name.upper()}: No results available")
                continue
                
            print(f"\n{benchmark_name.upper()}:")
            print("-" * 40)
            
            for mode in self.modes:
                if mode in self.results[benchmark_name]:
                    stats = self.results[benchmark_name][mode]
                    print(f"\n{mode}:")
                    print(f"  Cycles: {stats['cycles']}")
                    print(f"  Instructions: {stats['instructions']}")
                    print(f"  CPI: {stats['cycles_per_instruction']:.2f}")
                    print(f"  IPC: {stats['instructions_per_cycle']:.2f}")
                    print(f"  Pipeline Stalls: {stats['pipeline_stalls']}")
                    print(f"  Pipeline Flushes: {stats['pipeline_flushes']}")

def main():
    print("SlitherRISC Benchmark Runner")
    print("=" * 80)
    
    try:
        runner = BenchmarkRunner()
        runner.run_all_benchmarks()
        runner.print_summary()
        runner.save_results()
    except Exception as e:
        print(f"Error in benchmark runner: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()