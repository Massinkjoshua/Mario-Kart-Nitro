805f3cf8 stwu r1, -0x40(r1)
805f3cfc mflr r0
805f3d00 lis r4, -0x7f64
805f3d04 stw r0, 0x44(r1)
805f3d08 li r0, 1
805f3d0c stw r31, 0x3c(r1)
805f3d10 stw r30, 0x38(r1)
805f3d14 mr r30, r3
805f3d18 stw r29, 0x34(r1)
805f3d1c stw r28, 0x30(r1)
805f3d20 stb r0, 0x80(r3)
805f3d24 lwz r3, 0x1e38(r4)
805f3d28 lwz r3, 0(r3)
805f3d2c lwz r31, 0x204(r3)
805f3d30 cmpwi r31, 0
805f3d34 bne 0x805f3d40
805f3d38 li r31, 0
805f3d3c b 0x805f3d94
805f3d40 lis r29, -0x7f64
805f3d44 addi r29, r29, 0x1ca8
805f3d48 beq 0x805f3d90
805f3d4c lwz r12, 0(r31)
805f3d50 mr r3, r31
805f3d54 lwz r12, 0x60(r12)
805f3d58 mtctr r12
805f3d5c bctrl 
805f3d60 b 0x805f3d78
805f3d64 cmplw r3, r29
805f3d68 bne 0x805f3d74
805f3d6c li r0, 1
805f3d70 b 0x805f3d84
805f3d74 lwz r3, 0(r3)
805f3d78 cmpwi r3, 0
805f3d7c bne 0x805f3d64
805f3d80 li r0, 0
805f3d84 cmpwi r0, 0
805f3d88 beq 0x805f3d90
805f3d8c b 0x805f3d94
805f3d90 li r31, 0
805f3d94 cmpwi r31, 0
805f3d98 beq 0x805f4084
805f3d9c lbz r4, 0x174(r30)
805f3da0 mr r3, r31
805f3da4 li r5, 0
805f3da8 li r6, 0
805f3dac bl 0x805f59ac
805f3db0 lbz r4, 0x174(r30)
805f3db4 mulli r0, r4, 0xc
805f3db8 add r3, r31, r0
805f3dbc lbz r0, 0x5c(r3)
805f3dc0 cmpwi r0, 0
805f3dc4 beq 0x805f3f40
805f3dc8 lis r3, -0x7f64
805f3dcc lwz r3, 0x1e38(r3)
805f3dd0 lwz r3, 0(r3)
805f3dd4 lwz r0, 0(r3)
805f3dd8 cmpwi r0, 0x92
805f3ddc blt 0x805f3de8
805f3de0 cmpwi r0, 0x93
805f3de4 ble 0x805f3dfc
805f3de8 cmpwi r0, 0x90
805f3dec beq 0x805f3dfc
805f3df0 cmpwi r0, 0x91
805f3df4 beq 0x805f3e08
805f3df8 b 0x805f3e24
805f3dfc li r0, 1
805f3e00 stb r0, 0x80(r30)
805f3e04 b 0x805f3e3c
805f3e08 mr r3, r31
805f3e0c li r5, 0
805f3e10 li r6, 1
805f3e14 bl 0x805f59ac
805f3e18 li r0, 0
805f3e1c stb r0, 0x80(r30)
805f3e20 b 0x805f3e3c
805f3e24 mr r3, r31
805f3e28 li r5, 1
805f3e2c li r6, 1
805f3e30 bl 0x805f59ac
805f3e34 li r0, 0
805f3e38 stb r0, 0x80(r30)
805f3e3c lis r3, -0x7f64
805f3e40 lwz r3, 0x1e38(r3)
805f3e44 lwz r3, 0(r3)
805f3e48 lwz r28, 0x204(r3)
805f3e4c cmpwi r28, 0
805f3e50 bne 0x805f3e5c
805f3e54 li r28, 0
805f3e58 b 0x805f3eb0
805f3e5c lis r29, -0x7f64
805f3e60 addi r29, r29, 0x1ca8
805f3e64 beq 0x805f3eac
805f3e68 lwz r12, 0(r28)
805f3e6c mr r3, r28
805f3e70 lwz r12, 0x60(r12)
805f3e74 mtctr r12
805f3e78 bctrl 
805f3e7c b 0x805f3e94
805f3e80 cmplw r3, r29
805f3e84 bne 0x805f3e90
805f3e88 li r0, 1
805f3e8c b 0x805f3ea0
805f3e90 lwz r3, 0(r3)
805f3e94 cmpwi r3, 0
805f3e98 bne 0x805f3e80
805f3e9c li r0, 0
805f3ea0 cmpwi r0, 0
805f3ea4 beq 0x805f3eac
805f3ea8 b 0x805f3eb0
805f3eac li r28, 0
805f3eb0 lbz r4, 0x174(r30)
805f3eb4 mr r3, r28
805f3eb8 mulli r0, r4, 0xc
805f3ebc add r5, r28, r0
805f3ec0 lwz r28, 0x58(r5)
805f3ec4 mr r5, r28
805f3ec8 bl 0x805f5958
805f3ecc lis r3, -0x7f64
805f3ed0 lwz r3, 0x1988(r3)
805f3ed4 cmpwi r3, 0
805f3ed8 beq 0x805f3f40
805f3edc lwz r5, 0x14(r3)
805f3ee0 cmpwi r5, 0
805f3ee4 beq 0x805f3f40
805f3ee8 lbz r4, 0x174(r30)
805f3eec mulli r0, r4, 0xc
805f3ef0 add r3, r5, r0
805f3ef4 lwz r3, 0x18(r3)
805f3ef8 cmpwi r3, 0
805f3efc beq 0x805f3f08
805f3f00 lwz r0, 8(r3)
805f3f04 b 0x805f3f0c
805f3f08 li r0, 0
805f3f0c cmpwi r0, 3
805f3f10 beq 0x805f3f40
805f3f14 mulli r0, r4, 0xc
805f3f18 add r3, r5, r0
805f3f1c lwz r5, 0x18(r3)
805f3f20 cmpwi r5, 0
805f3f24 beq 0x805f3f40
805f3f28 cmpwi r28, -1
805f3f2c beq 0x805f3f34
805f3f30 stw r28, 0x14(r5)
805f3f34 lwz r3, 0x18(r3)
805f3f38 li r5, 2
805f3f3c bl 0x8082fb78
805f3f40 lbz r4, 0x174(r30)
805f3f44 mr r3, r31
805f3f48 bl 0x805f5a4c
805f3f4c cmpwi r3, 0
805f3f50 mr r28, r3
805f3f54 beq 0x805f4084
805f3f58 lis r4, -0x7f77
805f3f5c addi r3, r30, 0xa8
805f3f60 addi r4, r4, 0x5fa4
805f3f64 addi r4, r4, 0x93
805f3f68 bl 0x805e8368
805f3f6c cmpwi r3, 0
805f3f70 mr r30, r3
805f3f74 bne 0x805f3f80
805f3f78 li r30, 0
805f3f7c b 0x805f3fd0
805f3f80 lis r29, -0x7fc8
805f3f84 addi r29, r29, 0x6178
805f3f88 beq 0x805f3fcc
805f3f8c lwz r12, 0(r3)
805f3f90 lwz r12, 0xc(r12)
805f3f94 mtctr r12
805f3f98 bctrl 
805f3f9c b 0x805f3fb4
805f3fa0 cmplw r3, r29
805f3fa4 bne 0x805f3fb0
805f3fa8 li r0, 1
805f3fac b 0x805f3fc0
805f3fb0 lwz r3, 0(r3)
805f3fb4 cmpwi r3, 0
805f3fb8 bne 0x805f3fa0
805f3fbc li r0, 0
805f3fc0 cmpwi r0, 0
805f3fc4 beq 0x805f3fcc
805f3fc8 b 0x805f3fd0
805f3fcc li r30, 0
805f3fd0 mr r4, r28
805f3fd4 addi r3, r1, 8
805f3fd8 bl 0x80082400
805f3fdc lwz r0, 0x20(r1)
805f3fe0 li r4, 0
805f3fe4 stw r4, 0xc(r1)
805f3fe8 mr r3, r30
805f3fec rlwinm r0, r0, 0, 0x13, 0x10
805f3ff0 stw r0, 0x20(r1)
805f3ff4 sth r4, 0x1e(r1)
805f3ff8 lwz r12, 0(r30)
805f3ffc lwz r12, 0x68(r12)
805f4000 mtctr r12
805f4004 bctrl 
805f4008 lwz r0, 0x3c(r3)
805f400c mr r29, r3
805f4010 rlwinm. r0, r0, 4, 0x1c, 0x1f
805f4014 bne 0x805f4034
805f4018 lis r3, -0x7f74
805f401c lis r5, -0x7f74
805f4020 addi r3, r3, -0x640c
805f4024 li r4, 0x88
805f4028 addi r5, r5, -0x6440
805f402c crclr cr1eq
805f4030 bl 0x80025fb0
805f4034 mr r3, r29
805f4038 bl 0x800809a0
805f403c lwz r0, 8(r1)
805f4040 stw r0, 0(r3)
805f4044 lwz r0, 0xc(r1)
805f4048 stw r0, 4(r3)
805f404c lhz r0, 0x10(r1)
805f4050 sth r0, 8(r3)
805f4054 lhz r0, 0x12(r1)
805f4058 sth r0, 0xa(r3)
805f405c lfs f0, 0x14(r1)
805f4060 stfs f0, 0xc(r3)
805f4064 lfs f0, 0x18(r1)
805f4068 stfs f0, 0x10(r3)
805f406c lhz r0, 0x1c(r1)
805f4070 sth r0, 0x14(r3)
805f4074 lhz r0, 0x1e(r1)
805f4078 sth r0, 0x16(r3)
805f407c lwz r0, 0x20(r1)
805f4080 stw r0, 0x18(r3)
805f4084 lwz r0, 0x44(r1)
805f4088 lwz r31, 0x3c(r1)
805f408c lwz r30, 0x38(r1)
805f4090 lwz r29, 0x34(r1)
805f4094 lwz r28, 0x30(r1)
805f4098 mtlr r0
805f409c addi r1, r1, 0x40
805f40a0 blr 