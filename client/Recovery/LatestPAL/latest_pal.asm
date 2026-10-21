# Reconstructed editable PAL assembly, Mario Kart Nitro, 16 October 2026.
# Original source was not recovered for these appended functions.
# Native and core calls are linked by the typed Kamek relocations in patch.json.
# Input register r28 is owned by the original caller of gate_kart_custom_effects.


# gate_kart_custom_effects
L_c69e0:
    stwu 1, -0x10(1)
L_c69e4:
    mflr 0
L_c69e8:
    stw 0, 0x14(1)
L_c69ec:
    stw 31, 0xc(1)
L_c69f0:
    li 31, 0
L_c69f4:
    lwz 0, 0x124(28)
L_c69f8:
    cmpwi 0, 0
L_c69fc:
    bne L_c6a10
L_c6a00:
    bl L_c6a00
L_c6a04:
    cmpwi 3, 0
L_c6a08:
    beq L_c6a10
L_c6a0c:
    li 31, 1
L_c6a10:
    mr 3, 31
L_c6a14:
    lwz 31, 0xc(1)
L_c6a18:
    lwz 0, 0x14(1)
L_c6a1c:
    mtlr 0
L_c6a20:
    addi 1, 1, 0x10
L_c6a24:
    blr 

# copy_info_and_enable_umts_feather
L_c6a28:
    stwu 1, -0x10(1)
L_c6a2c:
    mflr 0
L_c6a30:
    stw 0, 0x14(1)
L_c6a34:
    stw 31, 0xc(1)
L_c6a38:
    mr 31, 5
L_c6a3c:
    stw 30, 8(1)
L_c6a40:
    mr 30, 3
L_c6a44:
    bl L_c6a44
L_c6a48:
    cmplwi 31, 0x44
L_c6a4c:
    bne L_c6a5c
L_c6a50:
    li 0, 1
L_c6a54:
    stb 0, 0x16(30)
L_c6a58:
    stb 0, 0x17(30)
L_c6a5c:
    mr 3, 30
L_c6a60:
    lwz 31, 0xc(1)
L_c6a64:
    lwz 30, 8(1)
L_c6a68:
    lwz 0, 0x14(1)
L_c6a6c:
    mtlr 0
L_c6a70:
    addi 1, 1, 0x10
L_c6a74:
    blr 

# prefix_matches
L_c6a78:
    b L_c6aa4
L_c6a7c:
    lbz 5, 0(3)
L_c6a80:
    addi 3, 3, 1
L_c6a84:
    lbz 0, 0(4)
L_c6a88:
    addi 4, 4, 1
L_c6a8c:
    extsb 5, 5
L_c6a90:
    extsb 0, 0
L_c6a94:
    cmpw 5, 0
L_c6a98:
    beq L_c6aa4
L_c6a9c:
    li 3, 0
L_c6aa0:
    blr 
L_c6aa4:
    lbz 0, 0(4)
L_c6aa8:
    extsb. 0, 0
L_c6aac:
    bne L_c6a7c
L_c6ab0:
    li 3, 1
L_c6ab4:
    blr 

# apply_skin_drift_colour
L_c6ab8:
    stwu 1, -0x20(1)
L_c6abc:
    mflr 0
L_c6ac0:
    cmpwi 3, 0
L_c6ac4:
    stw 0, 0x24(1)
L_c6ac8:
    stmw 26, 8(1)
L_c6acc:
    lis 27, 0
L_c6ad0:
    mr 28, 3
L_c6ad4:
    addi 27, 27, 0
L_c6ad8:
    beq L_c6c38
L_c6adc:
    addi 29, 3, 4
L_c6ae0:
    mr 3, 29
L_c6ae4:
    addi 4, 27, 0x1cb0
L_c6ae8:
    bl L_c6a78
L_c6aec:
    mr 30, 3
L_c6af0:
    mr 3, 29
L_c6af4:
    addi 4, 27, 0x1cc0
L_c6af8:
    bl L_c6a78
L_c6afc:
    mr 31, 3
L_c6b00:
    mr 3, 29
L_c6b04:
    addi 4, 27, 0x1cd0
L_c6b08:
    bl L_c6a78
L_c6b0c:
    cmpwi 30, 0
L_c6b10:
    bne L_c6b24
L_c6b14:
    cmpwi 31, 0
L_c6b18:
    bne L_c6b24
L_c6b1c:
    cmpwi 3, 0
L_c6b20:
    beq L_c6c38
L_c6b24:
    lwz 3, 0x24(28)
L_c6b28:
    addi 0, 3, -2
L_c6b2c:
    cmplwi 0, 0xb
L_c6b30:
    bgt L_c6c38
L_c6b34:
    lis 3, -0x7f64
L_c6b38:
    lwz 4, -0x28d8(3)
L_c6b3c:
    clrlwi 3, 0, 0x18
L_c6b40:
    cmpwi 4, 0
L_c6b44:
    beq L_c6c38
L_c6b48:
    lbz 0, 0x24(4)
L_c6b4c:
    cmplw 3, 0
L_c6b50:
    blt L_c6b58
L_c6b54:
    b L_c6c38
L_c6b58:
    mulli 0, 3, 0xf0
L_c6b5c:
    add 4, 4, 0
L_c6b60:
    lwz 26, 0x34(4)
L_c6b64:
    cmplwi 26, 0x30
L_c6b68:
    bge L_c6c38
L_c6b6c:
    mr 4, 26
L_c6b70:
    bl L_c6b70
L_c6b74:
    clrlwi 3, 3, 0x18
L_c6b78:
    li 0, 0x33
L_c6b7c:
    subfc 0, 0, 3
L_c6b80:
    subfe 0, 0, 0
L_c6b84:
    and 3, 3, 0
L_c6b88:
    slwi 0, 3, 2
L_c6b8c:
    mulli 5, 26, 0x99
L_c6b90:
    addi 4, 27, 0
L_c6b94:
    subf 3, 3, 0
L_c6b98:
    add 0, 4, 5
L_c6b9c:
    cmpwi 30, 0
L_c6ba0:
    add 5, 3, 0
L_c6ba4:
    li 8, 0
L_c6ba8:
    beq L_c6bbc
L_c6bac:
    lbz 0, 0xd(29)
L_c6bb0:
    cmpwi 0, 0x31
L_c6bb4:
    bne L_c6bbc
L_c6bb8:
    li 8, 0x1e
L_c6bbc:
    cmpwi 31, 0
L_c6bc0:
    bne L_c6bd8
L_c6bc4:
    cmpwi 30, 0
L_c6bc8:
    beq L_c6bdc
L_c6bcc:
    lbz 0, 0xd(29)
L_c6bd0:
    cmpwi 0, 0x33
L_c6bd4:
    bne L_c6bdc
L_c6bd8:
    li 8, 0x10
L_c6bdc:
    lbz 4, 0(5)
L_c6be0:
    slwi 6, 8, 8
L_c6be4:
    lbz 3, 1(5)
L_c6be8:
    subfic 7, 8, 0x64
L_c6bec:
    lbz 0, 2(5)
L_c6bf0:
    mullw 5, 4, 7
L_c6bf4:
    subf 6, 8, 6
L_c6bf8:
    mullw 3, 3, 7
L_c6bfc:
    mullw 0, 0, 7
L_c6c00:
    lis 4, 0x51ec
L_c6c04:
    add 5, 6, 5
L_c6c08:
    addi 4, 4, -0x7ae1
L_c6c0c:
    add 0, 6, 0
L_c6c10:
    add 3, 6, 3
L_c6c14:
    mulhwu 6, 4, 5
L_c6c18:
    mulhwu 5, 4, 3
L_c6c1c:
    mulhwu 0, 4, 0
L_c6c20:
    rlwinm 4, 6, 0x1b, 0x18, 0x1f
L_c6c24:
    mr 3, 28
L_c6c28:
    rlwinm 5, 5, 0x1b, 0x18, 0x1f
L_c6c2c:
    rlwinm 6, 0, 0x1b, 0x18, 0x1f
L_c6c30:
    li 7, 0xff
L_c6c34:
    bl L_c6c34
L_c6c38:
    lmw 26, 8(1)
L_c6c3c:
    lwz 0, 0x24(1)
L_c6c40:
    mtlr 0
L_c6c44:
    addi 1, 1, 0x20
L_c6c48:
    blr 

# create_coloured_drift_effect
L_c6c4c:
    stwu 1, -0x10(1)
L_c6c50:
    mflr 0
L_c6c54:
    stw 0, 0x14(1)
L_c6c58:
    stw 31, 0xc(1)
L_c6c5c:
    mr 31, 3
L_c6c60:
    bl L_c6c60
L_c6c64:
    mr 3, 31
L_c6c68:
    bl L_c6ab8
L_c6c6c:
    lwz 0, 0x14(1)
L_c6c70:
    lwz 31, 0xc(1)
L_c6c74:
    mtlr 0
L_c6c78:
    addi 1, 1, 0x10
L_c6c7c:
    blr 

# update_coloured_drift_effect
L_c6c80:
    stwu 1, -0x10(1)
L_c6c84:
    mflr 0
L_c6c88:
    stw 0, 0x14(1)
L_c6c8c:
    stw 31, 0xc(1)
L_c6c90:
    mr 31, 3
L_c6c94:
    bl L_c6c94
L_c6c98:
    mr 3, 31
L_c6c9c:
    bl L_c6ab8
L_c6ca0:
    lwz 0, 0x14(1)
L_c6ca4:
    lwz 31, 0xc(1)
L_c6ca8:
    mtlr 0
L_c6cac:
    addi 1, 1, 0x10
L_c6cb0:
    blr 
