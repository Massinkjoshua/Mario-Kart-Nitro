stwu 1,-48(1)
mflr 0
stw 0,52(1)
li 0,1
stb 0,1608(31)
lwz 0,1296(31)
cmpwi 0,0
beq finish
lis 0,28009; ori 0,0,26880
stw 0,8(1)
lis 0,0; ori 0,0,0
stw 0,12(1)
lis 0,0; ori 0,0,0
stw 0,16(1)
lis 0,0; ori 0,0,0
stw 0,20(1)
addi 3,31,1276
addi 4,1,8
lis 12,32862; ori 12,12,33640
mtctr 12
bctrl
cmpwi 3,0
beq next0
lis 0,49798; ori 0,0,0
stw 0,44(3)
lis 0,49638; ori 0,0,3784
stw 0,48(3)
lis 0,0; ori 0,0,0
stw 0,52(3)
lis 0,0; ori 0,0,0
stw 0,56(3)
lis 0,0; ori 0,0,0
stw 0,60(3)
lis 0,0; ori 0,0,0
stw 0,64(3)
lis 0,16128; ori 0,0,0
stw 0,68(3)
lis 0,16128; ori 0,0,0
stw 0,72(3)
lis 0,17076; ori 0,0,0
stw 0,76(3)
lis 0,17076; ori 0,0,0
stw 0,80(3)
next0:
lis 0,28265; ori 0,0,29810
stw 0,8(1)
lis 0,28511; ori 0,0,28009
stw 0,12(1)
lis 0,26975; ori 0,0,26226
stw 0,16(1)
lis 0,24941; ori 0,0,25856
stw 0,20(1)
addi 3,31,1276
addi 4,1,8
lis 12,32862; ori 12,12,33640
mtctr 12
bctrl
cmpwi 3,0
beq next1
lis 0,0; ori 0,0,0
stw 0,44(3)
lis 0,16948; ori 0,0,0
stw 0,48(3)
lis 0,0; ori 0,0,0
stw 0,52(3)
lis 0,0; ori 0,0,0
stw 0,56(3)
lis 0,0; ori 0,0,0
stw 0,60(3)
lis 0,0; ori 0,0,0
stw 0,64(3)
lis 0,16256; ori 0,0,0
stw 0,68(3)
lis 0,16256; ori 0,0,0
stw 0,72(3)
lis 0,17152; ori 0,0,0
stw 0,76(3)
lis 0,17156; ori 0,0,0
stw 0,80(3)
next1:
finish:
lwz 0,52(1)
mtlr 0
addi 1,1,48
lwz 0,20(1)
blr
