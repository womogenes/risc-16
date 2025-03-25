addi a0, a0, 1
addi a1, a1, 1

loop:
  add a0, a0, a1
  add a1, a0, a1
  bz x0, loop

data:
  .fill -1
