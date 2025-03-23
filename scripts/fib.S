# Compute the nth fibonacci number
addi a0, zero, 0x8f
neg a0, a0

li a1, 0xFFF
li a0, -2
li a1, data

halt

data:
  .fill -1
