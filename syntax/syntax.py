from lexer.lexer import Token

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"Node({self.value}, {self.left}, {self.right})"

def build_syntax_tree(tokens):
    if not tokens:
        raise ValueError("Empty token list")
    

    nodes = []
    for t in tokens:
        if t.type in ("IDENTIFIER", "INT", "FLOAT"):
            nodes.append(Node(t.value))
        else:
            nodes.append(t.value)  

    def get_value(item):
        if isinstance(item, Node):
            return None  
        return item

    def parse_expr(expr_list):
        if not expr_list:
            raise ValueError("Empty expression")
        
        expr_list = expr_list.copy()  


        i = 0
        while i < len(expr_list):
            if get_value(expr_list[i]) == "(":
                depth = 1
                j = i + 1
                while j < len(expr_list) and depth > 0:
                    val = get_value(expr_list[j])
                    if val == "(":
                        depth += 1
                    elif val == ")":
                        depth -= 1
                    j += 1
                if depth != 0:
                    raise ValueError("Unmatched parentheses")

                sub_tree = parse_expr(expr_list[i + 1:j - 1])
                expr_list[i:j] = [sub_tree]
            else:
                i += 1


        i = 1
        while i < len(expr_list):
            if i < len(expr_list) and get_value(expr_list[i]) in ("*", "/"):
                if i == 0 or i >= len(expr_list) - 1:
                    raise ValueError(f"Invalid expression: operator at position {i}")
                left = expr_list[i - 1]
                right = expr_list[i + 1]
                expr_list[i - 1:i + 2] = [Node(expr_list[i], left, right)]
            else:
                i += 1


        i = 1
        while i < len(expr_list):
            if i < len(expr_list) and get_value(expr_list[i]) in ("+", "-"):
                if i == 0 or i >= len(expr_list) - 1:
                    raise ValueError(f"Invalid expression: operator at position {i}")
                left = expr_list[i - 1]
                right = expr_list[i + 1]
                expr_list[i - 1:i + 2] = [Node(expr_list[i], left, right)]
            else:
                i += 1

        if len(expr_list) != 1:
            raise ValueError("Invalid expression structure")
        
        return expr_list[0]


    if len(nodes) >= 2:
        if get_value(nodes[1]) != "=":
            raise SyntaxError("Expected '=' as the second token")


    eq_index = None
    for i, n in enumerate(nodes):
        if get_value(n) == "=":
            eq_index = i
            break

    if eq_index is not None:
        if eq_index == 0 or eq_index >= len(nodes) - 1:
            raise ValueError("Invalid assignment expression")
        left = nodes[eq_index - 1]
        right = parse_expr(nodes[eq_index + 1:])
        return Node("=", left, right)
    else:
        return parse_expr(nodes)
