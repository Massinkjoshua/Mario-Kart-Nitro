
stwu 1,-32(1)
mflr 0
stw 0,36(1)
stw 31,28(1)
mr 31,3
li 0,1
stb 0,2348(31)
li 4,-1
stw 4,3428(31)
lwz 0,16(31)
cmpwi 0,0
bne finish
addi 3,31,1028
li 4,0
lis 12,32859; ori 12,12,56048
mtctr 12
bctrl
finish:
lwz 31,28(1)
lwz 0,36(1)
mtlr 0
addi 1,1,32
blr
