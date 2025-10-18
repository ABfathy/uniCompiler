from syntax.syntax import Node


def has_float(node):

    if node is None:
        return False
    
    if node.value not in ('+', '-', '*', '/', '='):
        try:
            val = float(node.value)
            if '.' in str(node.value) or isinstance(node.value, float):
                return True
        except (ValueError, TypeError):
            pass  
    
    return has_float(node.left) or has_float(node.right)


def is_int_value(value):
    try:
        val_str = str(value)
        if '.' not in val_str:
            int(value)
            return True
        return False
    except (ValueError, TypeError):
        return False


def add_type_conversions(node, needs_conversion):
    if node is None:
        return None
    
    node.left = add_type_conversions(node.left, needs_conversion)
    node.right = add_type_conversions(node.right, needs_conversion)
    
    if needs_conversion and node.value not in ('+', '-', '*', '/', '='):
        if is_int_value(node.value):

            float_value = str(float(node.value))
            
            
            result_node = Node(float_value) 
            result_node.left = Node("int_to_float")  
            result_node.left.left = Node(node.value)
            return result_node
    
    return node


def semantic_analysis(tree):
       
    needs_conversion = has_float(tree)    
    return add_type_conversions(tree, needs_conversion)