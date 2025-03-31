# Encodes instructions.

import re
from collections import defaultdict

from utils.reg_names import regname2idx, is_vreg
from utils.literals import encode_literal


def encode(inst: str, addr: int, labels: dict) -> int:
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

    def si(x: str, width: int, signed: bool, offset: bool = False) -> str:
        """
        Encode x as a signed/unsigned immediate.
        x is allowed to be a label, in which case we optionally
            compute the offset from current address.
        Offset: whether to compute label as an offset to addr.
        """
        res = encode_literal(x, width, signed)

        if res == None:
            # If labels is not provided, this is probably a first pass
            if labels == None:
                return bin(0xFFFF)[2:]

            # If x is not numeric, it is a label
            if not x in labels:
                raise NameError(f"Label '{x}' not found")
            value = labels[x] - addr if offset else labels[x]
            return si(value, width, signed)

        return res

    def join(subinstructions: list):
        """
        Recursively join list of instructions.
        """
        return sum([encode(inst, addr, labels) for inst in subinstructions], [])

    opcode, args_str = re.findall(r"^([\.\w]+)(?: (.+))?$", inst)[0]
    args = re.split(r"[,\s]+", args_str)

    # FILL DIRECTIVE
    if opcode == ".fill":
        return [int(si(args[0], 16, True), 2)]

    # PSEUDOINSTRUCTIONS
    if opcode == "halt":
        return encode("jalr 0, 0", addr, labels)

    if opcode == "neg":
        rd, rs = args
        return join([f"nand {rd}, {rs}, {rs}",
                     f"addi {rd}, {rd}, 1"])

    if opcode == "nop":
        return join([f"add 0, 0, 0"])

    if opcode == "li":
        assert len(args) == 2, \
            "Expected 1 register, 1 immediate for li instruction"
        rd, imm_raw = args
        imm = si(imm_raw, 16, True)
        imm_lo = int(imm[8:16], 2)

        # Add an extra 1 to compensate for sign extensions
        # Two's complement is weird
        imm_hi = (int(imm[0:8], 2) + (1 if imm_lo & 0xC0 else 0)) & 0xFF

        # If there are high bits, we must do swap thing
        # Also must do swap thing if it's a label
        if imm_hi != 0 or (encode_literal(imm_raw, 16, True) == None):
            return join([f"addi {rd}, zero, {imm_hi}",
                         f"swb {rd}, {rd}",
                         f"addi {rd}, {rd}, {imm_lo}"])

        # Otherwise, we can add directly
        return encode(f"addi {rd}, zero, {imm_lo}", addr, labels)

    if opcode == "jal":
        assert len(args) == 1, "Expected 1 label for jal instruction"
        imm = si(args[0], 16, True, True)
        return join([f"li ra, {imm}",
                     f"jalr ra, ra"])

    # IMM-TYPE
    imm_type = {"addi": "10", "nandi": "11"}
    if opcode in imm_type:
        assert len(
            args) == 3, "Expected 2 registers, 1 immediate for imm-type instruction"
        imm = si(args[2], 8, True)
        rd, rs = r(args[0]), r(args[1])
        return [int(f"{imm_type[opcode]}_{imm[0:3]}_{rs}_{rd}_{imm[3:8]}", 2)]

    # ALU2-TYPE
    alu2_type = {"swb": "01000", "sl": "01010", "sr": "01011"}
    if opcode in alu2_type:
        assert len(args) == 2, "Expected 2 registers for alu2-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        return [int(f"{alu2_type[opcode]}_{rs}_{rd}_00000", 2)]

    # ALU3-TYPE
    alu3_type = {"nand": "01001", "add": "01100"}
    if opcode in alu3_type:
        assert len(args) == 3, "Expected 3 registers for alu3-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        ro = r(args[2])
        return [int(f"{alu3_type[opcode]}_{rs}_{rd}_{ro}_00", 2)]

    # JUMP-TYPE
    jump_type = {"jalr": "00000"}
    if opcode in jump_type:
        assert len(args) == 2, "Expected 2 registers for jump-type instruction"
        rd = r(args[0])
        rs = r(args[1])
        return [int(f"{jump_type[opcode]}_{rs}_{rd}_00000", 2)]

    # BR-TYPE
    br_type = {"bn": "00101", "bz": "00110", "bp": "00111"}
    if opcode in br_type:
        assert len(
            args) == 2, "Expected 1 register, 1 label for br-type instruction"
        rs = r(args[0])
        imm = si(args[1], 8, True, True)
        return [int(f"{br_type[opcode]}_{rs}_{imm}", 2)]

    # MEM-TYPE
    mem_type = {"lw": "00010", "sw": "00011"}
    if opcode in mem_type:
        assert len(args) == 2, "Expected 2 registers for mem-type instruction"
        rd = r(args[0])
        imm, rs = re.findall(r"^(.+)\((.+)\)$", args[1])[0]
        imm = si(imm, 5, True)
        rs = r(rs)
        return [int(f"{mem_type[opcode]}_{rs}_{rd}_{imm}", 2)]

    raise Exception(f"Opcode '{opcode}' not supported")


if __name__ == "__main__":
    print(bin(encode("addi x1, x2, 0", 0, {})))
