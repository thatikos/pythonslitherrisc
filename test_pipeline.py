import pytest
from pipeline import Pipeline, PipelineStage, HazardType
from cache import MemorySystem
from registers import RegisterFile, Flags, SpecialRegisters
from isa import Instruction, Opcode, InstructionType

@pytest.fixture
def memory():
    """Create memory system fixture."""
    return MemorySystem()

@pytest.fixture
def registers():
    """Create register file fixture."""
    return RegisterFile()

@pytest.fixture
def pipeline(memory, registers):
    """Create pipeline fixture."""
    pipeline = Pipeline(memory, registers)
    pipeline.reset()  # Reset pipeline state
    return pipeline

def test_arithmetic_instructions(pipeline, registers):
    """Test arithmetic instructions."""
    # Test ADD
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ADD,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        rs2=3,
        imm=0
    )
    registers.set(2, 5)
    registers.set(3, 3)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 8

    # Test ADDI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ADDI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=10
    )
    registers.set(2, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 15

    # Test ADDIS
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ADDIS,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=-5
    )
    registers.set(2, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0
    assert registers.get_zero_flag()
    assert not registers.get_negative_flag()

    # Test SUBI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.SUBI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=3
    )
    registers.set(2, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 2  # 5 - 3 = 2

    # Test SUBIS
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.SUBIS,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=5
    )
    registers.set(2, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0  # 5 - 5 = 0
    assert registers.get_zero_flag()
    assert not registers.get_negative_flag()

    # Test MULI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.MULI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=3
    )
    registers.set(2, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 15  # 5 * 3 = 15

    # Test DIVI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.DIVI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=2
    )
    registers.set(2, 10)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 5  # 10 / 2 = 5

    # Test DIVI with division by zero
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.DIVI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0
    )
    registers.set(2, 10)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    # Should not update register when dividing by zero
    assert registers.get(1) == 0

    # Test ANDI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ANDI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0x0F  # 0000 1111 in binary
    )
    registers.set(2, 0x3F)  # 0011 1111 in binary
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0x0F  # 0000 1111 in binary

    # Test ANDI with zero
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ANDI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0
    )
    registers.set(2, 0xFFFF)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0  # Any number AND 0 = 0

    # Test ORI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ORI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0xF0  # 1111 0000 in binary
    )
    registers.set(2, 0x0F)  # 0000 1111 in binary
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0xFF  # 1111 1111 in binary

    # Test ORI with zero
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.ORI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0
    )
    registers.set(2, 0xFFFF)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0xFFFF  # Any number OR 0 = same number

    # Test XORI
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.XORI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0xFF  # 1111 1111 in binary
    )
    registers.set(2, 0x55)  # 0101 0101 in binary
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0xAA  # 1010 1010 in binary

    # Test XORI with zero
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.XORI,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0
    )
    registers.set(2, 0xFFFF)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0xFFFF  # Any number XOR 0 = same number

    # Test SHR
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.SHR,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=2
    )
    registers.set(2, 0x0C)  # 0000 1100 in binary
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0x03  # 0000 0011 in binary (shifted right by 2)

    # Test SHR with zero
    pipeline.reset()
    registers.reset()
    instruction = Instruction(
        opcode=Opcode.SHR,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        imm=0
    )
    registers.set(2, 0xFFFF)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 0xFFFF  # Any number shifted right by 0 = same number

def test_memory_instructions(pipeline, registers, memory):
    """Test memory instructions."""
    # Test STR and LDR instructions
    store_instruction = Instruction(
        opcode=Opcode.STR,
        type=InstructionType.MEMORY,
        rd=0,
        rs1=1,
        rs2=2,
        imm=0
    )
    load_instruction = Instruction(
        opcode=Opcode.LDR,
        type=InstructionType.MEMORY,
        rd=3,
        rs1=1,
        rs2=0,
        imm=0
    )
    registers.set(1, 100)  # Base address
    registers.set(2, 42)   # Value to store
    pipeline.memory.load_program([store_instruction.encode(), load_instruction.encode()])
    pipeline.run(10)
    assert memory.read(100)[0] == 42
    assert registers.get(3) == 42

def test_jal_instruction(pipeline, registers):
    """Test JAL instruction."""
    instruction = Instruction(
        opcode=Opcode.JAL,
        type=InstructionType.CONTROL,
        rd=1,
        rs1=0,
        rs2=0,
        imm=8
    )
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(1) == 4  # Return address
    assert pipeline.pc == 12  # PC + imm

def test_ret_instruction(pipeline, registers):
    """Test RET instruction."""
    # Set up Link Register with a return address
    registers.set(SpecialRegisters.LR.value, 20)  # Use .value to get the integer
    # Create RET instruction
    ret_instruction = Instruction(
        opcode=Opcode.RET,
        type=InstructionType.CONTROL,
        rd=0,
        rs1=0,
        rs2=0,
        imm=0
    )
    pipeline.memory.load_program([ret_instruction.encode()])
    pipeline.run(5)
    # After RET execution, PC should be at LR value + 4 (one instruction after return address)
    assert pipeline.pc == 24  # LR value + 4 (one instruction after return)

def test_hazard_detection(pipeline, registers):
    """Test pipeline hazard detection."""
    # Test RAW hazard
    add_instruction = Instruction(
        opcode=Opcode.ADD,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        rs2=3,
        imm=0
    )
    use_instruction = Instruction(
        opcode=Opcode.ADD,
        type=InstructionType.ARITHMETIC,
        rd=4,
        rs1=1,
        rs2=5,
        imm=0
    )
    registers.set(2, 5)
    registers.set(3, 3)
    registers.set(5, 2)
    pipeline.memory.load_program([add_instruction.encode(), use_instruction.encode()])
    pipeline.run(10)
    assert registers.get(4) == 10  # 8 + 2

def test_special_registers(pipeline, registers):
    """Test special register behavior."""
    # Test XZR register
    instruction = Instruction(
        opcode=Opcode.ADD,
        type=InstructionType.ARITHMETIC,
        rd=SpecialRegisters.XZR.value,
        rs1=1,
        rs2=2,
        imm=0
    )
    registers.set(1, 5)
    registers.set(2, 3)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get(SpecialRegisters.XZR.value) == 0

def test_status_flags(pipeline, registers):
    """Test status flag updates."""
    # Test flag updates for arithmetic operations
    instruction = Instruction(
        opcode=Opcode.ADD,
        type=InstructionType.ARITHMETIC,
        rd=1,
        rs1=2,
        rs2=3,
        imm=0
    )
    registers.set(2, -5)
    registers.set(3, 5)
    pipeline.memory.load_program([instruction.encode()])
    pipeline.run(5)
    assert registers.get_zero_flag()
    assert not registers.get_negative_flag()
    assert not registers.get_carry_flag()
    assert not registers.get_overflow_flag()

def test_cache_behavior(pipeline, memory):
    """Test cache behavior with memory instructions."""
    # Reset cache stats
    memory.L1_cache.reset()
    memory.L2_cache.reset()
    
    # First load the instruction into memory without counting cache stats
    instruction = Instruction(
        opcode=Opcode.LDR,
        type=InstructionType.MEMORY,
        rd=1,
        rs1=2,
        rs2=0,
        imm=0
    )
    pipeline.memory.load_program([instruction.encode()])
    
    # Reset cache stats again to only count data accesses
    memory.L1_cache.reset()
    memory.L2_cache.reset()
    
    # Now run the pipeline
    pipeline.run(5)
    stats = memory.get_stats()
    assert stats["L1"]["hits"] == 0
    assert stats["L1"]["misses"] == 1
    assert stats["L2"]["hits"] == 0
    assert stats["L2"]["misses"] == 1 