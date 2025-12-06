import re

class AssemblyGenerator:
    def __init__(self, id_types=None):
        self.instructions = []
        self.id_types = id_types if id_types else {}
        self.registers = ["R1", "R2"] # Restricted to 2 registers as requested

    def get_type(self, operand):
        """Determine if operand is FLOAT or INT"""
        operand = operand.strip()
        
        # Check for int_to_float wrapper
        if operand.startswith("int_to_float("):
            return "FLOAT"
            
        # Check for literals
        try:
            if '.' in operand:
                float(operand)
                return "FLOAT"
            int(operand)
            return "INT"
        except ValueError:
            pass
            
        # Check for identifiers
        if operand in self.id_types:
            return self.id_types[operand]
            
        # Default/Fallback (e.g. temps are usually floats if they result from float ops)
        # But we might need to track temp types. For now, assume temps are FLOAT if not known?
        # Or maybe we can infer from context.
        return "INT" 

    def parse_operand(self, operand):
        """Extract value from int_to_float or return as is"""
        operand = operand.strip()
        match = re.match(r'int_to_float\((.+)\)', operand)
        if match:
            return match.group(1)
        return operand

    def is_literal(self, op):
        return op.replace('.','',1).isdigit()

    def generate(self, icg_instructions):
        asm_code = []
        current_temp_in_r1 = None
        
        for instr in icg_instructions:
            if '=' not in instr:
                continue
                
            lhs, rhs = instr.split('=', 1)
            lhs = lhs.strip()
            rhs = rhs.strip()
            
            # Check for binary operation
            # We support +, -, *, /
            op_match = re.search(r'([\+\-\*\/])', rhs)
            
            if op_match:
                # Binary Operation
                op = op_match.group(1)
                parts = rhs.split(op, 1)
                op1_raw = parts[0].strip()
                op2_raw = parts[1].strip()
                
                op1 = self.parse_operand(op1_raw)
                op2 = self.parse_operand(op2_raw)
                
                type1 = self.get_type(op1_raw)
                type2 = self.get_type(op2_raw)
                
                is_float_op = (type1 == "FLOAT" or type2 == "FLOAT")
                
                # Determine Instruction Suffix
                suffix = "F" if is_float_op else ""
                
                # Map operator to instruction
                op_map = {
                    '+': 'ADD',
                    '-': 'SUB',
                    '*': 'MUL',
                    '/': 'DIV'
                }
                instr_name = op_map[op] + suffix
                
                reg1 = "R1"
                reg2 = "R2"
                
                is_commutative = op in ['+', '*']
                op1_is_lit = self.is_literal(op1)
                op2_is_lit = self.is_literal(op2)
                
                # Swap if commutative and op1 is lit (to put lit in op2 position)
                if is_commutative and op1_is_lit and not op2_is_lit:
                    op1, op2 = op2, op1
                    op1_is_lit, op2_is_lit = op2_is_lit, op1_is_lit
                    type1, type2 = type2, type1
                
                # Swap if commutative and op2 is in R1 but op1 is not
                if is_commutative and op2 == current_temp_in_r1 and op1 != current_temp_in_r1:
                    op1, op2 = op2, op1
                    op1_is_lit, op2_is_lit = op2_is_lit, op1_is_lit
                    type1, type2 = type2, type1

                # Generate Code
                if op1 == current_temp_in_r1:
                    # R1 has op1
                    if op2_is_lit:
                        asm_code.append(f"{instr_name} {reg1}, {reg1}, #{op2}")
                    else:
                        # Load op2 into R2
                        load_instr2 = "LOAD" + ("F" if type2 == "FLOAT" else "")
                        asm_code.append(f"{load_instr2} {reg2}, {op2}")
                        asm_code.append(f"{instr_name} {reg1}, {reg1}, {reg2}")
                        
                elif op2 == current_temp_in_r1:
                    # R1 has op2 (and op1 is NOT in R1)
                    # Non-commutative case (otherwise swapped)
                    if op1_is_lit:
                        # Lit - R1
                        asm_code.append(f"{instr_name} {reg1}, #{op1}, {reg1}")
                    else:
                        # Var - R1
                        load_instr1 = "LOAD" + ("F" if type1 == "FLOAT" else "")
                        asm_code.append(f"{load_instr1} {reg2}, {op1}")
                        asm_code.append(f"{instr_name} {reg1}, {reg2}, {reg1}")
                        
                else:
                    # Neither in R1
                    if op1_is_lit and not op2_is_lit:
                        # Lit OP Var (Non-commutative, e.g. 3 - y)
                        # Load op2 to R1
                        load_instr = "LOAD" + ("F" if type2 == "FLOAT" else "")
                        asm_code.append(f"{load_instr} {reg1}, {op2}")
                        # 3 - R1
                        asm_code.append(f"{instr_name} {reg1}, #{op1}, {reg1}")
                    else:
                        # Load op1 to R1
                        load_instr = "LOAD" + ("F" if type1 == "FLOAT" else "")
                        if op1_is_lit:
                            asm_code.append(f"{load_instr} {reg1}, #{op1}")
                        else:
                            asm_code.append(f"{load_instr} {reg1}, {op1}")
                            
                        if op2_is_lit:
                            asm_code.append(f"{instr_name} {reg1}, {reg1}, #{op2}")
                        else:
                            load_instr2 = "LOAD" + ("F" if type2 == "FLOAT" else "")
                            asm_code.append(f"{load_instr2} {reg2}, {op2}")
                            asm_code.append(f"{instr_name} {reg1}, {reg1}, {reg2}")
                
                # Store result logic
                if lhs.startswith('temp'):
                    current_temp_in_r1 = lhs
                    self.id_types[lhs] = "FLOAT" if is_float_op else "INT"
                else:
                    store_instr = "STR" + ("F" if is_float_op else "")
                    asm_code.append(f"{store_instr} {lhs}, {reg1}")
                    current_temp_in_r1 = None

            else:
                # Simple Assignment: x = y
                op_raw = rhs
                op = self.parse_operand(op_raw)
                type_op = self.get_type(op_raw)
                
                reg = "R1"
                
                if op == current_temp_in_r1:
                    # Value already in R1
                    pass
                else:
                    load_instr = "LOAD" + ("F" if type_op == "FLOAT" else "")
                    if op.replace('.','',1).isdigit():
                        asm_code.append(f"{load_instr} {reg}, #{op}")
                    else:
                        asm_code.append(f"{load_instr} {reg}, {op}")
                
                if lhs.startswith('temp'):
                    current_temp_in_r1 = lhs
                    self.id_types[lhs] = type_op
                else:
                    store_instr = "STR" + ("F" if type_op == "FLOAT" else "")
                    asm_code.append(f"{store_instr} {lhs}, {reg}")
                    current_temp_in_r1 = None

        return asm_code

def generate_assembly(instructions, id_types):
    generator = AssemblyGenerator(id_types)
    return generator.generate(instructions)
