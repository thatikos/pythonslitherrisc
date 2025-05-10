import unittest
from assembler import Assembler
from isa import Instruction, InstructionType, Opcode

class TestAssembler(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.assembler = Assembler()
    
    def test_arithmetic_instructions(self):
        """Test arithmetic instruction parsing."""
        # Test ADD
        source = "add r1, r2, r3"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test ADDI
        source = "addi r1, r2, 10"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test invalid register
        source = "add r32, r1, r2"
        instructions, errors = self.assembler.assemble(source)
        self.assertTrue(len(errors) > 0)
        
        # Test invalid immediate
        source = "addi r1, r2, invalid"
        instructions, errors = self.assembler.assemble(source)
        self.assertTrue(len(errors) > 0)
    
    def test_memory_instructions(self):
        """Test memory instruction parsing."""
        # Test LDR
        source = "ldr r1, [r2, 100]"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test STR
        source = "str r1, [r2, 100]"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test invalid memory format
        source = "ldr r1, r2, 100"
        instructions, errors = self.assembler.assemble(source)
        self.assertTrue(len(errors) > 0)
    
    def test_control_instructions(self):
        """Test control instruction parsing."""
        # Test JMP
        source = "jmp r1"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test BEQ
        source = "beq 100"
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 1)
        
        # Test invalid control instruction
        source = "jmp 100"
        instructions, errors = self.assembler.assemble(source)
        self.assertTrue(len(errors) > 0)
    
    def test_labels(self):
        """Test label handling."""
        source = """
        start:
            addi r1, r0, 10
        loop:
            subi r1, r1, 1
            beq loop
        """
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 3)
    
    def test_comments(self):
        """Test comment handling."""
        source = """
        # This is a comment
        addi r1, r0, 10    # Load 10 into r1
        # Another comment
        addi r2, r0, 20    # Load 20 into r2
        """
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 2)
    
    def test_immediate_formats(self):
        """Test different immediate value formats."""
        source = """
        addi r1, r0, 10     # Decimal
        addi r2, r0, 0xA    # Hexadecimal
        addi r3, r0, 0b1010 # Binary
        """
        instructions, errors = self.assembler.assemble(source)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(instructions), 3)

if __name__ == '__main__':
    unittest.main() 