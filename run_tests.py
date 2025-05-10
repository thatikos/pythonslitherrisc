import pytest
import sys

def main():
    """Run all pipeline tests."""
    # Run tests with verbose output
    args = ['-v', 'tests/test_pipeline.py']
    
    # Add any command line arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == '__main__':
    sys.exit(main()) 