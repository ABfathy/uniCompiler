from lexer.lexer import lexical_walk
from syntax.syntax import build_syntax_tree
from semantic.semantic import semantic_analysis
from icg.icg import generate_intermediate_code
from utils.tree_utils import print_tree, convert_tree_to_display


def main():

    while True:
        try:
            equation = input("-> ").strip()
            
            if not equation:
                continue
            
            tokens, id_map = lexical_walk(equation)
            tree = build_syntax_tree(tokens)
            display_tree = convert_tree_to_display(tree, id_map)
            

            print("\nSyntax Tree:")
            print_tree(display_tree)
            print()
            
            semantic_tree = semantic_analysis(tree)
            semantic_display_tree = convert_tree_to_display(semantic_tree, id_map)
        
            print("Semantic Tree:")
            print_tree(semantic_display_tree)
            print()

            icg_instructions = generate_intermediate_code(semantic_tree, id_map)
            print("Intermediate Code:")
            for instr in icg_instructions:
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
