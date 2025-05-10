from memory import Memory

def test_memory_access():
    # Create memory with cache enabled
    mem_with_cache = Memory(size=1024, cache_enabled=True)
    
    # Create memory with cache disabled
    mem_without_cache = Memory(size=1024, cache_enabled=False)
    
    # Test sequence
    test_addresses = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
    test_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    print("Testing memory access with cache enabled:")
    print("-" * 50)
    
    # Write values
    for addr, val in zip(test_addresses, test_values):
        mem_with_cache.write(addr, val)
        print(f"Wrote {val} to address {addr}")
    
    # Read values (should hit cache)
    print("\nReading values (should hit cache):")
    for addr in test_addresses:
        val = mem_with_cache.read(addr)
        print(f"Read {val} from address {addr}")
    
    # Read values again (should hit cache)
    print("\nReading values again (should hit cache):")
    for addr in test_addresses:
        val = mem_with_cache.read(addr)
        print(f"Read {val} from address {addr}")
    
    # Get stats
    stats = mem_with_cache.get_stats()
    print("\nCache statistics:")
    print(f"Total cycles: {stats['cycles']}")
    print(f"Cache hits: {stats['cache_hits']}")
    print(f"Cache misses: {stats['cache_misses']}")
    print(f"Hit rate: {stats['hit_rate']:.2%}")
    
    print("\nTesting memory access without cache:")
    print("-" * 50)
    
    # Write values
    for addr, val in zip(test_addresses, test_values):
        mem_without_cache.write(addr, val)
        print(f"Wrote {val} to address {addr}")
    
    # Read values (no cache)
    print("\nReading values (no cache):")
    for addr in test_addresses:
        val = mem_without_cache.read(addr)
        print(f"Read {val} from address {addr}")
    
    # Get stats
    stats = mem_without_cache.get_stats()
    print("\nMemory statistics (no cache):")
    print(f"Total cycles: {stats['cycles']}")

if __name__ == "__main__":
    test_memory_access() 