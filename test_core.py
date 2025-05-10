import pytest
from registers import RegisterFile
from cache import MemorySystem

def test_register_file():
    rf = RegisterFile()
    
    # Test general purpose registers
    rf.set(0, 42)
    assert rf.get(0) == 42
    
    # Test XZR (register 31)
    rf.set(31, 100)  # Should be ignored
    assert rf.get(31) == 0
    
    # Test status flags
    rf.update_flags(0, False, False)
    assert rf.get_flag(rf.FLAGS.ZERO)
    assert not rf.get_flag(rf.FLAGS.NEGATIVE)
    assert not rf.get_flag(rf.FLAGS.CARRY)
    assert not rf.get_flag(rf.FLAGS.OVERFLOW)
    
    # Test reset
    rf.reset()
    assert rf.get(0) == 0
    assert not rf.get_flag(rf.FLAGS.ZERO)

def test_memory_system():
    mem = MemorySystem()
    
    # Test basic read/write
    mem.write(0, 42)
    data, cycles = mem.read(0)
    assert data == 42
    
    # Test cache behavior
    data, cycles = mem.read(0)  # Should hit in L1
    assert cycles == 1
    
    # Test program loading
    program = [1, 2, 3, 4]
    mem.load_program(program)
    for i in range(len(program)):
        data, _ = mem.read(i)
        assert data == program[i]
    
    # Test statistics
    stats = mem.get_stats()
    assert "L1" in stats
    assert "L2" in stats
    assert "hits" in stats["L1"]
    assert "misses" in stats["L1"]
    assert "hit_rate" in stats["L1"]
    
    # Test reset
    mem.reset()
    data, _ = mem.read(0)
    assert data == 0 