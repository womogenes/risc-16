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
        if isinstance(x, int) or x.isnumeric():
            x = int(x)
            if x > 0 or (not signed):
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
    if len(args) < 2:
        raise SyntaxError(f"Instruction '{inst_str}' has too few arguments")

    ## REG-REG-REG-TYPE INSTRUCTIONS
    rrr_type = { "add": "000", "nand": "010" }
    if opcode in rrr_type:
        assert len(args) == 3, "Expected 3 registers for RRR-type instruction"
        return int(f"{rrr_type[opcode]}_{r(args[0])}_{r(args[1])}_0000_{r(args[2])}", 2)

    ## REG-REG-IMM-TYPE INSTRUCTIONS
    rri_type = { "addi": "001", "sw": "100", "lw": "101", "beq": "110" }
    if opcode in rri_type:
        assert len(args) == 3, "Expected 2 registers and 1 immediate for RRI-type instruction"
        return int(f"{rri_type[opcode]}_{r(args[0])}_{r(args[1])}_{si(args[2], 7, 1)}", 2)

    ## REG-IMM-TYPE INSTRUCTIONS
    ri_type = { "lui": "011", "jalr": "111" }
    if opcode in ri_type:
        assert len(args) == 2, "Expected 1 register and 1 immediate for RI-type instruction"
        return int(f"{ri_type[opcode]}_{r(args[0])}_{si(args[1], 7, 0)}", 2)
    
    raise Exception(f"Opcode '{opcode}' not supported")


if __name__ == "__main__":
    print(bin(encode("addi x1, x2, 0", 0, {})))
