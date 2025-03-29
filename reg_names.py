# Hard-coded register names.
# First value in each list is the canonical name.

REG_NAMES = [
    ["x0", "zero"],
    ["x1", "ra"],
    ["x2", "sp"],
    ["x3", "gp"],
    ["x4", "tp"],
    ["x5", "t0"],
    ["x6", "t1"],
    ["x7", "t2"]
]

def regname2idx(name: str):
    """
    Return index of register given name.
    """
    for reg_idx, names in enumerate(REG_NAMES):
        if name in names:
            return reg_idx
    raise Exception(f"Register name '{name}' not found.")
