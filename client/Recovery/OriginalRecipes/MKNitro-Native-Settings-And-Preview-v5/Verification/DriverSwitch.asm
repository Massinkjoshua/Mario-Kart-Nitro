8082fb78 stwu r1, -0x20(r1)
8082fb7c mflr r0
8082fb80 stw r0, 0x24(r1)
8082fb84 stw r31, 0x1c(r1)
8082fb88 lis r31, -0x7f75
8082fb8c addi r31, r31, -0x3680
8082fb90 stw r30, 0x18(r1)
8082fb94 mr r30, r5
8082fb98 stw r29, 0x14(r1)
8082fb9c mr r29, r3
8082fba0 stw r28, 0x10(r1)
8082fba4 mr r28, r4
8082fba8 lwz r0, 8(r3)
8082fbac cmpw r5, r0
8082fbb0 beq 0x8082fc60
8082fbb4 cmplwi r5, 1
8082fbb8 bgt 0x8082fc10
8082fbbc lwz r4, 0xc(r3)
8082fbc0 cmpwi r4, 0
8082fbc4 beq 0x8082fbe4
8082fbc8 lwz r3, 4(r3)
8082fbcc lwz r0, 0x28(r3)
8082fbd0 cmplw r0, r4
8082fbd4 beq 0x8082fbe4
8082fbd8 li r5, 1
8082fbdc bl 0x8055f7d8
8082fbe0 b 0x8082fbec
8082fbe4 cmpwi r4, 0
8082fbe8 beq 0x8082feec
8082fbec cmpwi r28, 0
8082fbf0 blt 0x8082fc60
8082fbf4 lis r3, -0x7f64
8082fbf8 clrlwi r4, r28, 0x18
8082fbfc lwz r3, 0x1988(r3)
8082fc00 li r5, 0
8082fc04 lwz r3, 0x18(r3)
8082fc08 bl 0x808333ac
8082fc0c b 0x8082fc60
8082fc10 lwz r4, 0x10(r3)
8082fc14 cmpwi r4, 0
8082fc18 beq 0x8082fc38
8082fc1c lwz r3, 4(r3)
8082fc20 lwz r0, 0x28(r3)
8082fc24 cmplw r0, r4
8082fc28 beq 0x8082fc38
8082fc2c li r5, 1
8082fc30 bl 0x8055f7d8
8082fc34 b 0x8082fc40
8082fc38 cmpwi r4, 0
8082fc3c beq 0x8082feec
8082fc40 cmpwi r28, 0
8082fc44 blt 0x8082fc60
8082fc48 lis r3, -0x7f64
8082fc4c clrlwi r4, r28, 0x18
8082fc50 lwz r3, 0x1988(r3)
8082fc54 li r5, 1
8082fc58 lwz r3, 0x18(r3)
8082fc5c bl 0x808333ac
8082fc60 addi r0, r30, -2
8082fc64 cmplwi r0, 1
8082fc68 ble 0x8082fdf4
8082fc6c cmpwi r30, 0
8082fc70 beq 0x8082fc80
8082fc74 cmpwi r30, 1
8082fc78 beq 0x8082fd4c
8082fc7c b 0x8082fee8
8082fc80 lwz r0, 8(r29)
8082fc84 cmpw r30, r0
8082fc88 beq 0x8082feec
8082fc8c lwz r0, 0xc(r29)
8082fc90 cmpwi r0, 0
8082fc94 bne 0x8082fc9c
8082fc98 b 0x8082feec
8082fc9c li r28, 0
8082fca0 lwz r3, 4(r29)
8082fca4 clrlwi r4, r28, 0x10
8082fca8 lwz r3, 0x28(r3)
8082fcac bl 0x80557234
8082fcb0 lwz r0, 4(r3)
8082fcb4 cmpwi r0, -1
8082fcb8 beq 0x8082fd3c
8082fcbc lwz r3, 4(r29)
8082fcc0 lwz r3, 0x28(r3)
8082fcc4 cmpwi r3, 0
8082fcc8 beq 0x8082fd24
8082fccc li r4, 0
8082fcd0 bl 0x80557360
8082fcd4 cmpwi r3, 0
8082fcd8 beq 0x8082fd24
8082fcdc cmpwi r28, 0
8082fce0 bne 0x8082fd24
8082fce4 lwz r0, 8(r29)
8082fce8 cmpwi r0, 1
8082fcec bne 0x8082fd24
8082fcf0 lwz r3, 4(r29)
8082fcf4 li r4, 0
8082fcf8 lfs f1, 0x14(r31)
8082fcfc lwz r3, 0x28(r3)
8082fd00 bl 0x8055586c
8082fd04 lwz r3, 4(r29)
8082fd08 clrlwi r4, r28, 0x10
8082fd0c lfs f1, 4(r31)
8082fd10 li r5, 1
8082fd14 lwz r3, 0x28(r3)
8082fd18 lfs f2, 0x10(r31)
8082fd1c bl 0x80557684
8082fd20 b 0x8082fd3c
8082fd24 lwz r3, 4(r29)
8082fd28 clrlwi r4, r28, 0x10
8082fd2c lfs f1, 4(r31)
8082fd30 lwz r3, 0x28(r3)
8082fd34 lfs f2, 0x10(r31)
8082fd38 bl 0x805573cc
8082fd3c addi r28, r28, 1
8082fd40 cmpwi r28, 3
8082fd44 blt 0x8082fca0
8082fd48 b 0x8082fee8
8082fd4c lwz r0, 0xc(r29)
8082fd50 cmpwi r0, 0
8082fd54 beq 0x8082feec
8082fd58 li r28, 3
8082fd5c lwz r3, 4(r29)
8082fd60 clrlwi r4, r28, 0x10
8082fd64 lwz r3, 0x28(r3)
8082fd68 bl 0x80557234
8082fd6c lwz r0, 4(r3)
8082fd70 cmpwi r0, -1
8082fd74 beq 0x8082fde4
8082fd78 lwz r3, 4(r29)
8082fd7c lwz r3, 0x28(r3)
8082fd80 cmpwi r3, 0
8082fd84 beq 0x8082fdcc
8082fd88 li r4, 0
8082fd8c bl 0x80557360
8082fd90 cmpwi r3, 0
8082fd94 beq 0x8082fdcc
8082fd98 cmpwi r28, 3
8082fd9c bne 0x8082fdcc
8082fda0 lwz r0, 8(r29)
8082fda4 cmpwi r0, 0
8082fda8 bne 0x8082fdcc
8082fdac lwz r3, 4(r29)
8082fdb0 clrlwi r4, r28, 0x10
8082fdb4 lfs f1, 4(r31)
8082fdb8 li r5, 1
8082fdbc lwz r3, 0x28(r3)
8082fdc0 lfs f2, 0x10(r31)
8082fdc4 bl 0x80557684
8082fdc8 b 0x8082fde4
8082fdcc lwz r3, 4(r29)
8082fdd0 clrlwi r4, r28, 0x10
8082fdd4 lfs f1, 4(r31)
8082fdd8 lwz r3, 0x28(r3)
8082fddc lfs f2, 0x10(r31)
8082fde0 bl 0x805573cc
8082fde4 addi r28, r28, 1
8082fde8 cmpwi r28, 6
8082fdec blt 0x8082fd5c
8082fdf0 b 0x8082fee8
8082fdf4 lwz r0, 0x10(r29)
8082fdf8 cmpwi r0, 0
8082fdfc beq 0x8082feec
8082fe00 lwz r3, 0x14(r29)
8082fe04 cmpwi r3, 0x12
8082fe08 bge 0x8082fe14
8082fe0c li r28, 1
8082fe10 b 0x8082fe4c
8082fe14 addi r0, r3, -0x22
8082fe18 cmplwi r0, 1
8082fe1c ble 0x8082fe40
8082fe20 cmpwi r3, 0x16
8082fe24 beq 0x8082fe40
8082fe28 cmpwi r3, 0x1f
8082fe2c beq 0x8082fe40
8082fe30 cmpwi r3, 0x1a
8082fe34 beq 0x8082fe40
8082fe38 cmpwi r3, 0x1d
8082fe3c bne 0x8082fe48
8082fe40 li r28, 3
8082fe44 b 0x8082fe4c
8082fe48 li r28, 2
8082fe4c lwz r3, 4(r29)
8082fe50 mr r4, r28
8082fe54 lwz r3, 0x28(r3)
8082fe58 bl 0x80557234
8082fe5c lwz r0, 4(r3)
8082fe60 cmpwi r0, -1
8082fe64 beq 0x8082feb4
8082fe68 lwz r3, 4(r29)
8082fe6c li r4, 0
8082fe70 lwz r3, 0x28(r3)
8082fe74 bl 0x80557360
8082fe78 cmpwi r3, 0
8082fe7c beq 0x8082fe9c
8082fe80 lwz r3, 4(r29)
8082fe84 li r4, 0
8082fe88 lwz r3, 0x28(r3)
8082fe8c bl 0x80557340
8082fe90 lhz r0, 8(r3)
8082fe94 cmpw r28, r0
8082fe98 beq 0x8082feb4
8082fe9c lwz r3, 4(r29)
8082fea0 mr r4, r28
8082fea4 lfs f1, 4(r31)
8082fea8 lwz r3, 0x28(r3)
8082feac lfs f2, 0x10(r31)
8082feb0 bl 0x805573cc
8082feb4 lwz r3, 4(r29)
8082feb8 li r4, 0
8082febc lwz r3, 0x28(r3)
8082fec0 bl 0x80557234
8082fec4 lwz r0, 4(r3)
8082fec8 cmpwi r0, -1
8082fecc beq 0x8082fee8
8082fed0 lwz r3, 4(r29)
8082fed4 li r4, 0
8082fed8 lfs f1, 4(r31)
8082fedc lwz r3, 0x28(r3)
8082fee0 lfs f2, 0x10(r31)
8082fee4 bl 0x805573cc
8082fee8 stw r30, 8(r29)
8082feec lwz r0, 0x24(r1)
8082fef0 lwz r31, 0x1c(r1)
8082fef4 lwz r30, 0x18(r1)
8082fef8 lwz r29, 0x14(r1)
8082fefc lwz r28, 0x10(r1)
8082ff00 mtlr r0
8082ff04 addi r1, r1, 0x20
8082ff08 blr 