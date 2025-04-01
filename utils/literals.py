import re

def encode_literal(x: str | int, width: int, signed: bool):
    """
    Decode a literal decimal, hex, or binary string.
    If it is none of the above, return None.
    """
    if not (isinstance(x, int) or (isinstance(x, str) and re.match(r"-?\d+", x) or re.match("0x[0-9a-f]+", x))):
        return None
    
    if isinstance(x, str):
        x = eval(x)
    
    assert isinstance(x, int)
    if x >= 0 or (not signed):
        if x >= (1<<width):
            raise SyntaxError(f"Unsigned immediate '{x}' does not fit in {width} bits")
        return bin(x)[2:].zfill(width)
    else:
        if x < -(1<<(width-1)) or x >= (1<<(width-1)):
            raise SyntaxError(f"Signed immediate '{x}' does not fit in {width} bits")
        return bin((1<<width) + x)[2:].zfill(width)

def decode_literal(x: int, width: int):
    """
    Decode a signed int with given width.
    """
    if not 0 <= x < (1<<width):
        raise Exception(f"Immediate '{x}' does not fit in {width} bits.")
    return (x & ((1<<width)-1)) - (x & (1<<(width-1)))*2
