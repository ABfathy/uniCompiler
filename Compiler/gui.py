import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math


from lexer.lexer import lexical_walk
from syntax.syntax import build_syntax_tree, Node
from semantic.semantic import semantic_analysis
from icg.icg import generate_intermediate_code
from optimization.optimizer import optimize_code
from assembly.assembly import generate_assembly
from utils.tree_utils import convert_tree_to_display

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UniCompiler GUI")
        self.root.geometry("1000x800")
        
        self.id_types = {}
        
        self.setup_theme()
        self.create_widgets()

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        bg_color = "#2b2b2b"
        fg_color = "#ffffff"
        accent_color = "#007acc"
        secondary_bg = "#3c3f41"
        
        self.root.configure(bg=bg_color)
        
        self.style.configure(".", background=bg_color, foreground=fg_color, fieldbackground=secondary_bg)
        self.style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        self.style.configure("TButton", background=accent_color, foreground=fg_color, borderwidth=0, font=("Segoe UI", 10, "bold"))
        self.style.map("TButton", background=[('active', '#005f9e')])
        self.style.configure("TNotebook", background=bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=secondary_bg, foreground=fg_color, padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[('selected', accent_color)])
        self.style.configure("TFrame", background=bg_color)
        
        # Custom canvas bg
        self.canvas_bg = secondary_bg

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="20")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Enter Equation:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.equation_var = tk.StringVar()
        self.entry = ttk.Entry(top_frame, textvariable=self.equation_var, font=("Consolas", 12), width=50)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.compile())
        
        self.compile_btn = ttk.Button(top_frame, text="Compile", command=self.compile)
        self.compile_btn.pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.token_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.token_frame, text="Lexical Analysis")
        self.token_text = tk.Text(self.token_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.token_text.pack(fill=tk.BOTH, expand=True)
        
        self.token_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#007acc", spacing3=10)
        self.token_text.tag_configure("subheader", font=("Segoe UI", 12, "bold"), foreground="#dcdcdc", spacing1=15, spacing3=5)
        self.token_text.tag_configure("content", font=("Consolas", 11), foreground="#d4d4d4", lmargin1=20, lmargin2=20)
        
        self.syntax_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.syntax_frame, text="Syntax Analysis")
        self.syntax_canvas = tk.Canvas(self.syntax_frame, bg=self.canvas_bg, highlightthickness=0)
        self.syntax_canvas.pack(fill=tk.BOTH, expand=True)
        self.add_scrollbars(self.syntax_frame, self.syntax_canvas)

        self.semantic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.semantic_frame, text="Semantic Analysis")
        self.semantic_canvas = tk.Canvas(self.semantic_frame, bg=self.canvas_bg, highlightthickness=0)
        self.semantic_canvas.pack(fill=tk.BOTH, expand=True)
        self.add_scrollbars(self.semantic_frame, self.semantic_canvas)

        self.icg_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.icg_frame, text="Intermediate Code")
        self.icg_text = tk.Text(self.icg_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.icg_text.pack(fill=tk.BOTH, expand=True)
        
        self.icg_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#007acc", spacing3=10)
        self.icg_text.tag_configure("line_num", foreground="#858585")
        self.icg_text.tag_configure("code", foreground="#d4d4d4")

        self.opt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.opt_frame, text="Optimized Code")
        self.opt_text = tk.Text(self.opt_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.opt_text.pack(fill=tk.BOTH, expand=True)
        
        self.opt_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#007acc", spacing3=10)
        self.opt_text.tag_configure("line_num", foreground="#858585")
        self.opt_text.tag_configure("code", foreground="#d4d4d4")

        self.asm_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.asm_frame, text="Assembly Code")
        self.asm_text = tk.Text(self.asm_frame, bg=self.canvas_bg, fg="white", font=("Consolas", 12), padx=20, pady=20, borderwidth=0)
        self.asm_text.pack(fill=tk.BOTH, expand=True)
        
        self.asm_text.tag_configure("header", font=("Segoe UI", 16, "bold"), foreground="#007acc", spacing3=10)
        self.asm_text.tag_configure("line_num", foreground="#858585")
        self.asm_text.tag_configure("code", foreground="#d4d4d4")

    def add_scrollbars(self, parent, canvas):
        v_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        h_scroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Mousewheel scrolling
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

            self.token_text.delete(1.0, tk.END)
            self.syntax_canvas.delete("all")
            self.semantic_canvas.delete("all")
            self.icg_text.delete(1.0, tk.END)
            self.opt_text.delete(1.0, tk.END)
            self.asm_text.delete(1.0, tk.END)
            
            # Reset scroll regions
            self.syntax_canvas.configure(scrollregion=(0,0,0,0))
            self.semantic_canvas.configure(scrollregion=(0,0,0,0))
            
            # Force UI update
            self.root.update()

            try:
                tokens, id_map = lexical_walk(equation)
                
                for var_name in id_map:
                    # Check if variable is used only on LHS (assignment target)
                    is_lhs = False
                    is_rhs = False
                    
                    for i, t in enumerate(tokens):
                        if t.type == "IDENTIFIER" and t.value == var_name:
                            if i + 1 < len(tokens) and tokens[i+1].type == "ASSIGN":
                                is_lhs = True
                            else:
                                is_rhs = True
                    
                    # If variable is only assigned to and never read, we don't need its type from user
                    if is_lhs and not is_rhs:
                        continue

                    if var_name not in self.id_types:
                        while True:
                            type_input = simpledialog.askstring("Input", f"Enter type for {var_name} (int/float):", parent=self.root)
                            if type_input and type_input.strip().lower() in ('int', 'float'):
                                self.id_types[var_name] = type_input.strip().upper()
                                break
                            elif type_input is None:
                                return
                            else:
                                messagebox.showerror("Error", "Invalid type. Please enter 'int' or 'float'.")

                display_tokens = []
                for t in tokens:
                    if t.type == "IDENTIFIER" and t.value in id_map:
                        display_tokens.append(id_map[t.value])
                    else:
                        display_tokens.append(t.value)
                token_string = " ".join(display_tokens)

                self.token_text.insert(tk.END, "Lexical Analysis Result\n", "header")
                
                self.token_text.insert(tk.END, "Token String\n", "subheader")
                self.token_text.insert(tk.END, f"{token_string}\n", "content")

                self.token_text.insert(tk.END, "Token List\n", "subheader")
                for t in tokens:
                    self.token_text.insert(tk.END, f"• {t}\n", "content")
                
                self.token_text.insert(tk.END, "Symbol Table\n", "subheader")
                for k, v in id_map.items():
                    self.token_text.insert(tk.END, f"• {k} -> {v}\n", "content")

            except Exception as e:
                self.token_text.insert(tk.END, f"Lexical Error:\n{str(e)}")
                self.notebook.select(0)
                return

            try:
                tree = build_syntax_tree(tokens)
                display_tree = convert_tree_to_display(tree, id_map)
                self.draw_tree_on_canvas(self.syntax_canvas, display_tree)
            except Exception as e:
                self.syntax_canvas.create_text(400, 300, text=f"Syntax Error:\n{str(e)}", fill="red", font=("Segoe UI", 14))
                self.notebook.select(1)
                return

            try:
                semantic_tree = semantic_analysis(tree, self.id_types) 
                semantic_display_tree = convert_tree_to_display(semantic_tree, id_map)
                self.draw_tree_on_canvas(self.semantic_canvas, semantic_display_tree)
            except Exception as e:
                self.semantic_canvas.create_text(400, 300, text=f"Semantic Error:\n{str(e)}", fill="red", font=("Segoe UI", 14))
                self.notebook.select(2)
                return

            try:
                icg_instructions = generate_intermediate_code(semantic_tree, id_map)
                
                self.icg_text.insert(tk.END, "Generated Intermediate Code\n", "header")
                
                for i, instr in enumerate(icg_instructions, 1):
                    self.icg_text.insert(tk.END, f"{i:02d}  ", "line_num")
                    self.icg_text.insert(tk.END, f"{instr}\n", "code")

                # Optimization
                optimized_instructions = optimize_code(icg_instructions)
                
                self.opt_text.insert(tk.END, "Optimized Code\n", "header")
                
                for i, instr in enumerate(optimized_instructions, 1):
                    self.opt_text.insert(tk.END, f"{i:02d}  ", "line_num")
                    self.opt_text.insert(tk.END, f"{instr}\n", "code")

                # Assembly Generation
                assembly_code = generate_assembly(optimized_instructions, self.id_types)
                
                self.asm_text.insert(tk.END, "Assembly Code\n", "header")
                
                for i, instr in enumerate(assembly_code, 1):
                    self.asm_text.insert(tk.END, f"{i:02d}  ", "line_num")
                    self.asm_text.insert(tk.END, f"{instr}\n", "code")

            except Exception as e:
                self.icg_text.insert(tk.END, f"ICG/Optimization/Assembly Error:\n{str(e)}")
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
            

        NODE_RADIUS = 25
        H_SPACING = 20
        V_SPACING = 80
        
        
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
                # Leaf
                self.node_x[id(n)] = self.leaf_counter * (NODE_RADIUS * 2 + H_SPACING)
                self.leaf_counter += 1
            else:
                # Parent
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
        
        for n_id, x in self.node_x.items():
          
            pass
            

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
        

        fill_color = "#007acc" 
        if str(node.value) in ['+', '-', '*', '/', '=']:
            fill_color = "#d65d0e" 
        elif str(node.value).startswith('ID'):
            fill_color = "#98971a" 
        elif str(node.value).replace('.','',1).isdigit():
            fill_color = "#b16286" 
            
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="white", width=2)
        canvas.create_text(x, y, text=str(node.value), fill="white", font=("Segoe UI", 10, "bold"))
        
        self.draw_nodes(canvas, node.left, positions, off_x, off_y)
        self.draw_nodes(canvas, node.right, positions, off_x, off_y)

if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()
