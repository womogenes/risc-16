# Executes instructinos.

def execute(inst: int, reg: list, mem: list, pc: int):
    """
    Decode instruction and execute it.
        Modifies registers and memory, returns new PC.
    """
    if not (isinstance(inst, int) and 0 <= inst < (1<<16)):
        raise Exception(f"Encoded instruction is not a 16-bit value")
    
    def sto(rd, val):
        """
        Store a value in a register
        """
        assert isinstance(val, int)
        if rd != 0:
            reg[rd] = val & 0xFFFF
            return 1
        return 0

    def decode_signed(x: int, width: int):
        """
        Decode a signed int with given width.
        """
        if not 0 <= x < (1<<width):
            raise Exception(f"Immediate '{x}' does not fit in {width} bits.")
        return (x & ((1<<width)-1)) - (x & (1<<(width-1)))*2

    rs = (inst & (0b111<<8)) >> 8
    rd = (inst & (0b111<<5)) >> 5
    ro = (inst & (0b111<<2)) >> 2


    ## IMM-TYPE
    opcode = (inst & (0b11<<14)) >> 14
    imm_imm = ((inst & (0b111<<11)) >> 6) + (inst & 0b11111)
    imm_imm = decode_signed(imm_imm, 8)
    match opcode:
        case 0b10:
            sto(rd, reg[rs] + imm_imm)
        case 0b11:
            sto(rd, ~(reg[rs] & imm_imm))
    
    # Update PC (default value)
    pc += 2

    ## ALU-TYPE
    opcode = (inst & (0b11111)<<11) >> 11
    match opcode:
        case 0b01000:
            lo = reg[rs] & 0x00FF
            hi = (reg[rs] & 0xFF00) >> 8
            sto(rd, (lo<<8) + hi)
        case 0b01001:
            sto(rd, ~(reg[rs] & reg[ro]))
        case 0b01010:
            sto(rd, reg[rs] << 1)
        case 0b01011:
            sto(rd, reg[rs] >> 1)
        case 0b01100:
            sto(rd, reg[rs] + reg[ro])

    ## JUMP-TYPE
    match opcode:
        case 0b00000:
            sto(rd, pc + 2)
            pc = reg[rs]
    
    ## BR-TYPE
    imm_br = decode_signed(inst & 0xFF, 8)
    match opcode:
        case 0b00101:
            if reg[rs] < 0:
                pc += imm_br
        case 0b00110:
            if reg[rs] == 0:
                pc += imm_br
        case 0b00111:
            if reg[rs] > 0:
                pc += imm_br

    ## MEM-TYPE
    imm_mem = decode_signed(inst & 0x1F, 5)
    match opcode:
        case 0b00010:
            sto(rd, mem[reg[rs] + imm_mem])
        case 0b00011:
            mem[rs + imm_mem] = reg[rd]

    return pc
