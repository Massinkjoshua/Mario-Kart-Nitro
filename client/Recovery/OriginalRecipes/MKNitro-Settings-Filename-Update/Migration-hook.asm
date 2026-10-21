stwu 1,-128(1);mflr 0;stw 0,132(1);stw 31,124(1);stw 30,120(1);stw 29,116(1)
 mr 31,3;mr 30,4;mr 29,5
 bctrl
 cmpwi 3,0;bne finish
 addi 7,1,8;li 6,0;li 8,0
 copy_path:cmplwi 6,64;bge no_legacy
 lbzx 9,30,6;stbx 9,7,6
 cmpwi 9,47;bne no_slash
 add 8,7,6;addi 8,8,1
 no_slash:cmpwi 9,0;beq copied
 addi 6,6,1;b copy_path
 copied:cmpwi 8,0;beq no_legacy
 subf 10,7,8;cmplwi 10,45;bgt no_legacy
 li 9,82;stb 9,0(8);li 9,82;stb 9,1(8);li 9,71;stb 9,2(8);li 9,97;stb 9,3(8);li 9,109;stb 9,4(8);li 9,101;stb 9,5(8);li 9,83;stb 9,6(8);li 9,101;stb 9,7(8);li 9,116;stb 9,8(8);li 9,116;stb 9,9(8);li 9,105;stb 9,10(8);li 9,110;stb 9,11(8);li 9,103;stb 9,12(8);li 9,115;stb 9,13(8);li 9,46;stb 9,14(8);li 9,112;stb 9,15(8);li 9,117;stb 9,16(8);li 9,108;stb 9,17(8);li 9,0;stb 9,18(8)
 mr 3,31;addi 4,1,8;mr 5,29
 lwz 12,0(31);lwz 12,8(12);mtctr 12;bctrl
 b finish
 no_legacy:li 3,0
 finish:lwz 29,116(1);lwz 30,120(1);lwz 31,124(1);lwz 0,132(1);mtlr 0;addi 1,1,128;blr