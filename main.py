from lexer.lexer import lexical_walk


def main() -> None:
    while True:
        try:
            line = input("-> ").strip()
            if not line:
                continue

            tokens = lexical_walk(line)

            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
            print()

        except ValueError as e:
            print(f"Error: {e}\n")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
