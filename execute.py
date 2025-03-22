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

    print(bin(inst)[2:].zfill(16), end="\t")

    ## IMM-TYPE
    opcode = (inst & (0b11<<14)) >> 14
    imm_imm = ((inst & (0b111<<11)) >> 6) + (inst & 0b11111)
    imm_imm = decode_signed(imm_imm, 8)
    match opcode:
        case 0b10:
            sto(rd, reg[rs] + imm_imm)
            print(f"adding {imm_imm} to reg {rs} -> reg {rd}")
        case 0b11:
            sto(rd, ~(reg[rs] & imm_imm))
            print(f"nanding {imm_imm} with reg {rs} -> reg {rd}")
    
    # Update PC (default value)
    pc += 2

    ## ALU-TYPE
    opcode = (inst & (0b11111)<<11) >> 11
    match opcode:
        case 0b01000:
            lo = reg[rs] & 0x00FF
            hi = (reg[rs] & 0xFF00) >> 8
            sto(rd, (lo<<8) + hi)
            print(f"swapping bytes of reg {rd} -> reg {rd}")
        case 0b01001:
            sto(rd, ~(reg[rs] & reg[ro]))
            print(f"nanding reg {rs} with reg {ro} -> reg {rd}")
        case 0b01010:
            sto(rd, reg[rs] << 1)
            print(f"left shifting reg {rs} -> reg {rd}")
        case 0b01011:
            sto(rd, reg[rs] >> 1)
            print(f"right shifting reg {rs} -> reg {rd}")
        case 0b01100:
            sto(rd, reg[rs] + reg[ro])
            print(f"adding reg {rs} + reg {ro} -> reg {rd}")

    ## JUMP-TYPE
    match opcode:
        case 0b00000:
            sto(rd, pc + 2)
            pc = reg[rs]
            print(rs, rd)
            print(f"jump to reg[{rs}], pc + 2 -> reg {rd}")
    
    ## BR-TYPE
    imm_br = decode_signed(inst & 0xFF, 8)
    match opcode:
        case 0b00101:
            if reg[rs] < 0:
                pc += imm_br
            print(f"branching by {imm_br} if reg {rs} < 0")
        case 0b00110:
            if reg[rs] == 0:
                pc += imm_br
            print(f"branching by {imm_br} if reg {rs} == 0")
        case 0b00111:
            if reg[rs] > 0:
                pc += imm_br
            print(f"branching by {imm_br} if reg {rs} > 0")

    ## MEM-TYPE
    imm_mem = decode_signed(inst & 0x1F, 5)
    match opcode:
        case 0b00010:
            sto(rd, mem[reg[rs] + imm_mem])
            print(f"loading mem[reg[{rs}]+{imm_mem}] -> reg {rd}")
        case 0b00011:
            mem[rs + imm_mem] = reg[rd]
            print(f"storing reg {rd} -> mem[reg[{rs}]+{imm_mem}]")

    return pc
