# Hard-coded register names.
# First value in each list is the canonical name.

REG_NAMES = [
    ["0", "x0", "r0", "zero"],
    ["1", "r1"],
    ["2", "r2"],
    ["3", "r3", "in"],
    ["4", "r4", "o1"],
    ["5", "r5", "o2"]
]

VREG_NAMES = [
    None,
    ["x1", "ra"],
    ["x2", "sp"],
    ["x3", "a0"],
    ["x4", "a1"],
    ["x5", "a2"],
    ["x6", "a3"],
    ["x7", "a4"],
    ["x8", "s0"],
    ["x9", "s1"],
    ["x10", "s2"],
    ["x11", "s3"],
    ["x12", "s4"],
    ["x13", "t0"],
    ["x14", "t1"],
    ["x15", "t2"]
]

def is_vreg(name: str):
    """
    Is it a virtual register?
    """
    for names in VREG_NAMES:
        if names != None and name in names:
            return True
    return False

def regname2idx(name: str):
    """
    Return index of register given name.
    """
    for reg_idx, names in enumerate(REG_NAMES):
        if name in names:
            return reg_idx
    raise Exception(f"Register name '{name}' not found.")
