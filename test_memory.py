from memory import MemorySystem

def test_sequential_access():
    """Test sequential memory access pattern."""
    print("\nTesting sequential access pattern:")
    print("-" * 50)
    
    # Create memory system with cache and pipeline enabled
    mem = MemorySystem(memory_size=4096, cache_enabled=True, pipeline_enabled=True)
    
    # Write sequential values
    print("Writing sequential values...")
    for i in range(0, 64, 4):  # Write 16 cache lines
        mem.write(i, i)
    
    # Read values back (should hit in L1 cache)
    print("\nReading values (should hit in L1 cache)...")
    for i in range(0, 64, 4):
        value, cycles = mem.read(i)
        print(f"Address {i:04x}: Value={value}, Cycles={cycles}")
    
    # Get stats
    stats = mem.get_stats()
    print("\nCache statistics:")
    print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
    print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
    print(f"Total cycles: {stats['cycles']}")

def test_random_access():
    """Test random memory access pattern."""
    print("\nTesting random access pattern:")
    print("-" * 50)
    
    # Create memory system with cache and pipeline enabled
    mem = MemorySystem(memory_size=4096, cache_enabled=True, pipeline_enabled=True)
    
    # Write random values
    addresses = [0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700, 0x800]
    values = [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666, 0x7777, 0x8888]
    
    print("Writing random values...")
    for addr, val in zip(addresses, values):
        mem.write(addr, val)
    
    # Read values back (should miss in L1, hit in L2)
    print("\nReading values (should miss in L1, hit in L2)...")
    for addr in addresses:
        value, cycles = mem.read(addr)
        print(f"Address {addr:04x}: Value={value}, Cycles={cycles}")
    
    # Get stats
    stats = mem.get_stats()
    print("\nCache statistics:")
    print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
    print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
    print(f"Total cycles: {stats['cycles']}")

def test_cache_disabled():
    """Test memory access with cache disabled."""
    print("\nTesting memory access with cache disabled:")
    print("-" * 50)
    
    # Create memory system with cache disabled
    mem = MemorySystem(memory_size=4096, cache_enabled=False, pipeline_enabled=True)
    
    # Write values
    print("Writing values...")
    for i in range(0, 16, 4):
        mem.write(i, i)
    
    # Read values back (should always access main memory)
    print("\nReading values (should always access main memory)...")
    for i in range(0, 16, 4):
        value, cycles = mem.read(i)
        print(f"Address {i:04x}: Value={value}, Cycles={cycles}")
    
    # Get stats
    stats = mem.get_stats()
    print("\nMemory statistics:")
    print(f"Total cycles: {stats['cycles']}")

def test_pipeline_disabled():
    """Test memory access with pipeline disabled."""
    print("\nTesting memory access with pipeline disabled:")
    print("-" * 50)
    
    # Create memory system with pipeline disabled
    mem = MemorySystem(memory_size=4096, cache_enabled=True, pipeline_enabled=False)
    
    # Write values
    print("Writing values...")
    for i in range(0, 16, 4):
        mem.write(i, i)
    
    # Read values back
    print("\nReading values...")
    for i in range(0, 16, 4):
        value, cycles = mem.read(i)
        print(f"Address {i:04x}: Value={value}, Cycles={cycles}")
    
    # Get stats
    stats = mem.get_stats()
    print("\nCache statistics:")
    print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
    print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
    print(f"Total cycles: {stats['cycles']}")

def test_instruction_fetch():
    """Test instruction fetch behavior."""
    print("\nTesting instruction fetch behavior:")
    print("-" * 50)
    
    # Create memory system
    mem = MemorySystem(memory_size=4096, cache_enabled=True, pipeline_enabled=True)
    
    # Load a simple program
    program = [0x12345678, 0x87654321, 0x11111111, 0x22222222]
    mem.load_program(program)
    
    # Fetch instructions
    print("Fetching instructions...")
    for i in range(0, 16, 4):
        value, cycles = mem.read(i, is_instruction_fetch=True)
        print(f"Address {i:04x}: Value={value:08x}, Cycles={cycles}")
    
    # Get stats
    stats = mem.get_stats()
    print("\nCache statistics:")
    print(f"L1 Cache: Hits={stats['L1']['hits']}, Misses={stats['L1']['misses']}, Hit Rate={stats['L1']['hit_rate']:.2f}%")
    print(f"L2 Cache: Hits={stats['L2']['hits']}, Misses={stats['L2']['misses']}, Hit Rate={stats['L2']['hit_rate']:.2f}%")
    print(f"Total cycles: {stats['cycles']}")

if __name__ == "__main__":
    # Run all tests
    test_sequential_access()
    test_random_access()
    test_cache_disabled()
    test_pipeline_disabled()
    test_instruction_fetch() 