from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum, auto
from registers import RegisterFile, Flags, SpecialRegisters
from memory import MemorySystem
from isa import Instruction, Opcode, InstructionType

class PipelineStage(Enum):
    FETCH = auto()
    DECODE = auto()
    EXECUTE = auto()
    MEMORY = auto()
    WRITEBACK = auto()

class HazardType(Enum):
    NONE = auto()
    RAW = auto()  # Read After Write
    WAR = auto()  # Write After Read
    WAW = auto()  # Write After Write
    CONTROL = auto()
    STRUCTURAL = auto()

@dataclass
class PipelineRegister:
    instruction: Optional[Instruction] = None
    pc: int = 0
    rs1: int = 0
    rs2: int = 0
    rd: int = 0
    imm: int = 0
    alu_result: int = 0
    memory_data: int = 0
    write_back: bool = False
    hazard: HazardType = HazardType.NONE

class Pipeline:
    def __init__(self, memory: MemorySystem, registers: RegisterFile):
        """Initialize pipeline."""
        self.memory = memory
        self.registers = registers
        self.pc = 0
        self.stages = {
            PipelineStage.FETCH: PipelineRegister(),
            PipelineStage.DECODE: PipelineRegister(),
            PipelineStage.EXECUTE: PipelineRegister(),
            PipelineStage.MEMORY: PipelineRegister(),
            PipelineStage.WRITEBACK: PipelineRegister()
        }
        self.stalled = False
        self.flushed = False
        self.cycles = 0  # Initialize cycles counter
        self.instructions = 0  # Track completed instructions
        self.stall_count = 0  # Track number of stalls
        self.flush_count = 0  # Track number of flushes
        self.enabled = True  # Pipeline enabled by default
        self.sequential_stage = 0  # 0=fetch, 1=decode, 2=execute, 3=memory, 4=writeback
    
    def reset(self) -> None:
        """Reset pipeline state."""
        self.pc = 0
        for stage in self.stages.values():
            stage.instruction = None
            stage.pc = 0
            stage.rs1 = 0
            stage.rs2 = 0
            stage.rd = 0
            stage.imm = 0
            stage.alu_result = 0
            stage.memory_data = 0
            stage.write_back = False
            stage.hazard = HazardType.NONE
        self.stalled = False
        self.flushed = False
        self.cycles = 0  # Reset cycle count
        self.instructions = 0  # Reset instruction count
        self.stall_count = 0  # Reset stall count
        self.flush_count = 0  # Reset flush count
        self.sequential_stage = 0
    
    def detect_hazard(self, stage: PipelineStage) -> HazardType:
        """Detect hazards for a stage."""
        current = self.stages[stage]
        if not current.instruction:
            return HazardType.NONE
        
        # Check for RAW hazards
        execute = self.stages[PipelineStage.EXECUTE]
        memory = self.stages[PipelineStage.MEMORY]
        
        if execute.instruction and execute.write_back:
            if (current.instruction.rs1 == execute.rd or current.instruction.rs2 == execute.rd) and execute.rd != 0:
                return HazardType.RAW
        
        if memory.instruction and memory.write_back:
            if (current.instruction.rs1 == memory.rd or current.instruction.rs2 == memory.rd) and memory.rd != 0:
                return HazardType.RAW
        
        # Check for WAW hazards
        if current.write_back and current.rd != 0:  # Only check if current instruction writes back
            if execute.write_back and current.rd == execute.rd:
                return HazardType.WAW
            if memory.write_back and current.rd == memory.rd:
                return HazardType.WAW
        
        # Check for WAR hazards
        if current.write_back and current.rd != 0:
            if execute.instruction and (current.rd == execute.instruction.rs1 or current.rd == execute.instruction.rs2):
                return HazardType.WAR
            if memory.instruction and (current.rd == memory.instruction.rs1 or current.rd == memory.instruction.rs2):
                return HazardType.WAR
        
        return HazardType.NONE
    
    def forward_data(self, stage: PipelineStage) -> None:
        """Forward data to resolve hazards."""
        if stage == PipelineStage.FETCH:
            return
        
        current = self.stages[stage]
        if not current.instruction:
            return
        
        # Forward from EXECUTE stage (higher priority)
        execute = self.stages[PipelineStage.EXECUTE]
        if execute.instruction and execute.write_back:
            if current.instruction.rs1 == execute.rd and execute.rd != 0:  # Don't forward from R0
                current.rs1 = execute.alu_result
            if current.instruction.rs2 == execute.rd and execute.rd != 0:  # Don't forward from R0
                current.rs2 = execute.alu_result
        
        # Forward from MEMORY stage (lower priority)
        memory = self.stages[PipelineStage.MEMORY]
        if memory.instruction and memory.write_back:
            # Only forward from memory if execute stage isn't forwarding the same register
            if current.instruction.rs1 == memory.rd and memory.rd != 0 and memory.rd != execute.rd:
                if memory.instruction.type == InstructionType.MEMORY and memory.instruction.opcode == Opcode.LDR:
                    current.rs1 = memory.memory_data
                else:
                    current.rs1 = memory.alu_result
            if current.instruction.rs2 == memory.rd and memory.rd != 0 and memory.rd != execute.rd:
                if memory.instruction.type == InstructionType.MEMORY and memory.instruction.opcode == Opcode.LDR:
                    current.rs2 = memory.memory_data
                else:
                    current.rs2 = memory.alu_result
    
    def handle_hazard(self, stage: PipelineStage) -> None:
        """Handle detected hazards."""
        hazard = self.detect_hazard(stage)
        if hazard == HazardType.NONE:
            return
        
        if hazard == HazardType.CONTROL:
            self.flush_pipeline()
        elif hazard == HazardType.RAW:
            # Forward data instead of stalling
            self.forward_data(stage)
        elif hazard in [HazardType.WAR, HazardType.WAW]:
            self.stall_pipeline()
    
    def stall_pipeline(self) -> None:
        """Stall the pipeline."""
        self.stalled = True
    
    def flush_pipeline(self) -> None:
        """Flush the pipeline."""
        self.flushed = True
        for stage in self.stages.values():
            stage.instruction = None
            stage.write_back = False
    
    def fetch(self) -> None:
        """Fetch stage."""
        if self.stalled or self.flushed:
            return
        
        # Check if PC is within valid memory range
        if self.pc < 0 or self.pc >= len(self.memory.memory) * 4:  # memory size in bytes
            self.stages[PipelineStage.FETCH].instruction = None
            return
        
        # Fetch instruction from memory
        try:
            instruction_data, _ = self.memory.read(self.pc, is_instruction_fetch=True)
            instruction = Instruction.decode(instruction_data)
            if instruction is None:
                print(f"[DEBUG] FETCH: Invalid instruction at PC={self.pc}")
                self.stages[PipelineStage.FETCH].instruction = None
                return
            
            print(f"[DEBUG] FETCH: {instruction}")
            
            # Update pipeline register
            fetch = self.stages[PipelineStage.FETCH]
            fetch.instruction = instruction
            fetch.pc = self.pc  # Save current PC value
            
            # Handle hazards
            self.handle_hazard(PipelineStage.FETCH)
            
        except Exception as e:
            print(f"[DEBUG] FETCH: Error fetching instruction at PC={self.pc}: {e}")
            self.stages[PipelineStage.FETCH].instruction = None
    
    def decode(self) -> None:
        """Decode stage."""
        if self.stalled or self.flushed:
            return
        
        # Get instruction from fetch stage
        fetch = self.stages[PipelineStage.FETCH]
        if not fetch.instruction:
            self.stages[PipelineStage.DECODE].instruction = None
            return
        
        # Move instruction to decode stage
        decode = self.stages[PipelineStage.DECODE]
        decode.instruction = fetch.instruction
        decode.pc = fetch.pc
        
        # Decode instruction fields
        instruction = fetch.instruction
        decode.rs1 = instruction.rs1
        decode.rs2 = instruction.rs2
        decode.rd = instruction.rd
        decode.imm = instruction.imm
        
        # Read register values
        if instruction.rs1 != 0:  # Don't read R0
            decode.rs1 = self.registers.read(instruction.rs1)
        if instruction.rs2 != 0:  # Don't read R0
            decode.rs2 = self.registers.read(instruction.rs2)
        
        # Handle hazards
        self.handle_hazard(PipelineStage.DECODE)
        
        # Forward data if needed
        self.forward_data(PipelineStage.DECODE)
        
        print(f"[DEBUG] DECODE: {instruction}")
        
    def execute(self) -> None:
        """Execute stage."""
        if self.stalled or self.flushed:
            return
        
        # Get instruction from decode stage
        decode = self.stages[PipelineStage.DECODE]
        if not decode.instruction:
            self.stages[PipelineStage.EXECUTE].instruction = None
            return
        
        # Move instruction to execute stage
        execute = self.stages[PipelineStage.EXECUTE]
        execute.instruction = decode.instruction
        execute.pc = decode.pc
        execute.rs1 = decode.rs1
        execute.rs2 = decode.rs2
        execute.rd = decode.rd
        execute.imm = decode.imm
        
        # Execute instruction
        instruction = decode.instruction
        result = 0
        
        if instruction.type == InstructionType.ARITHMETIC:
            if instruction.opcode == Opcode.ADD:
                result = execute.rs1 + execute.rs2
            elif instruction.opcode == Opcode.ADDS:
                result = execute.rs1 + execute.rs2
                self.registers.update_flags(result)
            elif instruction.opcode == Opcode.ADDI:
                result = execute.rs1 + execute.imm
            elif instruction.opcode == Opcode.ADDIS:
                result = execute.rs1 + execute.imm
                self.registers.update_flags(result)
            elif instruction.opcode == Opcode.SUB:
                result = execute.rs1 - execute.rs2
            elif instruction.opcode == Opcode.SUBS:
                result = execute.rs1 - execute.rs2
                self.registers.update_flags(result)
            elif instruction.opcode == Opcode.SUBI:
                result = execute.rs1 - execute.imm
            elif instruction.opcode == Opcode.SUBIS:
                result = execute.rs1 - execute.imm
                self.registers.update_flags(result)
            elif instruction.opcode == Opcode.MUL:
                result = execute.rs1 * execute.rs2
            elif instruction.opcode == Opcode.MULI:
                result = execute.rs1 * execute.imm
            elif instruction.opcode == Opcode.DIV:
                if execute.rs2 != 0:
                    result = execute.rs1 // execute.rs2
            elif instruction.opcode == Opcode.DIVI:
                if execute.imm != 0:
                    result = execute.rs1 // execute.imm
            elif instruction.opcode == Opcode.AND:
                result = execute.rs1 & execute.rs2
            elif instruction.opcode == Opcode.ANDI:
                result = execute.rs1 & execute.imm
            elif instruction.opcode == Opcode.OR:
                result = execute.rs1 | execute.rs2
            elif instruction.opcode == Opcode.ORI:
                result = execute.rs1 | execute.imm
            elif instruction.opcode == Opcode.XOR:
                result = execute.rs1 ^ execute.rs2
            elif instruction.opcode == Opcode.XORI:
                result = execute.rs1 ^ execute.imm
            elif instruction.opcode == Opcode.SHL:
                result = execute.rs1 << execute.imm
            elif instruction.opcode == Opcode.SHR:
                result = execute.rs1 >> execute.imm
            elif instruction.opcode == Opcode.CMP:
                result = execute.rs1 - execute.rs2
                self.registers.update_flags(result)
            elif instruction.opcode == Opcode.MOD:
                if execute.rs2 != 0:
                    result = execute.rs1 % execute.rs2
            elif instruction.opcode == Opcode.MODI:
                if execute.imm != 0:
                    result = execute.rs1 % execute.imm
            elif instruction.opcode == Opcode.MOV:
                result = execute.rs1
            elif instruction.opcode == Opcode.MOVI:
                result = execute.imm
            execute.write_back = True
        
        elif instruction.type == InstructionType.MEMORY:
            if instruction.opcode == Opcode.LDR:
                result = execute.rs1 + execute.imm  # Calculate memory address
            elif instruction.opcode == Opcode.STR:
                result = execute.rs1 + execute.imm  # Calculate memory address
            execute.write_back = instruction.opcode == Opcode.LDR
        
        elif instruction.type == InstructionType.CONTROL:
            if instruction.opcode == Opcode.JMP:
                self.pc = execute.rs1 + execute.imm
                self.flush_pipeline()
            elif instruction.opcode == Opcode.BEQ:
                if self.registers.get_zero_flag():
                    self.pc = execute.pc + execute.imm
                    self.flush_pipeline()
            elif instruction.opcode == Opcode.BLT:
                if self.registers.get_negative_flag():
                    self.pc = execute.pc + execute.imm
                    self.flush_pipeline()
            elif instruction.opcode == Opcode.CAL:
                self.pc = execute.rs1 + execute.imm
                self.flush_pipeline()
            elif instruction.opcode == Opcode.FLUSH:
                self.memory.flush_cache_line(execute.rs1)
            execute.write_back = False
        
        # Store result
        execute.alu_result = result
        
        # Handle hazards
        self.handle_hazard(PipelineStage.EXECUTE)
        
        # Forward data if needed
        self.forward_data(PipelineStage.EXECUTE)
        
        print(f"[DEBUG] EXECUTE: {instruction}")
    
    def memory_stage(self) -> None:
        """Memory stage."""
        if self.stalled or self.flushed:
            return
        
        # Get instruction from execute stage
        execute = self.stages[PipelineStage.EXECUTE]
        if not execute.instruction:
            return
        
        # Move instruction to memory stage
        memory = self.stages[PipelineStage.MEMORY]
        memory.instruction = execute.instruction
        memory.pc = execute.pc
        memory.rd = execute.rd
        memory.alu_result = execute.alu_result
        memory.write_back = execute.write_back
        
        # Handle memory operations
        instruction = execute.instruction
        if instruction.type == InstructionType.MEMORY:
            if instruction.opcode == Opcode.LDR:
                # Load from memory
                addr = execute.alu_result
                data, _ = self.memory.read(addr)
                memory.alu_result = data  # Store loaded data in alu_result
                memory.write_back = True
            elif instruction.opcode == Opcode.STR:
                # Store to memory
                addr = execute.alu_result
                self.memory.write(addr, execute.rs2)
                memory.write_back = False
        
        # Clear execute stage
        self.stages[PipelineStage.EXECUTE].instruction = None
        
        # Handle hazards
        self.handle_hazard(PipelineStage.MEMORY)
        
        # Forward data if needed
        self.forward_data(PipelineStage.MEMORY)
        
        print(f"[DEBUG] MEMORY: {instruction}")
    
    def writeback(self) -> None:
        """Writeback stage."""
        if self.stalled or self.flushed:
            return
        
        # Get instruction from memory stage
        memory = self.stages[PipelineStage.MEMORY]
        if not memory.instruction:
            return
        
        # Get result from memory stage
        instruction = memory.instruction
        result = memory.alu_result
        
        # Update register file if needed
        if memory.write_back:
            if instruction.rd != 0:  # Don't write to R0
                self.registers.set(instruction.rd, result)
                print(f"[DEBUG] WRITEBACK: r{instruction.rd} = {result}")
        
        # Clear memory stage
        self.stages[PipelineStage.MEMORY].instruction = None
        
        # Update instruction count
        self.instructions += 1
    
    def clear_pipeline_stages(self):
        for stage in self.stages:
            self.stages[stage].instruction = None

    def advance_sequential_stage(self):
        """Move instruction from previous stage to current stage."""
        if self.sequential_stage == 0:  # FETCH
            self.fetch()
        elif self.sequential_stage == 1:  # DECODE
            # Move instruction from fetch to decode
            self.stages[PipelineStage.DECODE] = self.stages[PipelineStage.FETCH]
            self.stages[PipelineStage.FETCH] = PipelineRegister()
            self.decode()
        elif self.sequential_stage == 2:  # EXECUTE
            # Move instruction from decode to execute
            self.stages[PipelineStage.EXECUTE] = self.stages[PipelineStage.DECODE]
            self.stages[PipelineStage.DECODE] = PipelineRegister()
            self.execute()
        elif self.sequential_stage == 3:  # MEMORY
            # Move instruction from execute to memory
            self.stages[PipelineStage.MEMORY] = self.stages[PipelineStage.EXECUTE]
            self.stages[PipelineStage.EXECUTE] = PipelineRegister()
            self.memory_stage()
        elif self.sequential_stage == 4:  # WRITEBACK
            # Move instruction from memory to writeback
            self.stages[PipelineStage.WRITEBACK] = self.stages[PipelineStage.MEMORY]
            self.stages[PipelineStage.MEMORY] = PipelineRegister()
            self.writeback()
            self.cycles += 5  # Only increment after a full instruction
        
        # Move to next stage
        self.sequential_stage = (self.sequential_stage + 1) % 5

    def step(self) -> None:
        """Execute one pipeline cycle."""
        if not self.enabled:
            # Sequential execution
            if self.sequential_stage == 0:  # Fetch
                self.fetch()
                self.sequential_stage = 1
            elif self.sequential_stage == 1:  # Decode
                self.decode()
                self.sequential_stage = 2
            elif self.sequential_stage == 2:  # Execute
                self.execute()
                self.sequential_stage = 3
            elif self.sequential_stage == 3:  # Memory
                self.memory_stage()
                self.sequential_stage = 4
            elif self.sequential_stage == 4:  # Writeback
                self.writeback()
                self.sequential_stage = 0
                # Update PC after completing the instruction
                if not self.stalled and not self.flushed:
                    self.pc += 4
                    self.instructions += 1  # Count completed instruction
            self.cycles += 1  # Increment cycles for each step
        else:
            # Pipelined execution
            # Execute stages in reverse order to avoid overwriting data
            self.writeback()
            self.memory_stage()
            self.execute()
            self.decode()
            self.fetch()
            
            # Update PC after fetch if not stalled or flushed
            if not self.stalled and not self.flushed:
                self.pc += 4
            
            # Print pipeline state
            print(f"[DEBUG] Pipeline state: PC={self.pc}")
            
            # Check if all stages are empty
            all_empty = True
            for stage in self.stages.values():
                if stage.instruction is not None:
                    all_empty = False
                    break
            
            if all_empty:
                print("[DEBUG] All pipeline stages are empty. Program complete.")
                return

    def run(self, num_cycles: int) -> None:
        """Run pipeline for specified number of cycles."""
        for _ in range(num_cycles):
            self.step()

    def get_stats(self) -> Dict[str, float]:
        """Get pipeline statistics."""
        return {
            "cycles": self.cycles,
            "instructions": self.instructions,
            "cpi": self.cycles / max(1, self.instructions),
            "stalls": self.stall_count,
            "flushes": self.flush_count
        } 