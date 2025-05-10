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

def create_sub_instruction(rd: int, rs1: int, rs2: int) -> int:
    """Create a SUB instruction."""
    instr = Instruction(
        type=InstructionType.ARITHMETIC,
        opcode=Opcode.SUB,
        rd=rd,
        rs1=rs1,
        rs2=rs2,
        imm=0
    )
    return instr.encode()

def create_ldr_instruction(rd: int, rs1: int, offset: int) -> int:
    """Create a LDR instruction."""
    instr = Instruction(
        type=InstructionType.MEMORY,
        opcode=Opcode.LDR,
        rd=rd,
        rs1=rs1,
        rs2=0,
        imm=offset
    )
    return instr.encode()

def create_str_instruction(rs2: int, rs1: int, offset: int) -> int:
    """Create a STR instruction."""
    instr = Instruction(
        type=InstructionType.MEMORY,
        opcode=Opcode.STR,
        rd=0,
        rs1=rs1,
        rs2=rs2,
        imm=offset
    )
    return instr.encode()

def test_sequential_execution():
    """Test pipeline with sequential instructions."""
    # Create memory, registers and pipeline
    memory = MemorySystem(cache_enabled=True, pipeline_enabled=True)
    registers = RegisterFile()
    pipeline = Pipeline(memory, registers)
    
    # Load a simple program
    program = [
        create_add_instruction(1, 2, 3),    # ADD r1, r2, r3
        create_sub_instruction(4, 1, 5),    # SUB r4, r1, r5
        create_ldr_instruction(6, 0, 100),  # LDR r6, [r0, #100]
        create_str_instruction(6, 0, 200),  # STR r6, [r0, #200]
    ]
    memory.load_program(program)
    
    # Run pipeline for 10 cycles
    pipeline.run(10)
    
    # Print statistics
    stats = pipeline.get_stats()
    print("\nSequential Execution Test:")
    print(f"Cycles: {stats['cycles']}")
    print(f"Instructions: {stats['instructions']}")
    print(f"CPI: {stats['cpi']:.2f}")
    print(f"Stalls: {stats['stalls']}")
    print(f"Flushes: {stats['flushes']}")

def test_hazard_detection():
    """Test pipeline hazard detection."""
    memory = MemorySystem(cache_enabled=True, pipeline_enabled=True)
    registers = RegisterFile()
    pipeline = Pipeline(memory, registers)
    
    # Load program with hazards
    program = [
        create_add_instruction(1, 2, 3),    # ADD r1, r2, r3
        create_add_instruction(4, 1, 5),    # ADD r4, r1, r5  (RAW hazard)
        create_add_instruction(1, 6, 7),    # ADD r1, r6, r7  (WAR hazard)
        create_add_instruction(8, 1, 9),    # ADD r8, r1, r9  (RAW hazard)
    ]
    memory.load_program(program)
    
    # Run pipeline for 15 cycles
    pipeline.run(15)
    
    # Print statistics
    stats = pipeline.get_stats()
    print("\nHazard Detection Test:")
    print(f"Cycles: {stats['cycles']}")
    print(f"Instructions: {stats['instructions']}")
    print(f"CPI: {stats['cpi']:.2f}")
    print(f"Stalls: {stats['stalls']}")
    print(f"Flushes: {stats['flushes']}")

def test_branch_handling():
    """Test pipeline branch handling."""
    memory = MemorySystem(cache_enabled=True, pipeline_enabled=True)
    registers = RegisterFile()
    pipeline = Pipeline(memory, registers)
    
    # Create JAL and BEQ instructions
    jal_instr = Instruction(
        type=InstructionType.CONTROL,
        opcode=Opcode.JAL,
        rd=1,
        rs1=0,
        rs2=0,
        imm=100
    ).encode()
    
    beq_instr = Instruction(
        type=InstructionType.CONTROL,
        opcode=Opcode.BEQ,
        rd=0,
        rs1=1,
        rs2=2,
        imm=200
    ).encode()
    
    # Load program with branches
    program = [
        create_add_instruction(1, 2, 3),    # ADD r1, r2, r3
        jal_instr,                          # JAL r1, 100
        create_sub_instruction(4, 1, 5),    # SUB r4, r1, r5
        beq_instr,                          # BEQ r1, r2, 200
    ]
    memory.load_program(program)
    
    # Run pipeline for 12 cycles
    pipeline.run(12)
    
    # Print statistics
    stats = pipeline.get_stats()
    print("\nBranch Handling Test:")
    print(f"Cycles: {stats['cycles']}")
    print(f"Instructions: {stats['instructions']}")
    print(f"CPI: {stats['cpi']:.2f}")
    print(f"Stalls: {stats['stalls']}")
    print(f"Flushes: {stats['flushes']}")

def test_pipeline_disabled():
    """Test pipeline with pipelining disabled."""
    memory = MemorySystem(cache_enabled=True, pipeline_enabled=False)
    registers = RegisterFile()
    pipeline = Pipeline(memory, registers)
    pipeline.enabled = False
    
    # Load a simple program
    program = [
        create_add_instruction(1, 2, 3),    # ADD r1, r2, r3
        create_sub_instruction(4, 1, 5),    # SUB r4, r1, r5
        create_ldr_instruction(6, 0, 100),  # LDR r6, [r0, #100]
        create_str_instruction(6, 0, 200),  # STR r6, [r0, #200]
    ]
    memory.load_program(program)
    
    # Run pipeline for 10 cycles
    pipeline.run(10)
    
    # Print statistics
    stats = pipeline.get_stats()
    print("\nPipeline Disabled Test:")
    print(f"Cycles: {stats['cycles']}")
    print(f"Instructions: {stats['instructions']}")
    print(f"CPI: {stats['cpi']:.2f}")
    print(f"Stalls: {stats['stalls']}")
    print(f"Flushes: {stats['flushes']}")

if __name__ == "__main__":
    print("Running Pipeline Tests...")
    test_sequential_execution()
    test_hazard_detection()
    test_branch_handling()
    test_pipeline_disabled() 