
 stwu 1,-32(1); mflr 0; stw 0,36(1); stw 31,28(1); mr 31,3
 bl original_entry
 lwz 0,1732(31); cmplwi 0,17; bge finish
 mulli 0,0,20
 lis 12,0x1357; addi 12,12,0x2468; add 12,12,0
 lbz 6,8(12); lbz 7,16(12)
 cmplwi 6,8; bgt finish; cmplwi 7,5; bgt finish
 add 0,6,7; slwi 0,0,6
 lis 9,0x1357; addi 9,9,0x2468; add 9,9,0
 lwz 10,0(9); addi 9,9,4
 addi 3,31,1736; li 4,0
 radio_loop:
 cmplw 4,6; bge scroll_start
 lwz 11,0(9); stw 11,8(3); stw 10,16(3); stw 10,20(3)
 addi 3,3,664; addi 9,9,4; addi 4,4,1; b radio_loop
 scroll_start:
 addi 3,31,7088; li 4,0
 scroll_loop:
 cmplw 4,7; bge rebuild
 lwz 11,0(9); stw 11,8(3); stw 10,16(3); stw 10,20(3)
 addi 3,3,1480; addi 9,9,4; addi 4,4,1; b scroll_loop
 rebuild:
 addi 3,31,36
 lis 12,0x805c; ori 12,12,0x2a5c; mtctr 12; bctrl
 finish:
 lwz 31,28(1); lwz 0,36(1); mtlr 0; addi 1,1,32; blr
 original_entry:
 stwu 1,-80(1); b 0
