import tkinter as tk
from tkinter import ttk
from memory import MemorySystem

class MemoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Simulator")
        
        # Create memory instance
        self.memory = MemorySystem(memory_size=4096, cache_enabled=True, pipeline_enabled=True)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control panel
        self.create_control_panel()
        
        # Memory view
        self.create_memory_view()
        
        # Cache views
        self.create_cache_views()
        
        # Stats view
        self.create_stats_view()
        
    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Address input
        ttk.Label(control_frame, text="Address:").grid(row=0, column=0, padx=5)
        self.addr_var = tk.StringVar(value="0")
        addr_entry = ttk.Entry(control_frame, textvariable=self.addr_var, width=10)
        addr_entry.grid(row=0, column=1, padx=5)
        
        # Value input
        ttk.Label(control_frame, text="Value:").grid(row=0, column=2, padx=5)
        self.value_var = tk.StringVar(value="0")
        value_entry = ttk.Entry(control_frame, textvariable=self.value_var, width=10)
        value_entry.grid(row=0, column=3, padx=5)
        
        # Format selection
        ttk.Label(control_frame, text="Format:").grid(row=0, column=4, padx=5)
        self.format_var = tk.StringVar(value="hex")
        format_combo = ttk.Combobox(control_frame, textvariable=self.format_var, values=["hex", "decimal", "binary"], width=8)
        format_combo.grid(row=0, column=5, padx=5)
        
        # Buttons
        ttk.Button(control_frame, text="Read", command=self.read_memory).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="Write", command=self.write_memory).grid(row=0, column=7, padx=5)
        ttk.Button(control_frame, text="Reset", command=self.reset_memory).grid(row=0, column=8, padx=5)
        
        # Cache and pipeline controls
        cache_frame = ttk.Frame(control_frame)
        cache_frame.grid(row=1, column=0, columnspan=9, pady=5)
        
        self.cache_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cache_frame, text="Enable Cache", variable=self.cache_var, command=self.toggle_cache).grid(row=0, column=0, padx=5)
        
        self.pipeline_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cache_frame, text="Enable Pipeline", variable=self.pipeline_var, command=self.toggle_pipeline).grid(row=0, column=1, padx=5)
        
    def create_memory_view(self):
        memory_frame = ttk.LabelFrame(self.main_frame, text="Memory", padding="5")
        memory_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create memory display
        self.memory_text = tk.Text(memory_frame, width=40, height=10)
        self.memory_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(memory_frame, orient=tk.VERTICAL, command=self.memory_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.memory_text['yscrollcommand'] = scrollbar.set
        
        self.update_memory_view()
        
    def create_cache_views(self):
        cache_frame = ttk.LabelFrame(self.main_frame, text="Cache", padding="5")
        cache_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # L1 Cache view
        l1_frame = ttk.LabelFrame(cache_frame, text="L1 Cache", padding="5")
        l1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.l1_text = tk.Text(l1_frame, width=40, height=5)
        self.l1_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # L2 Cache view
        l2_frame = ttk.LabelFrame(cache_frame, text="L2 Cache", padding="5")
        l2_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.l2_text = tk.Text(l2_frame, width=40, height=5)
        self.l2_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_cache_views()
        
    def create_stats_view(self):
        stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding="5")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.stats_text = tk.Text(stats_frame, width=80, height=4)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.update_stats_view()
        
    def read_memory(self):
        try:
            addr = int(self.addr_var.get())
            value, cycles = self.memory.read(addr)
            self.value_var.set(str(value))
            self.update_all_views()
        except ValueError:
            self.value_var.set("Invalid address")
            
    def write_memory(self):
        try:
            addr = int(self.addr_var.get())
            value = int(self.value_var.get())
            cycles = self.memory.write(addr, value)
            self.update_all_views()
        except ValueError:
            self.value_var.set("Invalid input")
            
    def reset_memory(self):
        self.memory.reset()
        self.update_all_views()
        
    def toggle_cache(self):
        self.memory.cache_enabled = self.cache_var.get()
        self.update_all_views()
        
    def toggle_pipeline(self):
        self.memory.pipeline_enabled = self.pipeline_var.get()
        self.update_all_views()
        
    def format_value(self, value: int) -> str:
        """Format a value according to the selected format."""
        if self.format_var.get() == "hex":
            return f"{value:08x}"
        elif self.format_var.get() == "binary":
            return f"{value:032b}"
        else:  # decimal
            return str(value)
        
    def update_memory_view(self):
        self.memory_text.delete(1.0, tk.END)
        for i in range(0, min(100, len(self.memory.memory)), 4):
            values = self.memory.memory[i:i+4]
            formatted_values = [self.format_value(v) for v in values]
            self.memory_text.insert(tk.END, f"{i:04x}: {' '.join(formatted_values)}\n")
            
    def update_cache_views(self):
        # Update L1 cache view
        self.l1_text.delete(1.0, tk.END)
        for i, line in enumerate(self.memory.L1_cache.lines):
            if line.valid:
                formatted_data = [self.format_value(v) for v in line.data]
                self.l1_text.insert(tk.END, f"Line {i}: Tag={line.tag}, Data={' '.join(formatted_data)}\n")
            else:
                self.l1_text.insert(tk.END, f"Line {i}: Invalid\n")
        
        # Update L2 cache view
        self.l2_text.delete(1.0, tk.END)
        for i, line in enumerate(self.memory.L2_cache.lines):
            if line.valid:
                formatted_data = [self.format_value(v) for v in line.data]
                self.l2_text.insert(tk.END, f"Line {i}: Tag={line.tag}, Data={' '.join(formatted_data)}\n")
            else:
                self.l2_text.insert(tk.END, f"Line {i}: Invalid\n")
                
    def update_stats_view(self):
        stats = self.memory.get_stats()
        self.stats_text.delete(1.0, tk.END)
        
        # L1 Cache stats
        l1_stats = stats["L1"]
        self.stats_text.insert(tk.END, f"L1 Cache: Hits={l1_stats['hits']}, Misses={l1_stats['misses']}, Hit Rate={l1_stats['hit_rate']:.2f}% | ")
        
        # L2 Cache stats
        l2_stats = stats["L2"]
        self.stats_text.insert(tk.END, f"L2 Cache: Hits={l2_stats['hits']}, Misses={l2_stats['misses']}, Hit Rate={l2_stats['hit_rate']:.2f}% | ")
        
        # Total cycles
        self.stats_text.insert(tk.END, f"Total Cycles: {stats['cycles']}")
        
    def update_all_views(self):
        self.update_memory_view()
        self.update_cache_views()
        self.update_stats_view()

if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryGUI(root)
    root.mainloop() 