
 lwz 12,100(27); cmpwi 12,0; beq original
 lwz 12,12(12); cmpwi 12,0; beq original
 lwz 12,4(12); cmpwi 12,110; beq course
 cmpwi 12,111; bne original
 course:
li 6,0
original:
lis 12,32863; addi 12,12,22956; mtctr 12; bctr
