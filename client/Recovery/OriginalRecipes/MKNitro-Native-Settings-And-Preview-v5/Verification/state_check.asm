
 lwz 12,100(27); cmpwi 12,0; beq original
 lwz 12,12(12); cmpwi 12,0; beq original
 lwz 12,4(12); cmpwi 12,110; beq course
 cmpwi 12,111; bne original
 course:
li 12,0; cmpw 0,12; blr
original:
cmpwi 0,3; blr
