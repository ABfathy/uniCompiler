import string

def read_number(equation: str, start: int) -> tuple[str, int]:
    i = start
    n = len(equation)
    num = ""
    has_dot = False

    while i < n and (equation[i].isdigit() or equation[i] == '.'):
        if equation[i-1].isalpha():
                    raise ValueError(f"Invalid token '{equation[i-1]}' at position {i-1}")
                
        if equation[i] == '.':
            if has_dot:
                raise ValueError(f"Invalid token '.' at position {i}")
            has_dot = True
        num += equation[i]
        i += 1

    if num.startswith('.'):
        num = '0' + num
    if num.endswith('.'):
        num += '0'

    return num, i


def lexical_walk(equation: str) -> str:
    i = 0
    n = len(equation)
    id_counter = 1
    result_tokens: list[str] = []
    
    while i < n:
        ch = equation[i]

        if ch.isspace():
            i += 1
            continue    

        elif ch.isdigit() or (ch == '.' and i + 1 < n and equation[i + 1].isdigit()):
            num, i = read_number(equation, i)
            if i < n and (equation[i].isalpha() or equation[i] == '_'):
                raise ValueError(f"Invalid token '{equation[i]}' at position {i}")
            result_tokens.append(num)

        elif ch in string.ascii_letters or ch == '_':
            id = ch
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
            raise ValueError(f"Invalid token '{ch}' at position {i}")
    
    return " ".join(result_tokens)


def main() -> None:
    while True:
        try:
            line = input("-> ")
            tokens = lexical_walk(line)
            print("Tokens:", tokens)
            print()
        except ValueError as e:
            print(f"Error: {e}\n")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()