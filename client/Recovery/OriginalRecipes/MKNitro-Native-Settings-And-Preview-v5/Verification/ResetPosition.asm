8063d3cc lwz r6, 0x64(r3)
8063d3d0 lwz r7, 8(r6)
8063d3d4 cmpwi r7, 0
8063d3d8 beq 0x8063d464
8063d3dc lfs f1, 4(r3)
8063d3e0 lfs f0, 0x28(r7)
8063d3e4 lbz r4, 0x18(r3)
8063d3e8 fmuls f1, f1, f0
8063d3ec lfs f0, 0x1c(r7)
8063d3f0 lfs f5, 8(r3)
8063d3f4 addi r5, r4, 1
8063d3f8 lfs f3, 0xc(r3)
8063d3fc fadds f0, f0, f1
8063d400 lfs f2, 0x10(r3)
8063d404 stfs f0, 0x1c(r3)
8063d408 lfs f1, 0x14(r3)
8063d40c lfs f4, 0x2c(r7)
8063d410 lfs f0, 0x20(r7)
8063d414 fmuls f4, f5, f4
8063d418 fadds f0, f0, f4
8063d41c stfs f0, 0x20(r3)
8063d420 lfs f0, 0x24(r7)
8063d424 fadds f0, f3, f0
8063d428 stfs f0, 0x24(r3)
8063d42c lfs f0, 0x28(r7)
8063d430 fmuls f0, f2, f0
8063d434 stfs f0, 0x28(r3)
8063d438 lfs f0, 0x2c(r7)
8063d43c fmuls f0, f1, f0
8063d440 stfs f0, 0x2c(r3)
8063d444 lwz r4, 8(r6)
8063d448 lbz r4, 0x30(r4)
8063d44c addi r0, r4, 1
8063d450 mullw r4, r5, r0
8063d454 addi r0, r4, -1
8063d458 rlwinm r0, r0, 0x18, 0x18, 0x1f
8063d45c stb r0, 0x30(r3)
8063d460 b 0x8063d494
8063d464 lfs f4, 4(r3)
8063d468 lfs f3, 8(r3)
8063d46c lfs f2, 0xc(r3)
8063d470 lfs f1, 0x10(r3)
8063d474 lfs f0, 0x14(r3)
8063d478 lbz r0, 0x18(r3)
8063d47c stfs f4, 0x1c(r3)
8063d480 stfs f3, 0x20(r3)
8063d484 stfs f2, 0x24(r3)
8063d488 stfs f1, 0x28(r3)
8063d48c stfs f0, 0x2c(r3)
8063d490 stb r0, 0x30(r3)
8063d494 lwz r4, 0x64(r3)
8063d498 lwz r4, 8(r4)
8063d49c cmpwi r4, 0
8063d4a0 beq 0x8063d4d8
8063d4a4 lfs f2, 0x34(r3)
8063d4a8 lfs f0, 0x28(r4)
8063d4ac lfs f1, 0x1c(r3)
8063d4b0 fmuls f3, f2, f0
8063d4b4 lfs f2, 0x38(r3)
8063d4b8 lfs f0, 0x20(r3)
8063d4bc fadds f1, f1, f3
8063d4c0 stfs f1, 0x4c(r3)
8063d4c4 lfs f1, 0x2c(r4)
8063d4c8 fmuls f1, f2, f1
8063d4cc fadds f0, f0, f1
8063d4d0 stfs f0, 0x50(r3)
8063d4d4 b 0x8063d4f8
8063d4d8 lfs f3, 0x1c(r3)
8063d4dc lfs f2, 0x34(r3)
8063d4e0 lfs f1, 0x20(r3)
8063d4e4 lfs f0, 0x38(r3)
8063d4e8 fadds f2, f3, f2
8063d4ec fadds f0, f1, f0
8063d4f0 stfs f2, 0x4c(r3)
8063d4f4 stfs f0, 0x50(r3)
8063d4f8 lbz r5, 0x30(r3)
8063d4fc lbz r4, 0x48(r3)
8063d500 addi r5, r5, 1
8063d504 lfs f1, 0x24(r3)
8063d508 addi r0, r4, 1
8063d50c lfs f0, 0x3c(r3)
8063d510 mullw r4, r5, r0
8063d514 lfs f3, 0x28(r3)
8063d518 fadds f4, f1, f0
8063d51c lfs f2, 0x40(r3)
8063d520 lfs f1, 0x2c(r3)
8063d524 lfs f0, 0x44(r3)
8063d528 fmuls f2, f3, f2
8063d52c addi r0, r4, -1
8063d530 fmuls f0, f1, f0
8063d534 rlwinm r0, r0, 0x18, 0x18, 0x1f
8063d538 stfs f4, 0x54(r3)
8063d53c stfs f2, 0x58(r3)
8063d540 stfs f0, 0x5c(r3)
8063d544 stb r0, 0x60(r3)
8063d548 addi r3, r3, 0x68
8063d54c b 0x805c2a5c
8063d550 lwz r4, 0x64(r3)
8063d554 lwz r4, 8(r4)
8063d558 cmpwi r4, 0
8063d55c beq 0x8063d594
8063d560 lfs f2, 0x34(r3)
8063d564 lfs f0, 0x28(r4)
8063d568 lfs f1, 0x1c(r3)
8063d56c fmuls f3, f2, f0
8063d570 lfs f2, 0x38(r3)
8063d574 lfs f0, 0x20(r3)
8063d578 fadds f1, f1, f3
8063d57c stfs f1, 0x4c(r3)
8063d580 lfs f1, 0x2c(r4)
8063d584 fmuls f1, f2, f1
8063d588 fadds f0, f0, f1
8063d58c stfs f0, 0x50(r3)
8063d590 b 0x8063d5b4
8063d594 lfs f3, 0x1c(r3)
8063d598 lfs f2, 0x34(r3)
8063d59c lfs f1, 0x20(r3)
8063d5a0 lfs f0, 0x38(r3)
8063d5a4 fadds f2, f3, f2
8063d5a8 fadds f0, f1, f0
8063d5ac stfs f2, 0x4c(r3)
8063d5b0 stfs f0, 0x50(r3)
8063d5b4 lbz r5, 0x30(r3)
8063d5b8 lbz r4, 0x48(r3)
8063d5bc addi r5, r5, 1
8063d5c0 lfs f1, 0x24(r3)
8063d5c4 addi r0, r4, 1
8063d5c8 lfs f0, 0x3c(r3)
8063d5cc mullw r4, r5, r0
8063d5d0 lfs f3, 0x28(r3)
8063d5d4 fadds f4, f1, f0
8063d5d8 lfs f2, 0x40(r3)
8063d5dc lfs f1, 0x2c(r3)
8063d5e0 lfs f0, 0x44(r3)
8063d5e4 fmuls f2, f3, f2
8063d5e8 addi r0, r4, -1
8063d5ec fmuls f0, f1, f0
8063d5f0 rlwinm r0, r0, 0x18, 0x18, 0x1f
8063d5f4 stfs f4, 0x54(r3)
8063d5f8 stfs f2, 0x58(r3)
8063d5fc stfs f0, 0x5c(r3)
8063d600 stb r0, 0x60(r3)
8063d604 blr 