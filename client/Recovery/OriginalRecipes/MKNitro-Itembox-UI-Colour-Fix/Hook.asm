stwu 1,-32(1);mflr 0;stw 0,36(1);stw 31,28(1);mr 31,3
lis 12,32894;ori 12,12,48928;mtctr 12;bctrl
addi 3,31,168
lis 4,0x1357;addi 4,4,0x2468
lis 12,32862;ori 12,12,33640;mtctr 12;bctrl
cmpwi 3,0;beq finish
mr 3,31
lis 4,0x1357;addi 4,4,0x2468
li 5,1
lis 12,32894;ori 12,12,48928;mtctr 12;bctrl
finish:lwz 31,28(1);lwz 0,36(1);mtlr 0;addi 1,1,32;blr