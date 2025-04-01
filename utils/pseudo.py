import re
from utils.reg_names import is_vreg, r2idx, vr2idx

def expand(inst: str, opcode: str, args: list[str]):
    """
    Expand instructions with virtual registers into primitive instructions.
    Returns a list of primitive instructions that implement the original instruction.
    If no expansion is needed, returns the original instruction in a list.
    """
    # Skip if no virtual registers are used
    if not any(is_vreg(arg) for arg in args):
        return [inst]

    # Helper functions to generate load/store instructions for virtual registers
    def load_vr(reg: str, rd="1"):
        return [f"lw {rd}, {vr2idx(reg)}(0)"] if is_vreg(reg) else []
        
    def store_vr(reg: str, rs="1"):
        return [f"sw {rs}, {vr2idx(reg)}(0)"] if is_vreg(reg) else []

    # Handle memory instructions (lw, sw) specially
    if opcode in ["lw", "sw"]:
        # Parse memory operand format: imm(reg)
        imm, rs = re.findall(r"^(.+)\((.+)\)$", args[1])[0]
        
        # Load base register if it's virtual
        load_base = load_vr(rs)
        
        # Add immediate to base register if non-zero
        imm_add = [f"addi 1, 1, {imm}"] if imm != "0" else []
        
        if opcode == "lw":
            # Load from memory to temp register, then store to destination if virtual
            load_store = [f"lw 2, 0(1)"] + store_vr(args[0], "2")
        elif opcode == "sw":
            # Load source register if virtual, then store to memory
            load_src = load_vr(args[0], "2")
            load_store = load_src + [f"sw 2, 0(1)"]
            
        return load_base + imm_add + load_store

    if opcode in ["add", "nand"]:
        # If rd is virtual, use "1" (and load_vr will return non-empty list),
        #   else use the actual value of rd
        rd, rs, ro = args
        rd = "1" if is_vreg(rd) else rd
        rs = "1" if is_vreg(rs) else rs
        ro = "2" if is_vreg(ro) else ro
        return load_vr(rs) + load_vr(ro, "2") + [f"{opcode} {rd}, {rs}, {ro}"] + store_vr(args[0])
        
    elif opcode in ["addi", "nandi"]:
        rd, rs, imm = args
        rd = "1" if is_vreg(rd) else rd
        rs = "1" if is_vreg(rs) else rs
        return load_vr(rs) + [f"{opcode} {rd}, {rs}, {imm}"] + store_vr(rd)
        
    elif opcode in ["swb", "sl", "sr"]:
        rd, rs = args
        rd = "1" if is_vreg(rd) else rd
        rs = "1" if is_vreg(rs) else rs
        return load_vr(args[1]) + [f"{opcode} {rd}, {rs}"] + store_vr(args[0])
        
    elif opcode == "jalr":
        rd, rs = args
        rd = "1" if is_vreg(rd) else rd
        rs = "1" if is_vreg(rs) else rs
        return load_vr(rs) + [f"{opcode} {rd}, {rs}"] + store_vr(rd)
        
    elif opcode in ["bn", "bz", "bp"]:
        rs, label = args
        rs = "1" if is_vreg(rs) else rs
        return load_vr(rs) + [f"{opcode} {rs}, {label}"]
        
    # Default case - no expansion needed
    return [inst]
