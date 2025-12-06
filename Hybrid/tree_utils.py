from syntax import Node

def print_tree(node, prefix="", is_left=True):
    """Print tree in a visual format."""
    if node is None:
        return
    
    connector = "├── " if is_left else "└── "
    print(prefix + connector + str(node.value))
    
    new_prefix = prefix + ("│   " if is_left else "    ")
    
    if node.left or node.right:
        if node.left:
            print_tree(node.left, new_prefix, True)
        if node.right:
            print_tree(node.right, new_prefix, False)


def convert_tree_to_display(node, id_map):
    """Convert tree to use V1, V2 notation for display."""
    if node is None:
        return None
    
    new_value = node.value
    
    # Convert identifier to V-notation
    if node.value in id_map:
        new_value = id_map[node.value]
    
    new_node = Node(new_value)
    new_node.left = convert_tree_to_display(node.left, id_map)
    new_node.right = convert_tree_to_display(node.right, id_map)
    
    return new_node
