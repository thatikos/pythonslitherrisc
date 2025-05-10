from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Optional

class InstructionType(Enum):
    ARITHMETIC = auto()
    MEMORY = auto()
    CONTROL = auto()

class Opcode(Enum):
    # Arithmetic Instructions (Type 00)
    ADD = 0x00    # 00000
    ADDS = 0x01   # 00001
    ADDI = 0x02   # 00010
    ADDIS = 0x03  # 00011
    SUB = 0x04    # 00100
    SUBS = 0x05   # 00101
    SUBI = 0x06   # 00110
    SUBIS = 0x07  # 00111
    MUL = 0x08    # 01000
    MULI = 0x09   # 01001
    DIV = 0x0A    # 01010
    DIVI = 0x0B   # 01011
    AND = 0x0C    # 01100
    ANDI = 0x0D   # 01101
    OR = 0x0E     # 01110
    ORI = 0x0F    # 01111
    XOR = 0x10    # 10000
    XORI = 0x11   # 10001
    SHL = 0x12    # 10010
    SHR = 0x13    # 10011
    CMP = 0x14    # 10100
    MOD = 0x15    # 10101
    MODI = 0x16   # 10110
    MOV = 0x17    # 10111
    MOVI = 0x18   # 11000

    # Memory Instructions (Type 01)
    LDR = 0x20    # 00
    STR = 0x21    # 01

    # Control Instructions (Type 10)
    JMP = 0x30    # 000
    BEQ = 0x31    # 001
    BLT = 0x32    # 010
    CAL = 0x33    # 100
    FLUSH = 0x34  # 101

@dataclass
class Instruction:
    type: InstructionType
    opcode: Opcode
    rd: int
    rs1: int
    rs2: int
    imm: int
    
    @staticmethod
    def decode(word: int) -> Optional['Instruction']:
        """Decode a 32-bit instruction word."""
        # Extract type (2 bits)
        instr_type = (word >> 30) & 0x3
        
        # Extract opcode based on type
        if instr_type == 0:  # Arithmetic
            opcode = (word >> 25) & 0x1F  # 5 bits
            rd = (word >> 20) & 0x1F      # 5 bits
            rs1 = (word >> 15) & 0x1F     # 5 bits
            rs2 = (word >> 10) & 0x1F     # 5 bits
            imm = word & 0x3FF            # 10 bits
        elif instr_type == 1:  # Memory
            opcode = (word >> 28) & 0x3   # 2 bits
            rd = (word >> 23) & 0x1F      # 5 bits
            rs1 = (word >> 18) & 0x1F     # 5 bits
            imm = word & 0x3FFFF          # 18 bits
            rs2 = 0  # Not used in memory instructions
        else:  # Control
            opcode = (word >> 27) & 0x7   # 3 bits
            if opcode in [Opcode.JMP.value, Opcode.CAL.value, Opcode.FLUSH.value]:
                rs1 = (word >> 22) & 0x1F  # 5 bits
                imm = 0  # Not used
                rs2 = 0  # Not used
                rd = 0   # Not used
            else:  # BEQ, BLT
                imm = word & 0x7FFFFFF    # 27 bits
                rs1 = 0  # Not used
                rs2 = 0  # Not used
                rd = 0   # Not used
        
        # Sign extend immediate if needed
        if instr_type == 0:  # Arithmetic
            if imm & 0x200:  # Check sign bit
                imm |= 0xFFFFFC00  # Extend with 1s
        elif instr_type == 1:  # Memory
            if imm & 0x20000:  # Check sign bit
                imm |= 0xFFFC0000  # Extend with 1s
        else:  # Control
            if imm & 0x4000000:  # Check sign bit
                imm |= 0xF8000000  # Extend with 1s
        
        try:
            opcode_enum = Opcode(opcode | (instr_type << 5))  # Combine type and opcode
        except ValueError:
            return None
            
        # Determine instruction type
        if instr_type == 0:
            instr_type_enum = InstructionType.ARITHMETIC
        elif instr_type == 1:
            instr_type_enum = InstructionType.MEMORY
        else:
            instr_type_enum = InstructionType.CONTROL
            
        return Instruction(
            type=instr_type_enum,
            opcode=opcode_enum,
            rd=rd,
            rs1=rs1,
            rs2=rs2,
            imm=imm
        )
    
    def encode(self) -> int:
        """Encode instruction into 32-bit word."""
        word = 0
        
        # Set type bits
        if self.type == InstructionType.ARITHMETIC:
            word |= 0 << 30  # Type 00
            word |= (self.opcode.value & 0x1F) << 25  # 5 bits opcode
            word |= (self.rd & 0x1F) << 20           # 5 bits rd
            word |= (self.rs1 & 0x1F) << 15          # 5 bits rs1
            word |= (self.rs2 & 0x1F) << 10          # 5 bits rs2
            word |= self.imm & 0x3FF                 # 10 bits imm
        elif self.type == InstructionType.MEMORY:
            word |= 1 << 30  # Type 01
            word |= (self.opcode.value & 0x3) << 28  # 2 bits opcode
            word |= (self.rd & 0x1F) << 23           # 5 bits rd
            word |= (self.rs1 & 0x1F) << 18          # 5 bits rs1
            word |= self.imm & 0x3FFFF               # 18 bits imm
        else:  # Control
            word |= 2 << 30  # Type 10
            word |= (self.opcode.value & 0x7) << 27  # 3 bits opcode
            if self.opcode in [Opcode.JMP, Opcode.CAL, Opcode.FLUSH]:
                word |= (self.rs1 & 0x1F) << 22      # 5 bits rs1
            else:  # BEQ, BLT
                word |= self.imm & 0x7FFFFFF         # 27 bits imm
        
        return word
    
    def __str__(self) -> str:
        """Convert instruction to assembly string."""
        if self.type == InstructionType.ARITHMETIC:
            if self.opcode in [Opcode.ADDI, Opcode.SUBI, Opcode.MULI, Opcode.DIVI, 
                             Opcode.ANDI, Opcode.ORI, Opcode.XORI, Opcode.MODI, 
                             Opcode.MOVI]:
                return f"{self.opcode.name.lower()} r{self.rd}, r{self.rs1}, {self.imm}"
            elif self.opcode in [Opcode.SHL, Opcode.SHR]:
                return f"{self.opcode.name.lower()} r{self.rd}, {self.imm}"
            elif self.opcode == Opcode.CMP:
                return f"{self.opcode.name.lower()} r{self.rs1}, r{self.rs2}"
            else:
                return f"{self.opcode.name.lower()} r{self.rd}, r{self.rs1}, r{self.rs2}"
        elif self.type == InstructionType.MEMORY:
            if self.opcode == Opcode.LDR:
                return f"ldr r{self.rd}, [r{self.rs1}, #{self.imm}]"
            else:  # STR
                return f"str r{self.rs2}, [r{self.rs1}, #{self.imm}]"
        else:  # CONTROL
            if self.opcode == Opcode.JMP:
                return f"jmp r{self.rs1}"
            elif self.opcode == Opcode.CAL:
                return f"cal r{self.rs1}"
            elif self.opcode == Opcode.FLUSH:
                return f"flush r{self.rs1}"
            else:  # BEQ, BLT
                return f"{self.opcode.name.lower()} #{self.imm}"

class InstructionDecoder:
    def __init__(self):
        self.instructions: List[Instruction] = []
    
    def decode_program(self, program: List[int]) -> List[Instruction]:
        """Decode a program into a list of instructions."""
        self.instructions = [Instruction.decode(word) for word in program]
        return self.instructions
    
    def encode_program(self, instructions: List[Instruction]) -> List[int]:
        """Encode a list of instructions into a program."""
        return [instr.encode() for instr in instructions]
    
    def get_instruction(self, pc: int) -> Optional[Instruction]:
        """Get instruction at program counter."""
        if 0 <= pc < len(self.instructions):
            return self.instructions[pc]
        return None 