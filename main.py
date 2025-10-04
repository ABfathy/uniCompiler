import string


def lexical_walk(equation: str) -> str:
    i: int = 0
    n: int = len(equation)
    id_counter: int = 1
    result_tokens: list[str] = []
    
    while i < n:
        ch: str = equation[i]
        
        if ch.isspace():
            i += 1
            continue
        
        elif ch == '.' and i + 1 < n and equation[i + 1].isdigit():
            num: str = "0."
            i += 1
            while i < n and equation[i].isdigit():
                num += equation[i]
                i += 1
            result_tokens.append(num)

        elif ch.isdigit():
            num: str = ch
            i += 1
            has_dot: bool = False
            while i < n and (equation[i].isdigit() or (equation[i] == '.' and not has_dot)):
                if equation[i] == '.':
                    has_dot = True
                num += equation[i]
                i += 1
            
            if num.endswith('.'):
                num += '0'
                
            result_tokens.append(num)
        
        elif ch in string.ascii_letters or ch == '_':
            id: str = ch
            i += 1
            while i < n and (equation[i] in string.ascii_letters or equation[i].isdigit() or equation[i] == '_'):
                id += equation[i]
                i += 1
            
            if id.lower() == "pi":
                result_tokens.append("3.14")
                continue
            
            result_tokens.append(f"ID{id_counter}")
            id_counter += 1
        
        elif ch in "+-*/=()":
            result_tokens.append(ch)
            i += 1
               
        else:
            raise ValueError(f"Invalid character '{ch}' at position {i}")
    
    return " ".join(result_tokens)


def main() -> None:
    while True:
        try:
            line: str = input("-> ")           
            tokens: str = lexical_walk(line)
            print("Tokens:", tokens)
            print()
             
        except ValueError as e:
            print(f"Error: {e}\n")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()