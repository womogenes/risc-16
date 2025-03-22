# Decodes instructions.

from reg_names import REG_NAMES

def decode(inst: int):
    """
    Decodes a 16-bit instruction into a string representation.
        inst: 16-bit integer instruction

    Example:
        0b0110001000101100 (encode("add x1, x2, x3", 0, {}))
    gets decoded as
        "add x1, x2, x3"
    """
    # Check that inst is a non-negative 16-bit integer
    if not isinstance(inst, int):
        raise TypeError("Instruction must be an integer")
    if inst < 0 or inst >= (1 << 16):
        raise ValueError("Instruction must be a non-negative 16-bit integer")

    # Convert instruction to 16-bit binary string
    bin_str = bin(inst)[2:].zfill(16)

    # Helper function to get register name from 3-bit binary string
    def get_reg_name(reg_bits: str) -> str:
        idx = int(reg_bits, 2)
        if idx >= len(REG_NAMES):
            raise ValueError(f"Invalid register index: {idx}")
        return REG_NAMES[idx][0]  # Return canonical name

    # Special case for .fill: if the value is small (< 64) and doesn't match valid opcodes
    if inst < 64 and not bin_str.startswith(("01", "10", "11", "000", "001")):
        return f".fill {inst}"
    
    # IMM-TYPE instructions (addi, nandi)
    if bin_str[0:2] in ["10", "11"]:
        opcode = "addi" if bin_str[0:2] == "10" else "nandi"
        # Format in encode.py: f"{imm_type[opcode]}_{imm[0:3]}_{rs}_{rd}_{imm[3:8]}"
        imm_high = bin_str[2:5]
        rs = get_reg_name(bin_str[5:8])
        rd = get_reg_name(bin_str[8:11])
        imm_low = bin_str[11:16]
        imm = imm_high + imm_low
        
        # Convert imm to signed integer
        imm_val = int(imm, 2)
        if imm_high[0] == "1":  # If MSB is 1, it's negative
            imm_val -= (1 << 8)
        
        return f"{opcode} {rd}, {rs}, {imm_val}"
    
    # ALU3-TYPE (add, nand)
    elif bin_str[0:5] in ["01100", "01001"]:
        # Format in encode.py: f"{alu3_type[opcode]}_{rs}_{rd}_{ro}_00"
        opcode = "add" if bin_str[0:5] == "01100" else "nand"
        rs = get_reg_name(bin_str[5:8])
        rd = get_reg_name(bin_str[8:11])
        ro = get_reg_name(bin_str[11:14])
        return f"{opcode} {rd}, {rs}, {ro}"
    
    # ALU2-TYPE (swb, sl, sr)
    elif bin_str[0:5] in ["01000", "01010", "01011"]:
        # Format in encode.py: f"{alu2_type[opcode]}_{rs}_{rd}_00000"
        opcode_map = {"01000": "swb", "01010": "sl", "01011": "sr"}
        opcode = opcode_map[bin_str[0:5]]
        rs = get_reg_name(bin_str[5:8])
        rd = get_reg_name(bin_str[8:11])
        return f"{opcode} {rd}, {rs}"
    
    # JUMP-TYPE (jalr)
    elif bin_str[0:5] == "00000":
        # Format in encode.py: f"{jump_type[opcode]}_{rs}_{rd}_00000"
        rs = get_reg_name(bin_str[5:8])
        rd = get_reg_name(bin_str[8:11])
        return f"jalr {rd}, {rs}"
    
    # MEM-TYPE (lw, sw)
    elif bin_str[0:5] in ["00010", "00011"]:
        # Format in encode.py: f"{mem_type[opcode]}_{rs}_{rd}_{imm}"
        opcode = "lw" if bin_str[0:5] == "00010" else "sw"
        rs = get_reg_name(bin_str[5:8])
        rd = get_reg_name(bin_str[8:11])
        imm = int(bin_str[11:16], 2)
        # Convert to signed if needed
        if bin_str[11] == "1":  # If MSB is 1, it's negative
            imm -= (1 << 5)
        return f"{opcode} {rd}, {imm}({rs})"
    
    # BR-TYPE (bn, bz, bp)
    elif bin_str[0:5] in ["00101", "00110", "00111"]:
        # Format in encode.py: f"{br_type[opcode]}_{rs}_{imm}"
        opcode_map = {"00101": "bn", "00110": "bz", "00111": "bp"}
        opcode = opcode_map[bin_str[0:5]]
        rs = get_reg_name(bin_str[5:8])
        imm = int(bin_str[8:16], 2)
        # Convert to signed if needed
        if bin_str[8] == "1":  # If MSB is 1, it's negative
            imm -= (1 << 8)
        return f"{opcode} {rs}, {imm}"
    
    # Default case - treat as .fill directive
    return f".fill {inst}"


if __name__ == "__main__":
    from encode import encode
    
    # Generate fresh test cases from encoder
    print("=== Generating test cases from encoder ===")
    test_insts = [
        "add x1, x2, x3",
        "addi x1, x2, 0",
        "addi x1, x0, 100",
        "addi x1, x2, -1",
        "nandi x1, x2, 100",
        "nandi x1, x3, -1",
        "swb x3, x2",
        "nand x1, x0, x3",
        "sl x1, x2",
        "lw x1, 0(x0)",
        "sw x1, 2(x0)",
        "jalr x1, x2",
        "bn x1, 4",
        "bz x2, -2"
    ]
    
    test_cases = []
    for inst in test_insts:
        try:
            encoded = encode(inst, 0, {})
            test_cases.append((inst, encoded))
            print(f"{inst} -> {bin(encoded)[2:].zfill(16)} (decimal: {encoded})")
        except Exception as e:
            print(f"Error encoding {inst}: {e}")
    
    # Add a .fill test case manually
    test_cases.append((".fill 5", 5))
    print(".fill 5 -> 0000000000000101 (decimal: 5)")
    
    # Run test cases
    print("\n=== Running decode tests ===")
    pass_count = 0
    
    for original_inst, encoded in test_cases:
        try:
            decoded = decode(encoded)
            # For .fill, we don't care about exact match
            if original_inst.startswith(".fill"):
                if decoded.startswith(".fill"):
                    pass_count += 1
                    print(f"{original_inst} -> {encoded} -> {decoded}")
                else:
                    print(f"{original_inst} -> {encoded} -> {decoded} (expected {original_inst})")
            else:
                # For other instructions, we want exact match
                if decoded == original_inst:
                    pass_count += 1
                    print(f"{original_inst} -> {encoded} -> {decoded}")
                else:
                    print(f"{original_inst} -> {encoded} -> {decoded} (expected {original_inst})")
        except Exception as e:
            print(f"Error decoding {encoded}: {e}")
    
    print(f"\nPassed {pass_count}/{len(test_cases)} tests")
    
    # Test round-trip encoding/decoding
    print("\n=== Testing round-trip encoding/decoding ===")
    for inst in test_insts:
        try:
            encoded = encode(inst, 0, {})
            decoded = decode(encoded)
            if decoded == inst:
                print(f"{inst} -> {bin(encoded)[2:].zfill(16)} -> {decoded}")
            else:
                print(f"{inst} -> {bin(encoded)[2:].zfill(16)} -> {decoded} (expected {inst})")
        except Exception as e:
            print(f"Error with {inst}: {e}")
            raise e
