from syntax.syntax import Node

class IntermediateCodeGenerator:
    def __init__(self, id_map=None):
        self.temp_counter = 1
        self.instructions = []
        self.id_map = id_map if id_map is not None else {}

    def new_temp(self):
        temp = f"temp{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def generate(self, node):
        if node is None:
            return None

       
        if node.left and node.left.value == "int_to_float":
            operand = self.generate(node.left.left)
            temp = self.new_temp()
            self.instructions.append(f"{temp} = int_to_float({operand})")
            return temp


        if node.left is None and node.right is None:
            return self.id_map.get(node.value, node.value)


        if node.value in ('+', '-', '*', '/'):
            left_val = self.generate(node.left)
            right_val = self.generate(node.right)
            temp = self.new_temp()
            self.instructions.append(f"{temp} = {left_val} {node.value} {right_val}")
            return temp
        
        elif node.value == '=':

            left_val = self.generate(node.left)
            right_val = self.generate(node.right)
            self.instructions.append(f"{left_val} = {right_val}")
            return left_val

        return node.value

def generate_intermediate_code(tree, id_map=None):
    icg = IntermediateCodeGenerator(id_map)
    icg.generate(tree)
    return icg.instructions
