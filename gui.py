import pygame
import pygame.font
import time
import tkinter as tk
from tkinter import filedialog
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from memory import MemorySystem
from pipeline import Pipeline, PipelineStage, HazardType
from registers import RegisterFile
from isa import Instruction
from assembler import assemble_file

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
LIGHT_GRAY = (230, 230, 230)
RED = (200, 60, 60)
GREEN = (60, 180, 60)
BLUE = (60, 60, 200)
YELLOW = (220, 220, 60)
BG_COLOR = (245, 245, 245)  # Light background

# Pipeline stage colors
PIPELINE_COLORS = {
    PipelineStage.FETCH: (255, 200, 200),    # Light red
    PipelineStage.DECODE: (200, 255, 200),   # Light green
    PipelineStage.EXECUTE: (200, 200, 255),  # Light blue
    PipelineStage.MEMORY: (255, 255, 200),   # Light yellow
    PipelineStage.WRITEBACK: (255, 200, 255) # Light purple
}

@dataclass
class GUISettings:
    """GUI settings and dimensions"""
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FONT_SIZE = 14
    PADDING = 10
    REGISTER_WIDTH = 200
    MEMORY_WIDTH = 300
    CACHE_WIDTH = 300
    PIPELINE_HEIGHT = 150
    STATS_SPACING = 150  # Space between stats items
    STATS_HEIGHT = 60    # Total height for stats section
    HEADER_HEIGHT = 30   # Height for section headers

class SimulatorGUI:
    def __init__(self, memory: MemorySystem, pipeline: Pipeline, registers: RegisterFile):
        """Initialize the GUI."""
        try:
            pygame.init()
            pygame.font.init()
            
            self.settings = GUISettings()
            self.screen = pygame.display.set_mode((self.settings.WINDOW_WIDTH, self.settings.WINDOW_HEIGHT))
            pygame.display.set_caption("SlitherRISC Simulator")
            
            self.font = pygame.font.SysFont('Courier New', self.settings.FONT_SIZE)
            self.memory = memory
            self.pipeline = pipeline
            self.registers = registers
            
            # Control buttons
            self.buttons = {
                'step': pygame.Rect(10, 10, 100, 30),
                'run': pygame.Rect(120, 10, 100, 30),
                'reset': pygame.Rect(230, 10, 100, 30),
                'cache_toggle': pygame.Rect(340, 10, 150, 30),
                'pipeline_toggle': pygame.Rect(500, 10, 150, 30),
                'load': pygame.Rect(660, 10, 100, 30),
                'save': pygame.Rect(770, 10, 100, 30),
                'run_to_breakpoint': pygame.Rect(880, 10, 150, 30)
            }
            
            self.running = False
            self.cache_enabled = True
            self.pipeline_enabled = True
            self.breakpoints: Set[int] = set()  # Set of PC values for breakpoints
            self.memory_format = 'hex'  # Current memory display format
            self.memory_offset = 0  # Current memory view offset
            
            # Initialize tkinter for file dialogs
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the main window
        except Exception as e:
            print(f"Error initializing GUI: {str(e)}")
            raise
        
    def draw_text(self, text: str, pos: Tuple[int, int], color: Tuple[int, int, int] = WHITE, bold: bool = False, size: int = None) -> None:
        """Draw text on the screen with optional bold and size."""
        font = self.font
        if size or bold:
            font = pygame.font.SysFont('Courier New', size or self.settings.FONT_SIZE, bold=bold)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, pos)
    
    def draw_buttons(self) -> None:
        """Draw control buttons at the top."""
        bx = self.settings.PADDING
        by = 10
        for name, rect in self.buttons.items():
            rect.x = bx
            rect.y = by
            pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
            pygame.draw.rect(self.screen, GRAY, rect, 1)
            if name == 'cache_toggle':
                text = f"Cache: {'On' if self.cache_enabled else 'Off'}"
            elif name == 'pipeline_toggle':
                text = f"Pipeline: {'On' if self.pipeline_enabled else 'Off'}"
            else:
                text = name.capitalize()
            text_surface = self.font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
            bx += rect.width + 10

    def draw_stats(self) -> None:
        """Draw statistics just below the buttons."""
        y = 50
        x = self.settings.PADDING
        
        # First row of stats
        self.draw_text(f"Cycles: {self.pipeline.cycles}", (x, y), GREEN, bold=True)
        x += self.settings.STATS_SPACING
        self.draw_text(f"Instructions: {self.pipeline.instructions}", (x, y), GREEN, bold=True)
        x += self.settings.STATS_SPACING
        self.draw_text(f"CPI: {self.pipeline.cycles/max(1, self.pipeline.instructions):.2f}", (x, y), BLACK)
        x += self.settings.STATS_SPACING
        self.draw_text(f"Stalls: {self.pipeline.stall_count}", (x, y), BLACK)
        x += self.settings.STATS_SPACING
        self.draw_text(f"Flushes: {self.pipeline.flush_count}", (x, y), BLACK)
        
        # Second row of stats
        y += 25
        x = self.settings.PADDING
        l1_stats = self.memory.L1_cache.get_stats()
        l2_stats = self.memory.L2_cache.get_stats()
        self.draw_text(f"L1 Hits: {l1_stats['hits']} Misses: {l1_stats['misses']} Hit Rate: {l1_stats['hit_rate']:.1f}%", (x, y), BLACK)
        x += self.settings.STATS_SPACING * 2
        self.draw_text(f"L2 Hits: {l2_stats['hits']} Misses: {l2_stats['misses']} Hit Rate: {l2_stats['hit_rate']:.1f}%", (x, y), BLACK)

    def draw_register_file(self) -> None:
        """Draw the register file section in two columns."""
        x, y = self.settings.PADDING, 90 + self.settings.STATS_HEIGHT  # Move down to account for stats
        self.draw_text("Register File", (x, y), BLUE, bold=True, size=18)
        y += self.settings.HEADER_HEIGHT
        col_width = 140
        for i in range(16):
            reg_value1 = self.registers.get(i)
            reg_value2 = self.registers.get(i+16)
            reg_name1 = f"R{i}" if i < 29 else ("STAT" if i == 29 else ("LR" if i == 30 else "XZR"))
            reg_name2 = f"R{i+16}" if i+16 < 29 else ("STAT" if i+16 == 29 else ("LR" if i+16 == 30 else "XZR"))
            text1 = f"{reg_name1}: 0x{reg_value1:08x}"
            text2 = f"{reg_name2}: 0x{reg_value2:08x}"
            self.draw_text(text1, (x, y), BLACK)
            self.draw_text(text2, (x + col_width, y), BLACK)
            y += 22

    def draw_pipeline(self) -> None:
        """Draw the pipeline stages horizontally, not overlapping memory."""
        x, y = 340, 110 + self.settings.STATS_HEIGHT  # Move down to account for stats
        self.draw_text("Pipeline", (x, y - 30), BLUE, bold=True, size=18)
        stage_width = 120
        stage_height = 40
        spacing = 18
        for idx, stage in enumerate(PipelineStage):
            stage_rect = pygame.Rect(x + idx * (stage_width + spacing), y, stage_width, stage_height)
            pygame.draw.rect(self.screen, PIPELINE_COLORS[stage], stage_rect)
            pygame.draw.rect(self.screen, GRAY, stage_rect, 2)
            instruction = self.pipeline.stages[stage].instruction
            label = stage.name
            instr_text = str(instruction) if instruction else "Empty"
            self.draw_text(label, (stage_rect.x + 5, stage_rect.y + 5), BLACK, bold=True)
            self.draw_text(instr_text, (stage_rect.x + 5, stage_rect.y + 22), BLACK)
            
            # Draw hazard indicators
            if self.pipeline.stages[stage].hazard != HazardType.NONE:
                hazard_text = f"Hazard: {self.pipeline.stages[stage].hazard.name}"
                self.draw_text(hazard_text, (stage_rect.x + 5, stage_rect.y + 40), RED)

    def draw_memory_and_cache(self) -> None:
        """Draw memory and cache side by side below the pipeline."""
        # Memory on the left below pipeline
        mem_x = 340
        mem_y = 200 + self.settings.STATS_HEIGHT  # Move down to account for stats
        self.draw_text("Memory", (mem_x, mem_y), BLUE, bold=True, size=18)
        
        # Memory format selector
        format_rect = pygame.Rect(mem_x + 100, mem_y, 200, 20)
        pygame.draw.rect(self.screen, LIGHT_GRAY, format_rect)
        pygame.draw.rect(self.screen, GRAY, format_rect, 1)
        format_text = f"Format: {self.memory_format}"
        self.draw_text(format_text, (mem_x + 110, mem_y), BLACK)
        
        y = mem_y + 30
        mem_font_size = 13
        for i in range(0, 16):
            addr = self.memory_offset + i * 4
            value = self.memory.memory[addr]
            if self.memory_format == 'hex':
                text = f"0x{addr:04x}: 0x{value:08x}"
            elif self.memory_format == 'decimal':
                text = f"0x{addr:04x}: {value}"
            else:  # binary
                text = f"0x{addr:04x}: {value:032b}"
            self.draw_text(text, (mem_x, y), BLACK, size=mem_font_size)
            y += 18
            
        # Memory navigation buttons
        nav_x = mem_x + 200
        nav_y = mem_y
        up_rect = pygame.Rect(nav_x, nav_y, 30, 20)
        down_rect = pygame.Rect(nav_x + 40, nav_y, 30, 20)
        pygame.draw.rect(self.screen, LIGHT_GRAY, up_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, down_rect)
        self.draw_text("↑", (nav_x + 10, nav_y), BLACK)
        self.draw_text("↓", (nav_x + 50, nav_y), BLACK)
        
        # Cache on the right below pipeline (moved further right)
        cache_x = mem_x + 400  # Increased spacing between memory and cache
        cache_y = mem_y
        self.draw_text("Cache", (cache_x, cache_y), BLUE, bold=True, size=18)
        y = cache_y + 30
        self.draw_text("L1 Cache:", (cache_x, y), YELLOW, bold=True)
        y += 18
        cache_font_size = 12
        for i, line in enumerate(self.memory.L1_cache.lines[:8]):
            text = f"L1[{i}]: " + (f"Tag=0x{line.tag:x}, Data=[{', '.join(f'0x{x:x}' for x in line.data)}]" if line.valid else "Invalid")
            self.draw_text(text, (cache_x, y), BLACK, size=cache_font_size)
            y += 16
        y += 6
        self.draw_text("L2 Cache:", (cache_x, y), YELLOW, bold=True)
        y += 18
        for i, line in enumerate(self.memory.L2_cache.lines[:8]):
            text = f"L2[{i}]: " + (f"Tag=0x{line.tag:x}, Data=[{', '.join(f'0x{x:x}' for x in line.data)}]" if line.valid else "Invalid")
            self.draw_text(text, (cache_x, y), BLACK, size=cache_font_size)
            y += 16

    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if window should close."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check button clicks
                if self.buttons['step'].collidepoint(pos):
                    self.pipeline.step()
                elif self.buttons['run'].collidepoint(pos):
                    self.running = not self.running
                elif self.buttons['reset'].collidepoint(pos):
                    self.pipeline.reset()
                    self.memory.reset()
                    self.registers.reset()
                elif self.buttons['cache_toggle'].collidepoint(pos):
                    self.cache_enabled = not self.cache_enabled
                    self.memory.cache_enabled = self.cache_enabled
                elif self.buttons['pipeline_toggle'].collidepoint(pos):
                    self.pipeline_enabled = not self.pipeline_enabled
                    self.pipeline.enabled = self.pipeline_enabled
                elif self.buttons['load'].collidepoint(pos):
                    self.load_program()
                elif self.buttons['save'].collidepoint(pos):
                    self.save_program()
                elif self.buttons['run_to_breakpoint'].collidepoint(pos):
                    self.run_to_breakpoint()
                
                # Check memory format selector
                format_rect = pygame.Rect(340 + 100, 200, 200, 20)
                if format_rect.collidepoint(pos):
                    self.cycle_memory_format()
                
                # Check memory navigation
                nav_x = 340 + 200
                nav_y = 200
                up_rect = pygame.Rect(nav_x, nav_y, 30, 20)
                down_rect = pygame.Rect(nav_x + 40, nav_y, 30, 20)
                if up_rect.collidepoint(pos):
                    self.memory_offset = max(0, self.memory_offset - 16)
                elif down_rect.collidepoint(pos):
                    self.memory_offset = min(len(self.memory.memory) - 16, self.memory_offset + 16)
                
                # Check for breakpoint setting
                if 340 <= pos[0] <= 640 and 230 <= pos[1] <= 500:  # Memory view area
                    addr = self.memory_offset + ((pos[1] - 230) // 18) * 4
                    if addr in self.breakpoints:
                        self.breakpoints.remove(addr)
                    else:
                        self.breakpoints.add(addr)
        
        return True

    def cycle_memory_format(self) -> None:
        """Cycle through memory display formats."""
        formats = ['hex', 'decimal', 'binary']
        current_idx = formats.index(self.memory_format)
        self.memory_format = formats[(current_idx + 1) % len(formats)]

    def load_program(self) -> None:
        """Load a program from file."""
        try:
            file_path = filedialog.askopenfilename(
                title="Load Program",
                filetypes=[("Assembly files", "*.asm"), ("Binary files", "*.bin"), ("All files", "*.*")]
            )
            if not file_path:  # User cancelled the dialog
                return
                
            if file_path.endswith('.asm'):
                try:
                    program, errors = assemble_file(file_path)
                    if errors:
                        # Show errors in a message box instead of printing
                        error_msg = "Assembly errors:\n" + "\n".join(errors)
                        self.show_error("Assembly Error", error_msg)
                        return
                except Exception as e:
                    self.show_error("Assembly Error", f"Failed to assemble file: {str(e)}")
                    return
            else:
                try:
                    # Load binary file
                    with open(file_path, 'rb') as f:
                        program = list(f.read())
                except Exception as e:
                    self.show_error("File Error", f"Failed to read file: {str(e)}")
                    return
            
            try:
                self.memory.load_program(program)
                self.pipeline.reset()
                self.registers.reset()
            except Exception as e:
                self.show_error("Load Error", f"Failed to load program into memory: {str(e)}")
                return
                
        except Exception as e:
            self.show_error("Error", f"Unexpected error while loading program: {str(e)}")
            return

    def show_error(self, title: str, message: str) -> None:
        """Show an error message in a tkinter message box."""
        try:
            from tkinter import messagebox
            messagebox.showerror(title, message)
        except Exception:
            # Fallback to printing if messagebox fails
            print(f"{title}: {message}")

    def save_program(self) -> None:
        """Save current program to file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Program",
                defaultextension=".bin",
                filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
            )
            if not file_path:  # User cancelled the dialog
                return
                
            try:
                with open(file_path, 'wb') as f:
                    f.write(bytes(self.memory.memory))
            except Exception as e:
                self.show_error("Save Error", f"Failed to save program: {str(e)}")
                
        except Exception as e:
            self.show_error("Error", f"Unexpected error while saving program: {str(e)}")

    def run_to_breakpoint(self) -> None:
        """Run until a breakpoint is hit."""
        self.running = True
        while self.running:
            if self.pipeline.pc in self.breakpoints:
                self.running = False
                break
            self.pipeline.step()
            time.sleep(0.1)  # Add a small delay for visualization

    def update(self) -> None:
        """Update simulator state."""
        if self.running:
            if self.pipeline.pc in self.breakpoints:
                self.running = False
            else:
                self.pipeline.step()
                time.sleep(0.5)  # Add a 500ms delay between instructions

    def draw(self) -> None:
        """Draw the entire GUI."""
        self.screen.fill(BG_COLOR)
        self.draw_buttons()
        self.draw_stats()
        self.draw_register_file()
        self.draw_pipeline()
        self.draw_memory_and_cache()
        pygame.display.flip()

    def run(self) -> None:
        """Run the GUI main loop."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
        
        pygame.quit()
        self.root.destroy()  # Clean up tkinter 