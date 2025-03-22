# Executes instructinos.

def execute(inst: int, reg: list, mem: list, pc: int):
    """
    Decode instruction and execute it.
        Modifies registers and memory, returns new PC.
    """
    if not (isinstance(inst, int) and 0 <= inst < (1<<16)):
        raise Exception(f"Encoded instruction is not a 16-bit value")

    def decode_signed(x: int, width: int):
        """
        Decode a signed int with given width.
        """
        if not 0 <= x < (1<<width):
            raise Exception(f"Immediate '{x}' does not fit in {width} bits.")
        return (x & ((1<<width)-1)) - (x & (1<<(width-1)))*2

    opcode_mask = 0b111 << 13
    opcode = (inst & opcode_mask) >> 13

    regA = inst & 0b000_111_000_0000_000
    regB = inst & 0b000_000_111_0000_000
    regC = inst & 0b000_000_000_0000_111

    pc += 1

    ## RRR-TYPE INSTRUCTION
    if opcode in [0b000, 0b010]:
        match opcode:
            case 0b000:
                reg[regA] = reg[regB] & reg[regC]
            case 0b001:
                reg[regA] = (reg[regB] + reg[regC]) & 0xFFFF

    ## RRI-TYPE INSTRUCTION
    elif opcode in [0b001, 0b100, 0b101, 0b110]:
        imm = decode_signed(inst & 0b1111111, 7)
        match opcode:
            case 0b001:
                reg[regA] = (reg[regB] + imm) & 0xFFFF
            case 0b101:
                mem[regB + imm] = reg[regA]
            case 0b100:
                reg[regA] = mem[regB + imm]
            case 0b110:
                if reg[regA] == reg[regB]:
                    pc += imm
