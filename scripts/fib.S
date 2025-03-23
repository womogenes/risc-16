# Compute the nth fibonacci number
addi a0, zero, 0x8f
nand a0, a0, a0
lw a0, 0(a0)

data:
  .fill 10
