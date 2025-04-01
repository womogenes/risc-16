# RISC-16 interpreter

An implementation 16-bit version of RISC-V assembly.

- ISA in `isa.txt`
- Main interpreter class in `interpreter.py`, which uses `encode.py` and `execute.py`
- `decode.py` is used only for testing

## TODO

Small optimization: line 5 is redundant with line 4 in the example below because we have a set of `li` instructions with the same value going to virtual registers.

```
pc: 4096        inst: 0b1000000000101010        addi 1, 0, 10   regs:      0,      0,      0,      0,      0
pc: 4097        inst: 0b0001100000100011           sw 1, 3(0)   regs:      0,     10,      0,      0,      0
pc: 4098        inst: 0b1000000000100001         addi 1, 0, 1   regs:      0,     10,      0,      0,      0
pc: 4099        inst: 0b0001100000100100           sw 1, 4(0)   regs:      0,      1,      0,      0,      0
pc: 4100        inst: 0b1000000000100001         addi 1, 0, 1   regs:      0,      1,      0,      0,      0
pc: 4101        inst: 0b0001100000100101           sw 1, 5(0)   regs:      0,      1,      0,      0,      0
```

Also, here:

```
pc: 4110        inst: 0b0001000000100011           lw 1, 3(0)   regs:      0,      3,      1,      0,      0
pc: 4111        inst: 0b0011000100001001              bz 1, 9   regs:      0,     10,      1,      0,      0
pc: 4112        inst: 0b0001000000100011           lw 1, 3(0)   regs:      0,     10,      1,      0,      0
pc: 4113        inst: 0b1011100100111111        addi 1, 1, -1   regs:      0,     10,      1,      0,      0
```

This comes from

```
bz a0, end
addi a0, a0, -1
```

There is no need to re-load a register if it's already loaded. Caching theory?
