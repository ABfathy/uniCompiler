"""
Hybrid Compiler - Command Line Interface
Supports direct execution with V-notation and IS syntax.
"""

from lexer import lexical_walk
from syntax import build_syntax_tree
from semantic import semantic_analysis
from executor import direct_execute
from tree_utils import print_tree, convert_tree_to_display


def main():
   
    while True:
        try:
            equation = input("\n-> ").strip()
            
            if not equation:
                continue
            
            if equation.lower() in ('exit', 'quit', 'q'):
                print("Exiting...")
                break
            
            # Lexical Analysis
            tokens, id_map = lexical_walk(equation)
            
            # Get types and values for RHS identifiers
            id_types = {}
            id_values = {}
            
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

                if var_name not in id_types:
                    while True:
                        type_input = input(f"Enter type for {var_name} ({id_map[var_name]}) (int/float): ").strip().lower()
                        if type_input in ('int', 'float'):
                            id_types[var_name] = type_input.upper()
                            break
                        print("Invalid type. Please enter 'int' or 'float'.")
                    
                    while True:
                        value_input = input(f"Enter value for {var_name} ({id_map[var_name]}): ").strip()
                        try:
                            if id_types[var_name] == 'INT':
                                id_values[var_name] = int(value_input)
                            else:
                                id_values[var_name] = float(value_input)
                            break
                        except ValueError:
                            print(f"Invalid {id_types[var_name].lower()} value.")

            # Syntax Analysis
            tree = build_syntax_tree(tokens)
            display_tree = convert_tree_to_display(tree, id_map)
            
            print("\n--- Syntax Tree ---")
            print_tree(display_tree)
            
            # Semantic Analysis
            semantic_tree = semantic_analysis(tree, id_types)
            semantic_display_tree = convert_tree_to_display(semantic_tree, id_map)
            
            print("\n--- Semantic Tree ---")
            print_tree(semantic_display_tree)
            
            # Direct Execution
            result, steps, value_tree, result_var = direct_execute(tree, id_map, id_values)
            
            print("\n--- Direct Execution ---")
            print_tree(value_tree)
            
            print("\n--- Execution Result ---")
            for step in steps:
                print(f"  {step}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
