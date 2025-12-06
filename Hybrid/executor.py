from syntax import Node


class DirectExecutor:
    """
    Direct Execution Engine for Hybrid Compiler.
    Evaluates the syntax tree with actual values and produces output.
    """
    
    def __init__(self, id_map, id_values):
        """
        id_map: Maps original variable names to V1, V2, etc.
        id_values: Maps original variable names to their actual values (from user input).
        """
        self.id_map = id_map  # {'x': 'V1', 'y': 'V2'}
        self.id_values = id_values  # {'x': None, 'y': 5}
        self.reverse_id_map = {v: k for k, v in id_map.items()}  # {'V1': 'x', 'V2': 'y'}
        self.execution_steps = []
        self.result = None
        self.result_var = None
    
    def evaluate(self, node):
        """
        Recursively evaluate the syntax tree from bottom to top.
        Returns the computed value.
        """
        if node is None:
            return 0
        
        # Handle int_to_float conversion nodes
        if node.left and isinstance(node.left, Node) and node.left.value == "int_to_float":
            # The actual value is in node.left.left
            inner_val = self.evaluate(node.left.left)
            return float(inner_val)
        
        # Leaf node: number or identifier
        if node.left is None and node.right is None:
            val_str = str(node.value)
            
            # Check if it's a number
            try:
                if '.' in val_str:
                    return float(val_str)
                return int(val_str)
            except ValueError:
                pass
            
            # It's an identifier - look up its value
            # node.value could be original name or V-name
            if node.value in self.id_values:
                return self.id_values[node.value]
            elif node.value in self.reverse_id_map:
                orig_name = self.reverse_id_map[node.value]
                return self.id_values.get(orig_name, 0)
            
            return 0
        
        # Assignment node (IS)
        if node.value == "IS":
            # Left side is the variable being assigned
            var_name = node.left.value if node.left else "unknown"
            
            # Get V-name
            v_name = self.id_map.get(var_name, var_name)
            
            # Evaluate right side
            result = self.evaluate(node.right)
            
            self.result = result
            self.result_var = var_name
            
            # Record the step
            self.execution_steps.append(f"{v_name} IS {result}")
            self.execution_steps.append(f"{var_name} = {result}")
            
            return result
        
        # Binary operation
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)
        
        if node.value == '+':
            result = left_val + right_val
        elif node.value == '-':
            result = left_val - right_val
        elif node.value == '*':
            result = left_val * right_val
        elif node.value == '/':
            if right_val == 0:
                raise ValueError("Division by zero")
            result = left_val / right_val
        else:
            result = 0
        
        return result
    
    def execute(self, tree):
        """Execute the tree and return results."""
        self.execution_steps = []
        self.result = self.evaluate(tree)
        return self.result, self.execution_steps
    
    def evaluate_subtree(self, node):
        """Evaluate a subtree and return the numeric result."""
        if node is None:
            return 0
        
        # Handle int_to_float nodes
        if node.left and isinstance(node.left, Node) and node.left.value == "int_to_float":
            inner_val = self.evaluate_subtree(node.left.left)
            return float(inner_val)
        
        # Leaf node
        if node.left is None and node.right is None:
            val_str = str(node.value)
            try:
                if '.' in val_str:
                    return float(val_str)
                return int(val_str)
            except ValueError:
                pass
            
            if node.value in self.id_values:
                return self.id_values[node.value]
            elif node.value in self.reverse_id_map:
                orig_name = self.reverse_id_map[node.value]
                return self.id_values.get(orig_name, 0)
            return 0
        
        # Binary operation
        left_val = self.evaluate_subtree(node.left)
        right_val = self.evaluate_subtree(node.right)
        
        if node.value == '+':
            return left_val + right_val
        elif node.value == '-':
            return left_val - right_val
        elif node.value == '*':
            return left_val * right_val
        elif node.value == '/':
            if right_val == 0:
                return 0
            return left_val / right_val
        
        return 0
    
    def create_value_tree(self, node):
        """
        Create a copy of the tree with actual values substituted for identifiers.
        For LHS variables (no value), use V-notation.
        Operators show their computed result.
        """
        if node is None:
            return None
        
        # Handle int_to_float nodes
        if node.left and isinstance(node.left, Node) and node.left.value == "int_to_float":
            inner_val = self.get_node_value(node.left.left)
            return Node(str(float(inner_val)))
        
        # Assignment node (IS) - special handling for LHS
        if node.value == "IS":
            result = self.evaluate_subtree(node.right)
            new_node = Node(f"IS  ({result})")
            # LHS: use V-notation
            if node.left:
                var_name = node.left.value
                v_name = self.id_map.get(var_name, var_name)
                new_node.left = Node(v_name)
            # RHS: evaluate with actual values
            new_node.right = self.create_value_tree(node.right)
            return new_node
        
        # Leaf node
        if node.left is None and node.right is None:
            val = self.get_node_value(node)
            return Node(str(val))
        
        # Operator node - show result
        if node.value in ['+', '-', '*', '/']:
            result = self.evaluate_subtree(node)
            new_node = Node(f"{node.value}  ({result})")
            new_node.left = self.create_value_tree(node.left)
            new_node.right = self.create_value_tree(node.right)
            return new_node
        
        # Create new node with evaluated children
        new_node = Node(node.value)
        new_node.left = self.create_value_tree(node.left)
        new_node.right = self.create_value_tree(node.right)
        
        return new_node
    
    def get_node_value(self, node):
        """Get the actual value of a node."""
        if node is None:
            return 0
            
        val_str = str(node.value)
        
        # Check if it's a number
        try:
            if '.' in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            pass
        
        # It's an identifier
        if node.value in self.id_values:
            return self.id_values[node.value]
        elif node.value in self.reverse_id_map:
            orig_name = self.reverse_id_map[node.value]
            return self.id_values.get(orig_name, self.id_map.get(node.value, node.value))
        
        # Return V-notation if available, otherwise original value
        return self.id_map.get(node.value, node.value)


def direct_execute(tree, id_map, id_values):
    """
    Execute the syntax tree directly with given values.
    Returns: (result, execution_steps, value_tree)
    """
    executor = DirectExecutor(id_map, id_values)
    result, steps = executor.execute(tree)
    value_tree = executor.create_value_tree(tree)
    return result, steps, value_tree, executor.result_var
