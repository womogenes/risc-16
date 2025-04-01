# setup:
#   li a0, 10

# # Compute the nth fibonacci number
# program:
#   li a1, 1
#   li a2, 1

# loop:
#   add a1, a1, a2
#   add a2, a1, a2

#   # Restart the loop
#   bz a0, end
#   addi a0, a0, -1
#   jal loop

# end:
#   mv 1, a0
#   halt

# halt


addi a0, 0, 10
# addi 5, a0, 0

halt
