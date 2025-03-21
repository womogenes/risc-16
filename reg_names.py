# Hard-coded register names.
# First value in each list is the canonical name.

REG_NAMES = [
    ["x0", "zero", "0"],
    ["x1", "sp", "1"],
    ["x2", "a0", "2"],
    ["x3", "a1", "3"]
]

def regname2idx(name: str):
    """
    Return index of register given name.
    """
    for reg_idx, names in enumerate(REG_NAMES):
        if name in names:
            return reg_idx
    raise Exception(f"Register name '{name}' not found.")
