from syntax.syntax import Node

def print_tree(node, prefix="", is_left=None):
    if node is None:
        return
    

    if is_left is None:  
        print(f"{node.value}")
    else:
        connector = "├── " if is_left else "└── "
        print(f"{prefix}{connector}{node.value}")
    

    if is_left is None:  
        new_prefix = ""
    else:
        extension = "│   " if is_left else "    "
        new_prefix = prefix + extension
    
    if node.left is not None or node.right is not None:
        if node.left is not None:
            print_tree(node.left, new_prefix, True)
        else:
            print(f"{new_prefix}├── None")
        
        if node.right is not None:
            print_tree(node.right, new_prefix, False)
        else:
            print(f"{new_prefix}└── None")


def convert_tree_to_display(node, id_map):
    if node is None:
        return None
    
    if node.value in id_map:
        display_value = id_map[node.value]
    else:
        display_value = node.value
    
    new_node = Node(display_value)
    new_node.left = convert_tree_to_display(node.left, id_map)
    new_node.right = convert_tree_to_display(node.right, id_map)
    
    return new_node