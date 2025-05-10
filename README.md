# SlitherRISC Simulator

A custom 32-bit RISC architecture simulator designed to run the classic game "Snake". This project implements a complete instruction set architecture (ISA) with pipelining, cache system, and a graphical user interface.

## Features

- 32-bit RISC architecture inspired by ARMv8
- 32 general-purpose registers including special-purpose registers (LR, XZR, STAT)
- Support for arithmetic, logical, shift, memory access, and control flow instructions
- 5-stage pipeline implementation
- Two-level cache system (L1 and L2) with write-through, no-allocate policy
- Memory-mapped I/O for graphics
- Interactive GUI for visualization and control
- Support for both continuous and single-step execution modes

## Requirements

- Python 3.8+
- NumPy
- Pygame
- Pytest (for testing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/slitherrisc-simulator.git
cd slitherrisc-simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

- `isa.py`: Instruction Set Architecture definitions and instruction encoding
- `pipeline.py`: Pipeline implementation with hazard detection and forwarding
- `cache.py`: Cache system implementation
- `registers.py`: Register file implementation
- `tests/`: Unit and integration tests
- `run_tests.py`: Test runner script

## Usage

1. Run the simulator:
```bash
python simulator.py
```

2. Run tests:
```bash
python run_tests.py
```

## Architecture Details

### Instruction Types
- Type 00: Arithmetic (ADD, SUB, MUL, DIV, etc.)
- Type 01: Memory Access (LOAD, STORE)
- Type 10: Control Flow (JMP, BEQ, BLT, etc.)

### Memory Organization
- Princeton architecture (unified instruction and data memory)
- Memory-mapped I/O for graphics
- Frame buffer for game display

### Pipeline Stages
1. Fetch
2. Decode
3. Execute
4. Memory
5. Write Back

## Development

### Running Tests
```bash
python run_tests.py
```

### Adding New Instructions
1. Add instruction encoding in `isa.py`
2. Implement execution in `pipeline.py`
3. Add test cases in `tests/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request