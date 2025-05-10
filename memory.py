from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import numpy as np

@dataclass
class CacheLine:
    valid: bool = False
    tag: int = 0
    data: List[int] = None
    dirty: bool = False
    
    def __post_init__(self):
        if self.data is None:
            self.data = [0] * 8  # 8 words per line

class Cache:
    def __init__(self, size: int, line_size: int, access_time: int):
        """Initialize a cache.
        
        Args:
            size: Number of cache lines
            line_size: Words per cache line
            access_time: Access time in cycles
        """
        self.size = size
        self.line_size = line_size
        self.access_time = access_time
        self.lines = [CacheLine() for _ in range(size)]
        self.hits = 0
        self.misses = 0
        self.last_miss_addr = None
        self.instruction_fetch_count = 0
    
    def reset(self) -> None:
        """Reset cache state."""
        for line in self.lines:
            line.valid = False
            line.tag = 0
            line.data = [0] * self.line_size
            line.dirty = False
        self.hits = 0
        self.misses = 0
        self.last_miss_addr = None
        self.instruction_fetch_count = 0
    
    def get_line_index(self, address: int) -> int:
        """Get cache line index for an address."""
        return (address // self.line_size) % self.size
    
    def get_tag(self, address: int) -> int:
        """Get tag for an address."""
        return address // (self.size * self.line_size)
    
    def get_offset(self, address: int) -> int:
        """Get word offset within a cache line."""
        return address % self.line_size
    
    def read(self, address: int, is_instruction_fetch: bool = False) -> Tuple[bool, Optional[int], int]:
        """Read from cache.
        
        Args:
            address: Memory address to read
            is_instruction_fetch: Whether this read is for instruction fetch
            
        Returns:
            Tuple of (hit, data, cycles)
        """
        line_index = self.get_line_index(address)
        tag = self.get_tag(address)
        offset = self.get_offset(address)
        
        line = self.lines[line_index]
        if line.valid and line.tag == tag:
            if not is_instruction_fetch:
                self.hits += 1
            return True, line.data[offset], self.access_time
        
        # Only count as a miss if it's not an instruction fetch or if it's the first fetch
        if not is_instruction_fetch or self.instruction_fetch_count == 0:
            if address != self.last_miss_addr:
                self.misses += 1
                self.last_miss_addr = address
        
        if is_instruction_fetch:
            self.instruction_fetch_count += 1
        
        return False, None, self.access_time
    
    def write(self, address: int, value: int) -> Tuple[bool, int]:
        """Write to cache.
        
        Args:
            address: Memory address to write
            value: Value to write
            
        Returns:
            Tuple of (hit, cycles)
        """
        line_index = self.get_line_index(address)
        tag = self.get_tag(address)
        offset = self.get_offset(address)
        
        line = self.lines[line_index]
        if line.valid and line.tag == tag:
            self.hits += 1
            line.data[offset] = value & 0xFFFFFFFF  # Ensure 32-bit value
            line.dirty = True
            return True, self.access_time
        
        # Only count as a miss if it's a different address than the last miss
        if address != self.last_miss_addr:
            self.misses += 1
            self.last_miss_addr = address
        
        # On write miss, allocate a new line
        line.valid = True
        line.tag = tag
        line.data[offset] = value & 0xFFFFFFFF  # Ensure 32-bit value
        line.dirty = True
        return False, self.access_time
    
    def get_stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

class MemorySystem:
    def __init__(self, memory_size: int = 16384, cache_enabled: bool = True, pipeline_enabled: bool = True):
        """Initialize memory system.
        
        Args:
            memory_size: Size of main memory in words (default: 16384 = 64KB)
            cache_enabled: Whether cache is enabled
            pipeline_enabled: Whether pipeline is enabled
        """
        # Main memory (64KB)
        self.memory = np.zeros(memory_size, dtype=np.int64)
        
        # Cache configuration
        self.cache_enabled = cache_enabled
        self.pipeline_enabled = pipeline_enabled
        
        # L1 Cache (32 lines, 8 words per line) - Optimized for matrix operations
        self.L1_cache = Cache(32, 8, 1)
        
        # L2 Cache (128 lines, 8 words per line) - Larger to reduce misses
        self.L2_cache = Cache(128, 8, 10)
        
        # Memory access time (100 cycles)
        self.memory_access_time = 100
        
        # Track last instruction fetch
        self.last_fetch_addr = None
        
        # Performance counters
        self.cycles = 0
        self.program_end = 0  # Track end address of loaded program
    
    def reset(self) -> None:
        """Reset memory system state."""
        self.memory.fill(0)
        self.L1_cache.reset()
        self.L2_cache.reset()
        self.last_fetch_addr = None
        self.cycles = 0
        self.program_end = 0
    
    def load_program(self, program: List[int]) -> None:
        """Load program into memory.
        
        Args:
            program: List of instructions to load
        """
        # Reset memory and caches
        self.reset()
        
        # Load program into memory at word-aligned addresses
        for i, instruction in enumerate(program):
            addr = i  # Instructions are already word-aligned
            self.memory[addr] = instruction & 0xFFFFFFFF  # Ensure 32-bit value
            
            # Pre-load program into L1 cache
            if self.cache_enabled:
                line_index = self.L1_cache.get_line_index(addr)
                tag = self.L1_cache.get_tag(addr)
                offset = self.L1_cache.get_offset(addr)
                
                # Allocate cache line if needed
                line = self.L1_cache.lines[line_index]
                if not line.valid or line.tag != tag:
                    line.valid = True
                    line.tag = tag
                    line.data = [0] * self.L1_cache.line_size
                
                # Load instruction into cache line
                line.data[offset] = instruction & 0xFFFFFFFF
        
        # Update program end address
        self.program_end = len(program)
    
    def read(self, address: int, is_instruction_fetch: bool = False) -> Tuple[int, int]:
        """Read from memory system.
        
        Args:
            address: Memory address to read (byte address)
            is_instruction_fetch: Whether this read is for instruction fetch
            
        Returns:
            Tuple of (data, cycles)
            
        Raises:
            ValueError: If address is invalid
        """
        word_index = address // 4
        if not 0 <= word_index < len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
            
        cycles = 0
        if not self.cache_enabled:
            cycles = self.memory_access_time
            self.cycles += cycles
            return self.memory[word_index], cycles
            
        # For instruction fetches, only count cache access if it's a new fetch
        if is_instruction_fetch:
            if address == self.last_fetch_addr:
                return self.memory[word_index], 0
            self.last_fetch_addr = address
            
        # Try L1 cache first
        hit, data, cycles1 = self.L1_cache.read(address, is_instruction_fetch)
        if hit:
            self.cycles += cycles1
            return data, cycles1
            
        # Try L2 cache
        hit, data, cycles2 = self.L2_cache.read(address, is_instruction_fetch)
        if hit:
            # On L2 hit, update L1 cache
            line_index = self.L1_cache.get_line_index(address)
            tag = self.L1_cache.get_tag(address)
            offset = self.L1_cache.get_offset(address)
            
            # Allocate L1 cache line
            line = self.L1_cache.lines[line_index]
            line.valid = True
            line.tag = tag
            line.data = [0] * self.L1_cache.line_size
            line.data[offset] = data
            
            cycles = cycles1 + cycles2
            self.cycles += cycles
            return data, cycles
            
        # Cache miss, read from memory
        data = self.memory[word_index]
        
        # Update both cache levels
        line_index = self.L1_cache.get_line_index(address)
        tag = self.L1_cache.get_tag(address)
        offset = self.L1_cache.get_offset(address)
        
        # Update L1 cache
        line = self.L1_cache.lines[line_index]
        line.valid = True
        line.tag = tag
        line.data = [0] * self.L1_cache.line_size
        line.data[offset] = data
        
        # Update L2 cache
        line_index = self.L2_cache.get_line_index(address)
        tag = self.L2_cache.get_tag(address)
        offset = self.L2_cache.get_offset(address)
        line = self.L2_cache.lines[line_index]
        line.valid = True
        line.tag = tag
        line.data = [0] * self.L2_cache.line_size
        line.data[offset] = data
        
        # Calculate total cycles
        cycles = cycles1 + cycles2 + self.memory_access_time
        self.cycles += cycles
        return data, cycles
    
    def write(self, address: int, value: int) -> int:
        """Write to memory system.
        
        Args:
            address: Memory address to write (byte address)
            value: Value to write
            
        Returns:
            Number of cycles taken
            
        Raises:
            ValueError: If address is invalid
        """
        word_index = address // 4
        if not 0 <= word_index < len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        cycles = 0
        if not self.cache_enabled:
            self.memory[word_index] = value
            cycles = self.memory_access_time
            self.cycles += cycles
            return cycles
        # Write-through policy: write to all levels
        self.memory[word_index] = value
        # Try L1 cache first
        hit1, cycles1 = self.L1_cache.write(address, value)
        # Try L2 cache
        hit2, cycles2 = self.L2_cache.write(address, value)
        # Calculate total cycles
        cycles = cycles1 + cycles2 + self.memory_access_time
        self.cycles += cycles
        return cycles
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get memory system statistics."""
        return {
            "L1": self.L1_cache.get_stats(),
            "L2": self.L2_cache.get_stats(),
            "cycles": self.cycles
        }
    
    def flush_cache_line(self, address: int) -> None:
        """Force writeback of cache line to memory."""
        if not self.cache_enabled:
            return
            
        # Flush L1 cache
        line_index = self.L1_cache.get_line_index(address)
        tag = self.L1_cache.get_tag(address)
        L1_line = self.L1_cache.lines[line_index]
        
        if L1_line.valid and L1_line.tag == tag:
            for i in range(4):
                mem_addr = (tag * self.L1_cache.size * 4) + (line_index * 4) + i
                self.memory[mem_addr] = L1_line.data[i]
            L1_line.dirty = False
        
        # Flush L2 cache
        line_index = self.L2_cache.get_line_index(address)
        tag = self.L2_cache.get_tag(address)
        L2_line = self.L2_cache.lines[line_index]
        
        if L2_line.valid and L2_line.tag == tag:
            for i in range(4):
                mem_addr = (tag * self.L2_cache.size * 4) + (line_index * 4) + i
                self.memory[mem_addr] = L2_line.data[i]
            L2_line.dirty = False 