from memory import MemorySystem
from pipeline import Pipeline
from registers import RegisterFile
from gui import SimulatorGUI
from assembler import assemble_file
import os
import sys

def main():
    try:
        # Initialize components
        memory = MemorySystem()
        registers = RegisterFile()
        pipeline = Pipeline(memory, registers)
        
        # Try to load test program if it exists
        test_program = 'gui_test.asm'
        if os.path.exists(test_program):
            program, errors = assemble_file(test_program)
            if errors:
                print("Assembly errors:")
                for error in errors:
                    print(error)
                print("Starting simulator without program loaded.")
                program = []
            memory.load_program(program)
        else:
            print(f"Test program '{test_program}' not found.")
            print("Starting simulator without program loaded.")
        
        # Create and run GUI
        gui = SimulatorGUI(memory, pipeline, registers)
        gui.run()
    except ImportError as e:
        print(f"Error importing required modules: {str(e)}")
        print("Make sure all required modules are in your Python path.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running simulator: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 