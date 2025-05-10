from memory import MemorySystem
from pipeline import Pipeline, PipelineStage, HazardType
from registers import RegisterFile
from isa import Instruction, InstructionType, Opcode

def create_add_instruction(rd: int, rs1: int, rs2: int) -> int:
    """Create an ADD instruction."""
    instr = Instruction(
        type=InstructionType.ARITHMETIC,
        opcode=Opcode.ADD,
        rd=rd,
        rs1=rs1,
        rs2=rs2,
        imm=0
    )
    return instr.encode()

def create_ldr_instruction(rd: int, base: int, offset: int) -> int:
    """Create a LDR instruction."""
    instr = Instruction(
        type=InstructionType.MEMORY,
        opcode=Opcode.LDR,
        rd=rd,
        rs1=base,
        rs2=0,
        imm=offset
    )
    return instr.encode()

def create_str_instruction(rd: int, base: int, offset: int) -> int:
    """Create a STR instruction."""
    instr = Instruction(
        type=InstructionType.MEMORY,
        opcode=Opcode.STR,
        rd=rd,
        rs1=base,
        rs2=0,
        imm=offset
    )
    return instr.encode()

def test_pipeline_cache_interaction():
    """Test interaction between pipeline and cache."""
    print("\nTesting Pipeline and Cache Interaction:")
    print("-" * 50)
    
    try:
        # Create memory system with both pipeline and cache enabled
        memory = MemorySystem(cache_enabled=True, pipeline_enabled=True)
        registers = RegisterFile()
        pipeline = Pipeline(memory, registers)
        
        # Initialize registers
        registers.set(1, 100)  # Base address for memory operations
        registers.set(2, 42)   # Value to store
        
        # Create a program that exercises both pipeline and cache
        program = [
            create_add_instruction(3, 1, 2),    # ADD r3, r1, r2  (r3 = 142)
            create_str_instruction(3, 1, 0),    # STR r3, [r1]    (Store 142 at address 100)
            create_ldr_instruction(4, 1, 0),    # LDR r4, [r1]    (Load from address 100)
            create_add_instruction(5, 4, 2),    # ADD r5, r4, r2  (r5 = 184)
            create_str_instruction(5, 1, 4),    # STR r5, [r1, #4] (Store 184 at address 104)
            create_ldr_instruction(6, 1, 4),    # LDR r6, [r1, #4] (Load from address 104)
        ]
        
        # Load program
        memory.load_program(program)
        
        # Run pipeline for 20 cycles
        print("Running pipeline for 20 cycles...")
        pipeline.run(20)
        
        # Print register values
        print("\nRegister values after execution:")
        for i in range(7):
            print(f"r{i} = {registers.get(i)}")
        
        # Print memory values
        print("\nMemory values:")
        for addr in range(100, 108, 4):
            try:
                value, _ = memory.read(addr)
                print(f"Memory[{addr}] = {value}")
            except ValueError as e:
                print(f"Error reading memory at {addr}: {e}")
        
        # Print cache statistics
        stats = memory.get_stats()
        print("\nCache statistics:")
        print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
        print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
        
        # Print pipeline statistics
        pipeline_stats = pipeline.get_stats()
        print("\nPipeline statistics:")
        print(f"Cycles: {pipeline_stats['cycles']}")
        print(f"Instructions: {pipeline_stats['instructions']}")
        print(f"CPI: {pipeline_stats['cpi']:.2f}")
        print(f"Stalls: {pipeline_stats['stalls']}")
        print(f"Flushes: {pipeline_stats['flushes']}")
        
    except Exception as e:
        print(f"Error in pipeline-cache interaction test: {e}")

def test_cache_performance():
    """Test cache performance with different access patterns."""
    print("\nTesting Cache Performance:")
    print("-" * 50)
    
    # Test configurations
    configs = [
        ("Cache + Pipeline", True, True),
        ("Cache Only", True, False),
        ("Pipeline Only", False, True),
        ("No Cache, No Pipeline", False, False)
    ]
    
    for name, cache_enabled, pipeline_enabled in configs:
        print(f"\nConfiguration: {name}")
        print("-" * 30)
        
        try:
            # Create memory system with specified configuration
            memory = MemorySystem(cache_enabled=cache_enabled, pipeline_enabled=pipeline_enabled)
            registers = RegisterFile()
            pipeline = Pipeline(memory, registers)
            
            # Initialize registers with a valid base address
            base_addr = 0x1000  # Use a higher base address to avoid conflicts
            registers.set(1, base_addr)
            
            # Create a program with sequential memory access
            program = []
            for i in range(16):  # Access 16 words
                offset = i * 4
                if base_addr + offset < memory.memory.size:  # Check if address is valid
                    program.append(create_ldr_instruction(2, 1, offset))  # LDR r2, [r1, #i*4]
                    program.append(create_str_instruction(2, 1, offset))  # STR r2, [r1, #i*4]
            
            # Load program
            memory.load_program(program)
            
            # Run pipeline
            pipeline.run(50)
            
            # Print statistics
            stats = memory.get_stats()
            print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
            print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
            print(f"Total cycles: {stats['cycles']}")
            
        except Exception as e:
            print(f"Error in {name} configuration: {e}")

def test_pipeline_hazards():
    """Test pipeline hazard detection and handling."""
    print("\nTesting Pipeline Hazards:")
    print("-" * 50)
    
    try:
        # Create memory system
        memory = MemorySystem(cache_enabled=True, pipeline_enabled=True)
        registers = RegisterFile()
        pipeline = Pipeline(memory, registers)
        
        # Initialize registers
        registers.set(2, 10)  # Initialize r2
        registers.set(3, 20)  # Initialize r3
        registers.set(5, 30)  # Initialize r5
        registers.set(6, 40)  # Initialize r6
        registers.set(7, 50)  # Initialize r7
        registers.set(9, 60)  # Initialize r9
        
        # Create a program with various hazards
        program = [
            create_add_instruction(1, 2, 3),    # ADD r1, r2, r3
            create_add_instruction(4, 1, 5),    # ADD r4, r1, r5  (RAW hazard)
            create_add_instruction(1, 6, 7),    # ADD r1, r6, r7  (WAR hazard)
            create_add_instruction(8, 1, 9),    # ADD r8, r1, r9  (RAW hazard)
            create_ldr_instruction(2, 1, 0),    # LDR r2, [r1]    (Memory hazard)
            create_add_instruction(3, 2, 4),    # ADD r3, r2, r4  (RAW hazard)
        ]
        
        # Load program
        memory.load_program(program)
        
        # Run pipeline
        print("Running pipeline for 15 cycles...")
        pipeline.run(15)
        
        # Print register values
        print("\nRegister values after execution:")
        for i in range(9):
            print(f"r{i} = {registers.get(i)}")
        
        # Print pipeline statistics
        stats = pipeline.get_stats()
        print("\nPipeline statistics:")
        print(f"Cycles: {stats['cycles']}")
        print(f"Instructions: {stats['instructions']}")
        print(f"CPI: {stats['cpi']:.2f}")
        print(f"Stalls: {stats['stalls']}")
        print(f"Flushes: {stats['flushes']}")
        
    except Exception as e:
        print(f"Error in pipeline hazards test: {e}")

if __name__ == "__main__":
    # Run all tests
    test_pipeline_cache_interaction()
    test_cache_performance()
    test_pipeline_hazards() 