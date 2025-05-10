from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from isa import Instruction, InstructionType, Opcode

@dataclass
class Symbol:
    """Represents a symbol (label) in the assembly code."""
    name: str
    address: int

class Assembler:
    def __init__(self):
        """Initialize the assembler."""
        self.symbols: Dict[str, Symbol] = {}  # Symbol table
        self.current_address = 0  # Current instruction address
        self.instructions: List[int] = []  # List of encoded instructions
        self.errors: List[str] = []  # List of assembly errors
        
    def reset(self) -> None:
        """Reset assembler state."""
        self.symbols.clear()
        self.current_address = 0
        self.instructions.clear()
        self.errors.clear()
    
    def add_error(self, line_num: int, message: str) -> None:
        """Add an error message."""
        self.errors.append(f"Line {line_num}: {message}")
    
    def parse_register(self, reg_str: str) -> Optional[int]:
        """Parse a register string (e.g., 'r1') into a register number."""
        if not reg_str:
            return None
            
        # Remove whitespace and convert to lowercase
        reg_str = reg_str.strip().lower()
        
        if not reg_str.startswith('r'):
            return None
            
        try:
            reg_num = int(reg_str[1:])
            if 0 <= reg_num <= 31:
                return reg_num
        except ValueError:
            pass
        return None
    
    def parse_immediate(self, imm_str: str) -> Optional[int]:
        """Parse an immediate value string into an integer."""
        try:
            # Handle hexadecimal
            if imm_str.startswith('0x'):
                return int(imm_str[2:], 16)
            # Handle binary
            elif imm_str.startswith('0b'):
                return int(imm_str[2:], 2)
            # Handle decimal
            else:
                return int(imm_str)
        except ValueError:
            return None
    
    def parse_memory_operand(self, operand: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse a memory operand in the format [base, offset]."""
        operand = operand.strip()
        if not (operand.startswith('[') and operand.endswith(']')):
            return None, None
            
        # Remove brackets and split by comma
        operand = operand[1:-1].strip()
        if ',' not in operand:
            return None, None
            
        # Split on the last comma to handle nested commas
        parts = operand.rsplit(',', 1)
        if len(parts) != 2:
            return None, None
            
        base, offset = [part.strip() for part in parts]
        
        # Parse base register and offset
        base_reg = self.parse_register(base)
        offset_val = self.parse_immediate(offset)
        
        return base_reg, offset_val
    
    def parse_instruction(self, line: str, line_num: int, resolve_labels: bool = False) -> Optional[Instruction]:
        """Parse a single line of assembly code into an instruction."""
        # Remove comments and whitespace
        line = line.split('#')[0].strip()
        if not line:
            return None
            
        # Split into parts and handle operands
        parts = line.split(None, 1)  # Split into mnemonic and the rest
        if not parts:
            return None
            
        mnemonic = parts[0].upper()  # Convert mnemonic to uppercase
        if len(parts) > 1:
            # For memory instructions, split only on first comma
            if mnemonic in ['LDR', 'STR']:
                operands = [op.strip() for op in parts[1].split(',', 1)]
            else:
                # Split operands by comma, handling whitespace
                operands = [op.strip() for op in parts[1].split(',')]
        else:
            operands = []
        
        # Parse based on instruction type
        if mnemonic in ['ADD', 'ADDS', 'SUB', 'SUBS', 'MUL', 'DIV', 'AND', 'OR', 'XOR', 'MOD']:
            # R-type arithmetic instructions
            if len(operands) != 3:
                self.add_error(line_num, f"Expected 3 operands for {mnemonic}")
                return None
                
            # Parse all registers
            rd = self.parse_register(operands[0])
            rs1 = self.parse_register(operands[1])
            rs2 = self.parse_register(operands[2])
            
            if rd is None:
                self.add_error(line_num, f"Invalid destination register: {operands[0]}")
                return None
            if rs1 is None:
                self.add_error(line_num, f"Invalid source register 1: {operands[1]}")
                return None
            if rs2 is None:
                self.add_error(line_num, f"Invalid source register 2: {operands[2]}")
                return None
                
            return Instruction(
                type=InstructionType.ARITHMETIC,
                opcode=Opcode[mnemonic],
                rd=rd,
                rs1=rs1,
                rs2=rs2,
                imm=0
            )
            
        elif mnemonic in ['ADDI', 'ADDIS', 'SUBI', 'SUBIS', 'MULI', 'DIVI', 'ANDI', 'ORI', 'XORI', 'MODI', 'MOVI']:
            # I-type arithmetic instructions
            if len(operands) != 2 and len(operands) != 3:
                self.add_error(line_num, f"Expected 2 or 3 operands for {mnemonic}")
                return None
                
            # Parse destination register
            rd = self.parse_register(operands[0])
            if rd is None:
                self.add_error(line_num, f"Invalid destination register: {operands[0]}")
                return None

            # Handle both formats: "rd, imm" and "rd, rs1, imm"
            if len(operands) == 2:
                # Format: rd, imm
                imm = self.parse_immediate(operands[1])
                if imm is None:
                    self.add_error(line_num, f"Invalid immediate value: {operands[1]}")
                    return None
                rs1 = 0  # Use r0 as source register
            else:
                # Format: rd, rs1, imm
                rs1 = self.parse_register(operands[1])
                if rs1 is None:
                    self.add_error(line_num, f"Invalid source register: {operands[1]}")
                    return None
                imm = self.parse_immediate(operands[2])
                if imm is None:
                    self.add_error(line_num, f"Invalid immediate value: {operands[2]}")
                    return None

            return Instruction(
                type=InstructionType.ARITHMETIC,
                opcode=Opcode[mnemonic],
                rd=rd,
                rs1=rs1,
                rs2=0,
                imm=imm
            )
            
        elif mnemonic == 'CMP':
            # Compare instruction
            if len(operands) != 2:
                self.add_error(line_num, f"Expected 2 operands for {mnemonic}")
                return None
                
            rs1 = self.parse_register(operands[0])
            rs2 = self.parse_register(operands[1])
            
            if rs1 is None:
                self.add_error(line_num, f"Invalid source register 1: {operands[0]}")
                return None
            if rs2 is None:
                self.add_error(line_num, f"Invalid source register 2: {operands[1]}")
                return None
                
            return Instruction(
                type=InstructionType.ARITHMETIC,
                opcode=Opcode.CMP,
                rd=0,
                rs1=rs1,
                rs2=rs2,
                imm=0
            )
            
        elif mnemonic in ['LDR', 'STR']:
            # Memory instructions
            if len(operands) != 2:
                self.add_error(line_num, f"Expected 2 operands for {mnemonic}")
                return None
                
            if mnemonic == 'LDR':
                rd = self.parse_register(operands[0])
                if rd is None:
                    self.add_error(line_num, f"Invalid destination register: {operands[0]}")
                    return None
                    
                # Parse memory operand
                rs1, imm = self.parse_memory_operand(operands[1])
                if rs1 is None:
                    self.add_error(line_num, "Memory operand must be in [base, offset] format")
                    return None
                if imm is None:
                    self.add_error(line_num, "Invalid offset in memory operand")
                    return None
                    
                return Instruction(
                    type=InstructionType.MEMORY,
                    opcode=Opcode.LDR,
                    rd=rd,
                    rs1=rs1,
                    rs2=0,
                    imm=imm
                )
            else:  # STR
                rs2 = self.parse_register(operands[0])
                if rs2 is None:
                    self.add_error(line_num, f"Invalid source register: {operands[0]}")
                    return None
                    
                # Parse memory operand
                rs1, imm = self.parse_memory_operand(operands[1])
                if rs1 is None:
                    self.add_error(line_num, "Memory operand must be in [base, offset] format")
                    return None
                if imm is None:
                    self.add_error(line_num, "Invalid offset in memory operand")
                    return None
                    
                return Instruction(
                    type=InstructionType.MEMORY,
                    opcode=Opcode.STR,
                    rd=0,
                    rs1=rs1,
                    rs2=rs2,
                    imm=imm
                )
                
        elif mnemonic in ['BEQ', 'BLT']:
            # Branch instructions
            if len(operands) != 1:
                self.add_error(line_num, f"Expected 1 operand for {mnemonic}")
                return None
                
            # Try parsing as immediate first
            imm = self.parse_immediate(operands[0])
            if imm is not None:
                return Instruction(
                    type=InstructionType.CONTROL,
                    opcode=Opcode[mnemonic],
                    rd=0,
                    rs1=0,
                    rs2=0,
                    imm=imm
                )
                
            # If not an immediate, treat as label
            if resolve_labels:
                if operands[0] not in self.symbols:
                    self.add_error(line_num, f"Undefined label: {operands[0]}")
                    return None
                # Calculate relative offset in words (4 bytes per instruction)
                target_addr = self.symbols[operands[0]].address
                current_addr = self.current_address + 4  # PC points to next instruction
                imm = (target_addr - current_addr) >> 2
            else:
                # During first pass, just use 0 for the immediate
                imm = 0
                
            return Instruction(
                type=InstructionType.CONTROL,
                opcode=Opcode[mnemonic],
                rd=0,
                rs1=0,
                rs2=0,
                imm=imm
            )
            
        elif mnemonic == 'JMP':
            # Jump instruction
            if len(operands) != 1:
                self.add_error(line_num, f"Expected 1 operand for {mnemonic}")
                return None
                
            # Try parsing as register first
            rs1 = self.parse_register(operands[0])
            if rs1 is not None:
                return Instruction(
                    type=InstructionType.CONTROL,
                    opcode=Opcode.JMP,
                    rd=0,
                    rs1=rs1,
                    rs2=0,
                    imm=0
                )
                
            # If not a register, try as label
            if resolve_labels:
                if operands[0] not in self.symbols:
                    self.add_error(line_num, f"Undefined label: {operands[0]}")
                    return None
                # Calculate relative offset in words (4 bytes per instruction)
                target_addr = self.symbols[operands[0]].address
                current_addr = self.current_address + 4  # PC points to next instruction
                imm = (target_addr - current_addr) >> 2
            else:
                # During first pass, just use 0 for the immediate
                imm = 0
                
            # Return a JMP instruction with the label's address
            return Instruction(
                type=InstructionType.CONTROL,
                opcode=Opcode.JMP,
                rd=0,
                rs1=0,
                rs2=0,
                imm=imm
            )
            
        elif mnemonic in ['CAL', 'FLUSH']:
            # Register-based control instructions
            if len(operands) != 1:
                self.add_error(line_num, f"Expected 1 operand for {mnemonic}")
                return None
                
            rs1 = self.parse_register(operands[0])
            if rs1 is None:
                self.add_error(line_num, "Invalid register")
                return None
                
            return Instruction(
                type=InstructionType.CONTROL,
                opcode=Opcode[mnemonic],
                rd=0,
                rs1=rs1,
                rs2=0,
                imm=0
            )
            
        else:
            self.add_error(line_num, f"Unknown instruction: {mnemonic}")
            return None
    
    def assemble(self, source: str) -> Tuple[List[int], List[str]]:
        """Assemble source code into machine code."""
        self.reset()
        
        # Split source into lines
        lines = source.split('\n')
        
        # First pass: collect labels
        print("First pass: collecting labels...")
        for i, line in enumerate(lines, 1):
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Check if line contains a label
            if line.endswith(':'):
                label = line[:-1].strip()
                if label in self.symbols:
                    self.add_error(i, f"Duplicate label: {label}")
                else:
                    self.symbols[label] = Symbol(label, self.current_address)
                    print(f"Found label {label} at address {self.current_address}")
                continue
                
            # Count non-label instructions
            self.current_address += 4
        
        # Second pass: parse instructions
        print("\nSecond pass: parsing instructions...")
        self.current_address = 0
        instructions = []
        
        for i, line in enumerate(lines, 1):
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Skip label declarations
            if line.endswith(':'):
                continue
                
            # Parse instruction
            print(f"Parsing line {i}: {line}")
            instr = self.parse_instruction(line, i, resolve_labels=True)
            if instr is not None:
                instructions.append(instr.encode())
                print(f"  Encoded as: {instr.encode():08x}")
                self.current_address += 4
                
                # Stop assembling if we hit a branch to a label that's already defined
                # This handles unreachable code after branch targets
                if instr.type == InstructionType.CONTROL and instr.opcode == Opcode.BEQ:
                    # Find the target label
                    target_addr = self.current_address + (instr.imm << 2)
                    for label, symbol in self.symbols.items():
                        if symbol.address == target_addr:
                            # If we're branching to a label that's already defined,
                            # stop assembling here
                            return instructions, self.errors
            else:
                print("  Failed to parse instruction")
        
        return instructions, self.errors

def assemble_file(filename: str) -> Tuple[List[int], List[str]]:
    """Assemble a file into machine code."""
    try:
        print(f"Reading file: {filename}")
        with open(filename, 'r') as f:
            source = f.read()
        print(f"File contents:\n{source}")
        return Assembler().assemble(source)
    except FileNotFoundError:
        return [], [f"File not found: {filename}"]
    except Exception as e:
        return [], [f"Error reading file: {str(e)}"]

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <assembly_file>")
        sys.exit(1)
        
    filename = sys.argv[1]
    instructions, errors = assemble_file(filename)
    
    if errors:
        print("Assembly errors:")
        for error in errors:
            print(error)
    else:
        print("Assembly successful!")
        print("\nGenerated instructions:")
        for i, instr in enumerate(instructions):
            decoded = Instruction.decode(instr)
            print(f"{i*4:04x}: {instr:08x}  # {decoded}") 