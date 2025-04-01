setup:
  li a0, 10

# Compute the nth fibonacci number
program:
  li a1, 1
  li a2, 1

loop:
  add a1, a1, a2
  mv a3, a2
  mv a2, a1
  mv a1, a3

  # Restart the loop
  bz a0, end
  addi a0, a0, -1
  j loop

end:
  mv 1, a0
  halt

halt

halt
