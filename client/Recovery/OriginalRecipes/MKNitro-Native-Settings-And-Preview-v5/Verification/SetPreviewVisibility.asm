805f59ac stwu r1, -0x20(r1)
805f59b0 mflr r0
805f59b4 stw r0, 0x24(r1)
805f59b8 stw r31, 0x1c(r1)
805f59bc stw r30, 0x18(r1)
805f59c0 mr r30, r6
805f59c4 stw r29, 0x14(r1)
805f59c8 mr r29, r4
805f59cc stw r28, 0x10(r1)
805f59d0 mr r28, r3
805f59d4 lbz r0, 0x90(r3)
805f59d8 cmpwi r0, 0
805f59dc bne 0x805f5a10
805f59e0 lis r31, -0x7f64
805f59e4 lwz r3, 0x1988(r31)
805f59e8 bl 0x8059e5a4
805f59ec mulli r0, r29, 0xc
805f59f0 add r3, r28, r0
805f59f4 lbz r0, 0x5c(r3)
805f59f8 cmpwi r0, 0
805f59fc beq 0x805f5a10
805f5a00 lwz r3, 0x1988(r31)
805f5a04 mr r4, r29
805f5a08 mr r5, r30
805f5a0c bl 0x8059e5bc
805f5a10 lwz r0, 0x24(r1)
805f5a14 lwz r31, 0x1c(r1)
805f5a18 lwz r30, 0x18(r1)
805f5a1c lwz r29, 0x14(r1)
805f5a20 lwz r28, 0x10(r1)
805f5a24 mtlr r0
805f5a28 addi r1, r1, 0x20
805f5a2c blr 