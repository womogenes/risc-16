import re

def decode_literal(x: str | int, width: int, signed: bool):
    """
    Decode a literal decimal, hex, or binary string.
    """
    if not (isinstance(x, int) or (isinstance(x, str) and re.match("-?\d+", x) or re.match("0x[0-9a-f]+", x))):
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
