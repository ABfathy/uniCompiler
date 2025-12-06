from lexer.lexer import lexical_walk
from syntax.syntax import build_syntax_tree
from semantic.semantic import semantic_analysis
from icg.icg import generate_intermediate_code
from optimization.optimizer import optimize_code
from assembly.assembly import generate_assembly
from utils.tree_utils import print_tree, convert_tree_to_display


def main():

    while True:
        id_types = {}
        try:
            equation = input("-> ").strip()
            
            if not equation:
                continue
            
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

                if var_name not in id_types:
                    while True:
                        type_input = input(f"Enter type for {var_name} (int/float): ").strip().lower()
                        if type_input in ('int', 'float'):
                            id_types[var_name] = type_input.upper()
                            break
                        print("Invalid type. Please enter 'int' or 'float'.")

            tree = build_syntax_tree(tokens)
            display_tree = convert_tree_to_display(tree, id_map)
            

            print("\nSyntax Tree:")
            print_tree(display_tree)
            print()
            
            semantic_tree = semantic_analysis(tree, id_types)
            semantic_display_tree = convert_tree_to_display(semantic_tree, id_map)
        
            print("Semantic Tree:")
            print_tree(semantic_display_tree)
            print()

            icg_instructions = generate_intermediate_code(semantic_tree, id_map)
            print("Intermediate Code:")
            for instr in icg_instructions:
                print(instr)
            print()

            optimized_instructions = optimize_code(icg_instructions)
            print("Optimized Code:")
            for instr in optimized_instructions:
                print(instr)
            print()

            assembly_code = generate_assembly(optimized_instructions, id_types)
            print("Assembly Code:")
            for instr in assembly_code:
                print(instr)
            print()
            
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
