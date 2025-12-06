from syntax.syntax import Node


def has_float(node, id_types):

    if node is None:
        return False
    
    if id_types and node.value in id_types:
        if id_types[node.value] == 'FLOAT':
            return True
    
    if node.value not in ('+', '-', '*', '/', '='):
        try:
            val = float(node.value)
            if '.' in str(node.value) or isinstance(node.value, float):
                return True
        except (ValueError, TypeError):
            pass  
    
    return has_float(node.left, id_types) or has_float(node.right, id_types)


def is_int_value(value):
    try:
        val_str = str(value)
        if '.' not in val_str:
            int(value)
            return True
        return False
    except (ValueError, TypeError):
        return False


def add_type_conversions(node, needs_conversion, id_types):
    if node is None:
        return None
    
    node.left = add_type_conversions(node.left, needs_conversion, id_types)
    node.right = add_type_conversions(node.right, needs_conversion, id_types)
    
    if needs_conversion and node.value not in ('+', '-', '*', '/', '='):
        is_int_id = node.value in id_types and id_types[node.value] == 'INT'
        if is_int_value(node.value) or is_int_id:
            
            if is_int_id:
                val = node.value
            else:
                val = str(float(node.value))
            
            result_node = Node(val)
            result_node.left = Node("int_to_float")
            result_node.left.left = Node(node.value)
            return result_node
    
    return node


def semantic_analysis(tree, id_types):
       
    needs_conversion = has_float(tree, id_types)    
    return add_type_conversions(tree, needs_conversion, id_types)