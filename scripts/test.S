    lw 1, 2(x0)    # load reg1 with 5 (uses symbolic address)
    lw 2, 2(x1)        # load reg2 with -1 (uses numeric address)
    addi x1, x2, 0

start:
    add x1, x1, x2        # decrement reg1 -- could have been addi 1,1,-1

addi a1, x0, 100
addi a1, x1, -1
nandi a1, x2, 100
nandi a1, x3, -1

swb x3, x2
nand a1, x0, x3
sl x3, x0
sl x1, x2

# done: halt                 # end of program

add x1, x2, x3
addi x1, x2, 0
addi x1, x0, 100
addi x1, x2, -1
nandi x1, x2, 100
nandi x1, x3, -1
swb x3, x2
nand x1, x0, x3
sl x1, x2
lw x1, 0(x0)
sw x1, 2(x0)
bn x1, start
bz x2, count

jalr x0, x0



# Data section
count:      .fill 5
neg1:       .fill 42
startAddr:  .fill start      # will contain the address of start (2)
