# Encodes instructions.

import re
from reg_names import regname2idx

def encode(inst_str: str, addr: int, labels: dict):
    """
    Encodes instruction as a 16-bit integer.
        inst: raw instruction
        addr: address of the instruction
        labels: dictionary containing parsed labels

    Example:
        add x1, x2, x3
    gets encoded as
        000_001_010_0000_011.
    """
    def r(reg_name) -> str:
        """
        Encode reg name as 3 bits.
        """
        idx = regname2idx(reg_name)
        return bin(idx)[2:].zfill(3)

    def si(x: str, width: int, signed: bool) -> str:
        """
        Encode x as a signed/unsigned immediate.
        x is allowed to be a label, in which case we
            compute the offset to current address.
        """
        if isinstance(x, int) or x.lstrip("-+").isdecimal():
            x = int(x)
            if x >= 0 or (not signed):
                if x >= (1<<width):
                    raise SyntaxError(f"Unsigned immediate '{x}' does not fit in {width} bits")
                return bin(x)[2:].zfill(width)
            else:
                if x < -(1<<(width-1)) or x >= (1<<(width-1)):
                    raise SyntaxError(f"Signed immediate '{x}' does not fit in {width} bits")
                return bin((1<<width) + x)[2:].zfill(width)
        
        # If is not numeric, it is a label
        if not x in labels:
            raise NameError(f"Label '{x}' not found")
        offset = labels[x] - addr
        return si(offset, width, signed)

    opcode, args_str = inst_str.split(" ", 1)
    args = re.split(r"[,\s]+", args_str)

    ## FILL DIRECTIVE
    if opcode == ".fill":
        assert len(args) == 1, "Expected 2 arguments for .fill directive"
        return int(si(args[0], 16, True), 2)

    ## IMM-TYPE
    imm_type = { "addi": "10", "nandi": "11" }
    if opcode in imm_type:
        assert len(args) == 3, "Expected 2 registers, 1 immediate for imm-type instruction"
        imm = si(args[2], 8, True)
        rd, rs = r(args[0]), r(args[1])
        return int(f"{imm_type[opcode]}_{imm[0:3]}_{rs}_{rd}_{imm[3:8]}", 2)

    ## ALU2-TYPE
    alu2_type = { "swb": "01000", "sl": "01010", "sr": "01011" }
    if opcode in alu2_type:
        assert len(args) == 2, "Expected 2 registers for alu2-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        return int(f"{alu2_type[opcode]}_{rs}_{rd}_00000", 2)
    
    ## ALU3-TYPE
    alu3_type = { "nand": "01001", "add": "01100" }
    if opcode in alu3_type:
        assert len(args) == 3, "Expected 3 registers for alu3-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        ro = r(args[2])
        res = int(f"{alu3_type[opcode]}_{rs}_{rd}_{ro}_00", 2)
        return res

    ## JUMP-TYPE
    jump_type = { "jalr": "00000" }
    if opcode in jump_type:
        assert len(args) == 2, "Expected 2 registers for jump-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        return int(f"{jump_type[opcode]}_{rs}_{rd}_00000", 2)
    
    ## BR-TYPE
    br_type = { "bn": "00101", "bz": "00110", "bp": "00111" }
    if opcode in br_type:
        assert len(args) == 2, "Expected 1 register, 1 label for br-type instruction"
        rs = r(args[0])
        imm = si(args[1], 8, True)
        assert imm[-1] == "0", "Expected multiple of 2 for br-type immediate"
        return int(f"{br_type[opcode]}_{rs}_{imm}", 2)

    ## MEM-TYPE
    mem_type = { "lw": "00010", "sw": "00011" }
    if opcode in mem_type:
        assert len(args) == 2, "Expected 2 registers for mem-type instruction"
        rd = r(args[0])
        imm, rs = re.findall(r"^(.+)\((.+)\)$", args[1])[0]
        imm = si(imm, 5, True)
        assert imm[-1] == "0", "Expected multiple of 2 for mem-type offset"
        rs = r(rs)
        return int(f"{mem_type[opcode]}_{rs}_{rd}_{imm}", 2)
    
    raise Exception(f"Opcode '{opcode}' not supported")


if __name__ == "__main__":
    print(bin(encode("addi x1, x2, 0", 0, {})))
