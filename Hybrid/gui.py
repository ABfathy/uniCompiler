import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math

from lexer import lexical_walk
from syntax import build_syntax_tree, Node
from semantic import semantic_analysis
from executor import direct_execute
from tree_utils import convert_tree_to_display


class HybridCompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hybrid Compiler GUI")
        self.root.geometry("1000x800")
        
        self.id_types = {}
        self.id_values = {}
        
        self.setup_theme()
        self.create_widgets()

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        bg_color = "#1e3a5f"  # Dark blue for hybrid
        fg_color = "#ffffff"
        accent_color = "#ff6b35"  # Orange accent
        secondary_bg = "#2d4a6f"
        
        self.root.configure(bg=bg_color)
        
        self.style.configure(".", background=bg_color, foreground=fg_color, fieldbackground=secondary_bg)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        self.style.configure("TButton", background=accent_color, foreground=fg_color, borderwidth=0, font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[('active', '#cc5500')])
        self.style.configure("TNotebook", background=bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=secondary_bg, foreground=fg_color, padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[('selected', accent_color)])
        self.style.configure("TFrame", background=bg_color)
        
        self.canvas_bg = secondary_bg

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="20")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Enter Equation:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.equation_var = tk.StringVar()
        self.entry = ttk.Entry(top_frame, textvariable=self.equation_var, font=("Consolas", 12), width=50)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.compile())
        
        self.compile_btn = ttk.Button(top_frame, text="Execute", command=self.compile)
        self.compile_btn.pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Lexical Analysis Tab
        self.token_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.token_frame, text="Lexical Analysis")
        self.token_text = tk.Text(self.token_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.token_text.pack(fill=tk.BOTH, expand=True)
        
        self.token_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#ff6b35", spacing3=10)
        self.token_text.tag_configure("subheader", font=("Segoe UI", 12, "bold"), foreground="#dcdcdc", spacing1=15, spacing3=5)
        self.token_text.tag_configure("content", font=("Consolas", 11), foreground="#d4d4d4", lmargin1=20, lmargin2=20)
        
        # Syntax Analysis Tab
        self.syntax_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.syntax_frame, text="Syntax Analysis")
        self.syntax_canvas = tk.Canvas(self.syntax_frame, bg=self.canvas_bg, highlightthickness=0)
        self.syntax_canvas.pack(fill=tk.BOTH, expand=True)
        self.add_scrollbars(self.syntax_frame, self.syntax_canvas)

        # Semantic Analysis Tab
        self.semantic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.semantic_frame, text="Semantic Analysis")
        self.semantic_canvas = tk.Canvas(self.semantic_frame, bg=self.canvas_bg, highlightthickness=0)
        self.semantic_canvas.pack(fill=tk.BOTH, expand=True)
        self.add_scrollbars(self.semantic_frame, self.semantic_canvas)

        # Direct Execution Tab
        self.exec_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exec_frame, text="Direct Execution")
        
        # Split into tree and output
        self.exec_paned = ttk.PanedWindow(self.exec_frame, orient=tk.HORIZONTAL)
        self.exec_paned.pack(fill=tk.BOTH, expand=True)
        
        self.exec_canvas_frame = ttk.Frame(self.exec_paned)
        self.exec_paned.add(self.exec_canvas_frame, weight=2)
        self.exec_canvas = tk.Canvas(self.exec_canvas_frame, bg=self.canvas_bg, highlightthickness=0)
        self.exec_canvas.pack(fill=tk.BOTH, expand=True)
        self.add_scrollbars(self.exec_canvas_frame, self.exec_canvas)
        
        self.exec_output_frame = ttk.Frame(self.exec_paned)
        self.exec_paned.add(self.exec_output_frame, weight=1)
        self.exec_text = tk.Text(self.exec_output_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.exec_text.pack(fill=tk.BOTH, expand=True)
        
        self.exec_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#ff6b35", spacing3=10)
        self.exec_text.tag_configure("result", font=("Consolas", 14, "bold"), foreground="#4ade80", spacing1=10)
        self.exec_text.tag_configure("step", font=("Consolas", 11), foreground="#d4d4d4", lmargin1=20)

    def add_scrollbars(self, parent, canvas):
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        h_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(int(-1*(e.delta/120)), "units"))

    def compile(self):
        equation = self.equation_var.get().strip()
        if not equation:
            return
            
        self.compile_btn.state(['disabled'])
        self.root.config(cursor="watch")
        self.root.update()
            
        try:
            self.id_types = {}
            self.id_values = {}

            self.token_text.delete(1.0, tk.END)
            self.syntax_canvas.delete("all")
            self.semantic_canvas.delete("all")
            self.exec_canvas.delete("all")
            self.exec_text.delete(1.0, tk.END)
            
            self.syntax_canvas.configure(scrollregion=(0,0,0,0))
            self.semantic_canvas.configure(scrollregion=(0,0,0,0))
            self.exec_canvas.configure(scrollregion=(0,0,0,0))
            
            self.root.update()

            # Lexical Analysis
            try:
                tokens, id_map = lexical_walk(equation)
                
                # Ask for types and values of RHS identifiers
                for var_name in id_map:
                    is_lhs = False
                    is_rhs = False
                    
                    for i, t in enumerate(tokens):
                        if t.type == "IDENTIFIER" and t.value == var_name:
                            if i + 1 < len(tokens) and tokens[i+1].type == "ASSIGN":
                                is_lhs = True
                            else:
                                is_rhs = True
                    
                    if is_lhs and not is_rhs:
                        continue

                    if var_name not in self.id_types:
                        while True:
                            type_input = simpledialog.askstring("Variable Type", 
                                f"Enter type for {var_name} ({id_map[var_name]}) (int/float):", 
                                parent=self.root)
                            if type_input and type_input.strip().lower() in ('int', 'float'):
                                self.id_types[var_name] = type_input.strip().upper()
                                break
                            elif type_input is None:
                                return
                            else:
                                messagebox.showerror("Error", "Invalid type. Please enter 'int' or 'float'.")
                        
                        # Ask for value
                        while True:
                            value_input = simpledialog.askstring("Variable Value", 
                                f"Enter value for {var_name} ({id_map[var_name]}):", 
                                parent=self.root)
                            if value_input is None:
                                return
                            try:
                                if self.id_types[var_name] == 'INT':
                                    self.id_values[var_name] = int(value_input)
                                else:
                                    self.id_values[var_name] = float(value_input)
                                break
                            except ValueError:
                                messagebox.showerror("Error", f"Invalid {self.id_types[var_name].lower()} value.")

                # Display tokens
                display_tokens = []
                for t in tokens:
                    if t.type == "IDENTIFIER" and t.value in id_map:
                        display_tokens.append(id_map[t.value])
                    elif t.type == "ASSIGN":
                        display_tokens.append("IS")
                    else:
                        display_tokens.append(t.value)
                token_string = " ".join(display_tokens)

                self.token_text.insert(tk.END, "Hybrid Lexical Analysis\n", "header")
                
                self.token_text.insert(tk.END, "Token String (Hybrid Format)\n", "subheader")
                self.token_text.insert(tk.END, f"{token_string}\n", "content")

                self.token_text.insert(tk.END, "Token List\n", "subheader")
                for t in tokens:
                    self.token_text.insert(tk.END, f"• {t}\n", "content")
                
                self.token_text.insert(tk.END, "Symbol Table (V-Notation)\n", "subheader")
                for k, v in id_map.items():
                    val_str = f" = {self.id_values.get(k, 'N/A')}" if k in self.id_values else ""
                    self.token_text.insert(tk.END, f"• {k} -> {v}{val_str}\n", "content")

            except Exception as e:
                self.token_text.insert(tk.END, f"Lexical Error:\n{str(e)}")
                self.notebook.select(0)
                return

            # Syntax Analysis
            try:
                tree = build_syntax_tree(tokens)
                display_tree = convert_tree_to_display(tree, id_map)
                self.draw_tree_on_canvas(self.syntax_canvas, display_tree)
            except Exception as e:
                self.syntax_canvas.create_text(400, 300, text=f"Syntax Error:\n{str(e)}", fill="red", font=("Segoe UI", 14))
                self.notebook.select(1)
                return

            # Semantic Analysis
            try:
                semantic_tree = semantic_analysis(tree, self.id_types) 
                semantic_display_tree = convert_tree_to_display(semantic_tree, id_map)
                self.draw_tree_on_canvas(self.semantic_canvas, semantic_display_tree)
            except Exception as e:
                self.semantic_canvas.create_text(400, 300, text=f"Semantic Error:\n{str(e)}", fill="red", font=("Segoe UI", 14))
                self.notebook.select(2)
                return

            # Direct Execution
            try:
                result, steps, value_tree, result_var = direct_execute(tree, id_map, self.id_values)
                
                # Draw value tree
                self.draw_tree_on_canvas(self.exec_canvas, value_tree)
                
                # Display execution output
                self.exec_text.insert(tk.END, "Execution Result\n", "header")
                
                for step in steps:
                    self.exec_text.insert(tk.END, f"{step}\n", "result")
                
                self.exec_text.insert(tk.END, "\nInput Values\n", "header")
                for var, val in self.id_values.items():
                    v_name = id_map.get(var, var)
                    self.exec_text.insert(tk.END, f"• {var} ({v_name}) = {val}\n", "step")

            except Exception as e:
                self.exec_text.insert(tk.END, f"Execution Error:\n{str(e)}")
                self.notebook.select(3)
                return
        finally:
            self.compile_btn.state(['!disabled'])
            self.root.config(cursor="")

    def draw_tree_on_canvas(self, canvas, root_node):
        if root_node is None:
            return

        positions = {}
        self.calculate_node_positions(root_node, 0, 0, positions)
        
        if not positions:
            return

        min_x = min(p[0] for p in positions.values())
        max_x = max(p[0] for p in positions.values())
        max_y = max(p[1] for p in positions.values())
        
        tree_width = max_x - min_x

        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()

        if canvas_width < 100:
            canvas_width = 960 

        if canvas_width > tree_width + 100:
            offset_x = (canvas_width - tree_width) / 2 - min_x
        else:
            offset_x = 50 - min_x
            
        offset_y = 50
        
        scroll_width = max(canvas_width, tree_width + 100)
        scroll_height = max(canvas.winfo_height(), max_y + 100)
        
        canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

        self.draw_edges(canvas, root_node, positions, offset_x, offset_y)
        self.draw_nodes(canvas, root_node, positions, offset_x, offset_y)

    def calculate_node_positions(self, node, depth, x_idx, positions):
        if node is None:
            return 0

        NODE_RADIUS = 40
        H_SPACING = 30
        V_SPACING = 100
        
        self.leaf_counter = 0
        self.node_depths = {}
        self.node_x = {}
        
        def assign_coordinates(n, d):
            if n is None:
                return
            
            assign_coordinates(n.left, d + 1)
            assign_coordinates(n.right, d + 1)
            
            self.node_depths[id(n)] = d
            
            if n.left is None and n.right is None:
                self.node_x[id(n)] = self.leaf_counter * (NODE_RADIUS * 2 + H_SPACING)
                self.leaf_counter += 1
            else:
                children_x = []
                if n.left:
                    children_x.append(self.node_x[id(n.left)])
                if n.right:
                    children_x.append(self.node_x[id(n.right)])
                
                if children_x:
                    self.node_x[id(n)] = sum(children_x) / len(children_x)
                else:
                    self.node_x[id(n)] = self.leaf_counter * (NODE_RADIUS * 2 + H_SPACING)
                    self.leaf_counter += 1
                    
        assign_coordinates(node, 0)
        
        def populate(n):
            if n is None:
                return
            positions[id(n)] = (self.node_x[id(n)], self.node_depths[id(n)] * V_SPACING)
            populate(n.left)
            populate(n.right)
            
        populate(node)

    def draw_edges(self, canvas, node, positions, off_x, off_y):
        if node is None:
            return
            
        x, y = positions[id(node)]
        x += off_x
        y += off_y
        
        if node.left:
            lx, ly = positions[id(node.left)]
            lx += off_x
            ly += off_y
            canvas.create_line(x, y, lx, ly, fill="#888888", width=2)
            self.draw_edges(canvas, node.left, positions, off_x, off_y)
            
        if node.right:
            rx, ry = positions[id(node.right)]
            rx += off_x
            ry += off_y
            canvas.create_line(x, y, rx, ry, fill="#888888", width=2)
            self.draw_edges(canvas, node.right, positions, off_x, off_y)

    def draw_nodes(self, canvas, node, positions, off_x, off_y):
        if node is None:
            return
            
        x, y = positions[id(node)]
        x += off_x
        y += off_y
        
        r = 20

        fill_color = "#ff6b35"  # Orange for operators
        if str(node.value) in ['+', '-', '*', '/', 'IS']:
            fill_color = "#ff6b35"
        elif str(node.value).startswith('V'):
            fill_color = "#4ade80"  # Green for variables
        elif str(node.value).replace('.','',1).replace('-','',1).isdigit():
            fill_color = "#60a5fa"  # Blue for numbers
            
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="white", width=2)
        canvas.create_text(x, y, text=str(node.value), fill="white", font=("Segoe UI", 10, "bold"))
        
        self.draw_nodes(canvas, node.left, positions, off_x, off_y)
        self.draw_nodes(canvas, node.right, positions, off_x, off_y)


if __name__ == "__main__":
    root = tk.Tk()
    app = HybridCompilerGUI(root)
    root.mainloop()
