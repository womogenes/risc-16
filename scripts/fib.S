addi 0, 0, 1
addi 1, 1, 1

loop:
  add 0, 0, 1
  add 1, 0, 1
  bz 0, loop

# data:
#   .fill -1
