import string
from typing import List, Dict, Tuple

class Token:
    def __init__(self, token_type: str, value: str):
        self.type = token_type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value='{self.value}')"

def read_number(equation: str, start: int) -> tuple[str, int, str]:
    i = start
    n = len(equation)
    num = ""
    has_dot = False

    while i < n and (equation[i].isdigit() or equation[i] == "."):
        if equation[i] == ".":
            if has_dot:
                raise ValueError(f"Invalid token '.' at position {i}")
            has_dot = True
        num += equation[i]
        i += 1

    if num.startswith("."):
        num = "0" + num
    if num.endswith("."):
        num += "0"

    token_type = "FLOAT" if has_dot else "INT"
    return num, i, token_type


def lexical_walk(equation: str) -> Tuple[List[Token], Dict[str, str]]:
    i = 0
    n = len(equation)
    id_counter = 1
    tokens: List[Token] = []
    display_tokens: List[str] = []
    id_map: Dict[str, str] = {}  

    while i < n:
        ch = equation[i]

        if ch.isspace():
            i += 1
            continue

        elif ch.isdigit() or (ch == "." and i + 1 < n and equation[i + 1].isdigit()):
            num, i, token_type = read_number(equation, i)

            if i < n and (equation[i].isalpha() or equation[i] == "_"):
                raise ValueError(f"Invalid token '{equation[i]}' after number '{num}'")
            tokens.append(Token(token_type, num))
            display_tokens.append(num)

        elif ch in string.ascii_letters or ch == "_":
            ident = ch
            i += 1
            while i < n and (equation[i].isalnum() or equation[i] == "_"):
                ident += equation[i]
                i += 1

            if i < n and equation[i] == ".":
                raise ValueError(f"Invalid token: identifier '{ident}' cannot be followed by '.'")

            if ident.lower() == "pi":
                tokens.append(Token("FLOAT", "3.14"))
                display_tokens.append("3.14")
            else:
                tokens.append(Token("IDENTIFIER", ident))
                # Store the ID mapping
                if ident not in id_map:
                    id_map[ident] = f"ID{id_counter}"
                    id_counter += 1
                display_tokens.append(id_map[ident])

        elif ch in "+-*/=()":
            token_type = (
                "ASSIGN" if ch == "=" else
                "LPAREN" if ch == "(" else
                "RPAREN" if ch == ")" else
                "OPERATOR"
            )
            tokens.append(Token(token_type, ch))
            display_tokens.append(ch)
            i += 1

        else:
            raise ValueError(f"Invalid character '{ch}' at position {i}")

    print(f"\nToken String: {' '.join(display_tokens)}")
    return tokens, id_map