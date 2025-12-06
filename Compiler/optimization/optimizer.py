import re

def optimize_code(instructions):
    """
    Optimizes intermediate code by:
    1. Inlining simple temporary variables (literals, identifiers, int_to_float).
    2. Merging complex operations into final assignments where possible.
    3. Preventing multiple binary operations in a single statement.
    """
    if not instructions:
        return []

    definitions = {}  # Stores inlinable expressions for temps
    optimized_instructions = []
    
    # Track the last emitted instruction that was a "complex" temp assignment
    # Format: {'index': int, 'temp': str}
    last_complex_instr = None

    def is_complex(expr):
        # Check for binary operators +, -, *, /
        # We assume int_to_float(...) is NOT complex in this context
        # as it can be part of a single operation.
        return any(op in expr for op in ['+', '-', '*', '/'])

    for instr in instructions:
        if '=' not in instr:
            optimized_instructions.append(instr)
            last_complex_instr = None
            continue
            
        lhs, rhs = instr.split('=', 1)
        lhs = lhs.strip()
        rhs = rhs.strip()
        
        # 1. Substitute existing definitions into RHS
        def replace_match(match):
            word = match.group(0)
            if word in definitions:
                return definitions[word]
            return word
            
        # Replace identifiers in RHS with their definitions
        new_rhs = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', replace_match, rhs)
        
        # 2. Analyze the new RHS
        rhs_is_complex = is_complex(new_rhs)
        
        # 3. Decide what to do based on LHS type
        if lhs.startswith('temp'):
            if not rhs_is_complex:
                # Simple expression (literal, ID, or int_to_float)
                # Store in definitions for future inlining
                definitions[lhs] = new_rhs
                # Do NOT emit yet
            else:
                # Complex expression (has binary ops)
                # We must emit this, as we don't want to inline it into another op
                optimized_instructions.append(f"{lhs} = {new_rhs}")
                
                # Track this instruction for potential peephole optimization
                last_complex_instr = {
                    'index': len(optimized_instructions) - 1,
                    'temp': lhs
                }
        else:
            # LHS is a User Variable (e.g., x, y, id1)
            # We always emit assignments to user variables
            
            # Peephole Optimization:
            # If we are assigning a temp that was just computed in the previous complex instruction,
            # we can merge them.
            # Example:
            #   temp3 = int_to_float(3) * int_to_float(4)  (last_complex_instr)
            #   x = temp3
            # Becomes:
            #   x = int_to_float(3) * int_to_float(4)
            
            merged = False
            if last_complex_instr and new_rhs == last_complex_instr['temp']:
                # Modify the previous instruction
                prev_idx = last_complex_instr['index']
                prev_instr = optimized_instructions[prev_idx]
                # Replace the LHS of previous instruction with current LHS
                # prev_instr is "tempX = expr"
                _, prev_rhs = prev_instr.split('=', 1)
                optimized_instructions[prev_idx] = f"{lhs} = {prev_rhs.strip()}"
                merged = True
            
            if not merged:
                optimized_instructions.append(f"{lhs} = {new_rhs}")
            
            # Reset last_complex_instr because we've moved past it
            last_complex_instr = None
            
    # 4. Renumber temporary variables
    final_instructions = []
    temp_map = {}
    temp_counter = 1
    
    for instr in optimized_instructions:
        # Replace old temps with new temps in the instruction string
        # We need to be careful to replace only whole words
        
        # First, identify if LHS is a temp definition
        if '=' in instr:
            lhs, rhs = instr.split('=', 1)
            lhs = lhs.strip()
            if lhs.startswith('temp'):
                if lhs not in temp_map:
                    temp_map[lhs] = f"temp{temp_counter}"
                    temp_counter += 1
        
        # Now replace all occurrences of old temps in the instruction
        def replace_temp(match):
            word = match.group(0)
            return temp_map.get(word, word)
            
        new_instr = re.sub(r'\btemp\d+\b', replace_temp, instr)
        final_instructions.append(new_instr)

    return final_instructions
