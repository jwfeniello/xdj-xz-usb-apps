.syntax unified
.arm
.fpu vfp
.section .text.hook
.global gran_hook,gran_state,gran_original
.type gran_hook,%function
gran_hook:
    push {r4-r11,lr}
    sub sp,sp,#12
    mov r9,r0
    mov r10,r1
    mov r11,r2
    mov r4,r3
    ldr r5,[sp,#48]
    ldr r6,[sp,#52]
    str r5,[sp]
    str r6,[sp,#4]
    adr r7,gran_state
    ldr r0,[r7,#36]
    cmp r0,#0
    beq call_original
    cmp r5,#2
    bne cleanup_fault
    cmp r6,#64
    bne cleanup_fault
    cmp r4,#0
    beq cleanup_fault
    ldr r8,[r4]
    ldr r0,[r7,#24]
    cmp r8,r0
    bne cleanup_fault
    mov r0,#0
    mov r1,#128
clear_previous:
    str r0,[r8],#4
    subs r1,r1,#1
    bne clear_previous
    str r0,[r7,#36]
    b call_original
cleanup_fault:
    mov r0,#1
    str r0,[r7,#32]
    mov r0,#0
    str r0,[r7]
call_original:
    mov r0,r9
    mov r1,r10
    mov r2,r11
    mov r3,r4
    ldr ip,gran_original
    blx ip
    adr r7,gran_state
    ldr r0,[r7]
    cmp r0,#2
    moveq r0,#0
    streq r0,[r7]
    cmp r0,#1
    bne finish
    ldr r0,[r7,#12]
    add r0,r0,#1
    str r0,[r7,#12]
    cmp r5,#2
    bne fault
    cmp r6,#64
    bne fault
    cmp r4,#0
    beq fault
    ldr r8,[r4]
    ldr r0,[r7,#24]
    cmp r8,r0
    bne fault
    vmrs r11,fpscr
    mov r0,#0x01000000
    vmsr fpscr,r0
    mov r0,r7
    mov r1,r8
    bl gran_process
    vmsr fpscr,r11
finish:
    add sp,sp,#12
    pop {r4-r11,pc}
fault:
    mov r0,#0
    str r0,[r7]
    mov r0,#1
    str r0,[r7,#32]
    b finish
.balign 4
gran_original: .word 0x3f078
gran_state:
    .space 288
.size gran_hook,.-gran_hook
