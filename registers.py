from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List

class SpecialRegisters(IntEnum):
    """Special register indices."""
    PC = 32    # Program Counter
    LR = 33    # Link Register
    SP = 34    # Stack Pointer
    STAT = 35  # Status Register (flags)
    XZR = 36   # Constant Zero Register

@dataclass
class Flags:
    """Processor flags."""
    zero: bool = False      # Zero flag
    negative: bool = False  # Negative flag
    carry: bool = False     # Carry flag
    overflow: bool = False  # Overflow flag
    error: bool = False     # Error flag (e.g., division by zero)
    
    def update(self, result: int, carry: bool = False, overflow: bool = False) -> None:
        """Update flags based on result and operation."""
        self.zero = result == 0
        self.negative = (result & 0x80000000) != 0
        self.carry = carry
        self.overflow = overflow
    
    def clear(self) -> None:
        """Clear all flags."""
        self.zero = False
        self.negative = False
        self.carry = False
        self.overflow = False
        self.error = False

class RegisterFile:
    """Register file implementation."""
    def __init__(self):
        """Initialize register file."""
        # General purpose registers (R0-R31)
        self.registers = [0] * 32
        
        # Special registers
        self.pc = 0         # Program Counter
        self.lr = 0         # Link Register
        self.sp = 0x1000    # Stack Pointer (initialized to 4096)
        self.flags = Flags()
        
        # Register 0 is hardwired to 0
        self.registers[0] = 0
    
    def reset(self) -> None:
        """Reset register file state."""
        self.registers = [0] * 32
        self.pc = 0
        self.lr = 0
        self.sp = 0x1000
        self.flags = Flags()
    
    def get(self, index: int) -> int:
        """Get register value.
        
        Args:
            index: Register index (0-31 for general purpose, 32+ for special)
            
        Returns:
            Register value
        """
        if index == SpecialRegisters.XZR:
            return 0
        elif 0 <= index < 32:
            return self.registers[index]
        elif index == SpecialRegisters.PC:
            return self.pc
        elif index == SpecialRegisters.LR:
            return self.lr
        elif index == SpecialRegisters.SP:
            return self.sp
        else:
            raise ValueError(f"Invalid register index: {index}")
    
    def set(self, index: int, value: int) -> None:
        """Set register value.
        
        Args:
            index: Register index (0-31 for general purpose, 32+ for special)
            value: Value to set
        """
        # Ensure 32-bit value
        value = value & 0xFFFFFFFF
        
        if index in [0, SpecialRegisters.XZR]:
            return  # R0 and XZR are read-only
        elif 0 < index < 32:
            self.registers[index] = value
        elif index == SpecialRegisters.PC:
            self.pc = value
        elif index == SpecialRegisters.LR:
            self.lr = value
        elif index == SpecialRegisters.SP:
            self.sp = value
        else:
            raise ValueError(f"Invalid register index: {index}")
    
    def update_flags(self, result: int, carry: bool = False, overflow: bool = False) -> None:
        """Update flags based on result and operation."""
        self.flags.update(result, carry, overflow)
    
    def get_zero_flag(self) -> bool:
        """Get zero flag."""
        return self.flags.zero
    
    def get_negative_flag(self) -> bool:
        """Get negative flag."""
        return self.flags.negative
    
    def get_carry_flag(self) -> bool:
        """Get carry flag."""
        return self.flags.carry
    
    def get_overflow_flag(self) -> bool:
        """Get overflow flag."""
        return self.flags.overflow
    
    def get_error_flag(self) -> bool:
        """Get error flag."""
        return self.flags.error
    
    def set_overflow_flag(self, value: bool) -> None:
        """Set overflow flag."""
        self.flags.overflow = value
    
    def set_error_flag(self, value: bool) -> None:
        """Set error flag."""
        self.flags.error = value
    
    def get_flags(self) -> Dict[str, bool]:
        """Get current flags state."""
        return {
            "zero": self.flags.zero,
            "negative": self.flags.negative,
            "carry": self.flags.carry,
            "overflow": self.flags.overflow,
            "error": self.flags.error
        }
    
    def dump(self) -> Dict[str, int]:
        """Dump register file state."""
        state = {f"R{i}": self.registers[i] for i in range(32)}
        state.update({
            "PC": self.pc,
            "LR": self.lr,
            "SP": self.sp,
            "STAT": self.get_flags()
        })
        return state 