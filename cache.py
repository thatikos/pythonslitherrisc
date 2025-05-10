from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np

@dataclass
class CacheLine:
    """Cache line structure."""
    valid: bool = False
    dirty: bool = False
    tag: int = 0
    data: List[int] = None
    lru_counter: int = 0  # For LRU replacement
    
    def __post_init__(self):
        if self.data is None:
            self.data = [0] * 4  # 4 words per line

class Cache:
    def __init__(self, size: int, line_size: int, access_time: int):
        """Initialize cache.
        
        Args:
            size: Number of cache lines
            line_size: Number of words per line
            access_time: Access time in cycles
        """
        self.size = size
        self.line_size = line_size
        self.access_time = access_time
        self.lines = [CacheLine(data=[0] * line_size) for _ in range(size)]
        
        # Performance counters
        self.hits = 0
        self.misses = 0
        self.cycles = 0
        self.lru_counter = 0  # Global counter for LRU
    
    def reset(self) -> None:
        """Reset cache state."""
        for line in self.lines:
            line.valid = False
            line.dirty = False
            line.tag = 0
            line.data = [0] * self.line_size
            line.lru_counter = 0
        self.hits = 0
        self.misses = 0
        self.cycles = 0
        self.lru_counter = 0
    
    def get_line_index(self, address: int) -> int:
        """Get cache line index from address."""
        return (address // (self.line_size * 4)) % self.size
    
    def get_tag(self, address: int) -> int:
        """Get cache line tag from address."""
        return address // (self.size * self.line_size * 4)
    
    def get_offset(self, address: int) -> int:
        """Get word offset within cache line."""
        return (address // 4) % self.line_size
    
    def read(self, address: int, is_instruction_fetch: bool = False) -> Tuple[bool, int, int]:
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
        cycles = self.access_time
        
        # Cache hit
        if line.valid and line.tag == tag:
            self.hits += 1
            # Update LRU counter
            self.lru_counter += 1
            line.lru_counter = self.lru_counter
            return True, line.data[offset], cycles
        
        # Cache miss
        self.misses += 1
        return False, 0, cycles
    
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
        cycles = self.access_time
        
        # Cache hit
        if line.valid and line.tag == tag:
            self.hits += 1
            line.data[offset] = value
            line.dirty = True
            # Update LRU counter
            self.lru_counter += 1
            line.lru_counter = self.lru_counter
            return True, cycles
        
        # Cache miss
        self.misses += 1
        
        # Allocate new line
        line.valid = True
        line.tag = tag
        line.data[offset] = value
        line.dirty = True
        # Update LRU counter
        self.lru_counter += 1
        line.lru_counter = self.lru_counter
        
        return False, cycles
    
    def get_stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate
        }

class MemorySystem:
    def __init__(self, memory_size: int = 4096):
        """Initialize memory system.
        
        Args:
            memory_size: Size of main memory in words
        """
        # Main memory (4KB)
        self.memory = np.zeros(memory_size, dtype=np.int64)
        
        # L1 Cache (16 lines, 4 words per line)
        self.L1_cache = Cache(16, 4, 1)
        
        # L2 Cache (64 lines, 4 words per line)
        self.L2_cache = Cache(64, 4, 10)
        
        # Memory access time (100 cycles)
        self.memory_access_time = 100
        
        # Track last instruction fetch
        self.last_fetch_addr = None
    
    def reset(self) -> None:
        """Reset memory system state."""
        self.memory.fill(0)
        self.L1_cache.reset()
        self.L2_cache.reset()
        self.last_fetch_addr = None
    
    def load_program(self, program: List[int]) -> None:
        """Load program into memory.
        
        Args:
            program: List of instructions to load
        """
        # Reset memory and caches
        self.reset()
        
        # Load program into memory at word-aligned addresses
        for i, instruction in enumerate(program):
            addr = i * 4  # Word-aligned addresses
            self.memory[addr] = instruction & 0xFFFFFFFF  # Ensure 32-bit value
    
    def read(self, address: int, is_instruction_fetch: bool = False) -> Tuple[int, int]:
        """Read from memory system.
        
        Args:
            address: Memory address to read
            is_instruction_fetch: Whether this read is for instruction fetch
            
        Returns:
            Tuple of (data, cycles)
            
        Raises:
            ValueError: If address is invalid
        """
        if not 0 <= address < len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        
        # For instruction fetches, only count cache access if it's a new fetch
        if is_instruction_fetch:
            if address == self.last_fetch_addr:
                return self.memory[address], 0
            self.last_fetch_addr = address
        
        # Try L1 cache first
        hit, data, cycles = self.L1_cache.read(address, is_instruction_fetch)
        if hit:
            return data, cycles
        
        # Try L2 cache
        hit, data, cycles2 = self.L2_cache.read(address, is_instruction_fetch)
        if hit:
            return data, cycles + cycles2
        
        # Cache miss, read from memory
        data = self.memory[address]
        
        return data, cycles + cycles2 + self.memory_access_time
    
    def write(self, address: int, value: int) -> int:
        """Write to memory system.
        
        Args:
            address: Memory address to write
            value: Value to write
            
        Returns:
            Number of cycles taken
            
        Raises:
            ValueError: If address is invalid
        """
        if not 0 <= address < len(self.memory):
            raise ValueError(f"Invalid memory address: {address}")
        
        # Write-through policy: write to all levels
        self.memory[address] = value
        
        hit1, cycles1 = self.L1_cache.write(address, value)
        hit2, cycles2 = self.L2_cache.write(address, value)
        
        return cycles1 + cycles2 + self.memory_access_time
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get memory system statistics."""
        return {
            "L1": self.L1_cache.get_stats(),
            "L2": self.L2_cache.get_stats()
        }
    
    def flush_cache_line(self, address: int) -> None:
        """Force writeback of cache line to memory."""
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