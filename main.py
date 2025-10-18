from lexer.lexer import lexical_walk
from syntax.syntax import build_syntax_tree
from utils.utils import print_tree, convert_tree_to_display


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