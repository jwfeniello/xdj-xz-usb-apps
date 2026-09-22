from pathlib import Path
import json, math, random, struct, time
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import *

p = Path(__file__).resolve().parent
layout = json.loads((p/'gran_layout.json').read_text())
code = (p/'gran_hook.bin').read_bytes()
base, orig, buf, buf2, stack, end = 0x100000, 0x3f078, 0x200000, 0x201000, 0x300000, 0x400000
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
alpha, inv = f32(.1077414503), f32(1/44160)
def pack(values): return struct.pack('<%df' % len(values), *values)

def setup(channels=2, frames=64, pointer=buf):
    u = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    for addr, size in [(base, 0x90000), (0x30000, 0x10000), (buf, 0x3000), (stack, 0x2000), (end, 0x1000)]:
        u.mem_map(addr, size)
    u.reg_write(UC_ARM_REG_C1_C0_2, 0xf00000)
    u.reg_write(UC_ARM_REG_FPEXC, 0x40000000)
    u.mem_write(base, code)
    u.mem_write(orig, bytes.fromhex('1eff2fe1'))
    s = base + layout['gran_state']
    state=[1,0,7938048,0,0,0,pointer,base+16384,0,0,0,0,0,2048,0,0,0x125abcd,0,0,44100,0]
    u.mem_write(s,struct.pack('<40I',*(state+[0]*19)))
    u.mem_write(buf+0x2000, struct.pack('<2I',buf,buf2))
    source = {'audio':pack([.25,-.5]*64), 'calls':0}
    sentinel = pack([.875,-.125]*64)
    def stock(uc, addr, size, _):
        if addr != orig: return
        source['calls'] += 1
        assert uc.reg_read(UC_ARM_REG_R0)==0x12345678
        assert uc.reg_read(UC_ARM_REG_R1)==0x87654321
        assert uc.reg_read(UC_ARM_REG_R2)==1
        assert uc.reg_read(UC_ARM_REG_R3)==buf+0x2000
        sp = uc.reg_read(UC_ARM_REG_SP)
        assert sp%8==0 and struct.unpack('<2I',uc.mem_read(sp,8))==(channels,frames)
        # Exact stock pause behavior: only first 64 floats explicitly cleared.
        uc.mem_write(buf,bytes(256))
        if source['audio'] is not None: uc.mem_write(buf,source['audio'])
        uc.mem_write(buf2,sentinel)
        # Stock callback may clobber all caller-saved integer registers.
        for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]:
            uc.reg_write(r,0xaabbccdd)
    u.hook_add(UC_HOOK_CODE,stock,begin=orig,end=orig)
    def run():
        u.reg_write(UC_ARM_REG_SP,stack+0x1000)
        u.mem_write(stack+0x1000,struct.pack('<2I',channels,frames))
        for reg,value in [(UC_ARM_REG_R0,0x12345678),(UC_ARM_REG_R1,0x87654321),(UC_ARM_REG_R2,1),(UC_ARM_REG_R3,buf+0x2000),(UC_ARM_REG_LR,end)]:
            u.reg_write(reg,value)
        for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1): u.reg_write(r,0x550000+r)
        for r in range(UC_ARM_REG_D8,UC_ARM_REG_D15+1): u.reg_write(r,0x1122334455660000+r)
        u.reg_write(UC_ARM_REG_FPSCR,0x80400000)
        u.emu_start(base,end,count=65000)
        assert u.reg_read(UC_ARM_REG_PC)==end and u.reg_read(UC_ARM_REG_SP)==stack+0x1000
        for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1): assert u.reg_read(r)==0x550000+r
        for r in range(UC_ARM_REG_D8,UC_ARM_REG_D15+1): assert u.reg_read(r)==0x1122334455660000+r
        assert u.reg_read(UC_ARM_REG_FPSCR)==0x80400000
        assert bytes(u.mem_read(buf2,512))==sentinel
        return struct.unpack('<21I',u.mem_read(s,84)), struct.unpack('<128f',u.mem_read(buf,512))
    return u,s,source,run

started=time.monotonic()
def setword(u,s,i,v):u.mem_write(s+i*4,struct.pack('<I',v))
def cmd(on=1,freeze=0,reverse=0,size=56,scatter=128,mix=180):return on|(freeze<<1)|(reverse<<2)|(size<<4)|(scatter<<12)|(mix<<20)
u,s,source,run=setup();state=None
# Initial dry fill, with exact original audio and ring wrap.
for i in range(1050):
 source['audio']=pack([.5,-.25]*64)
 setword(u,s,19,i*64+44100);state,out=run()
 assert pack(out)==source['audio']
assert state[11]==65536 and state[10]==(1050*64)&65535
# With a filled constant stereo ring, arbitrary grain position and reverse remain DC.
for reverse in [0,1]:
 setword(u,s,18,cmd(reverse=reverse))
 for _ in range(120):
  setword(u,s,19,state[1]+44100);state,out=run()
  assert max(abs(v-(.5 if i%2==0 else -.25)) for i,v in enumerate(out))<1e-6
# Freeze stops recording and reads previous audio while new input is zero.
setword(u,s,18,cmd(freeze=1));source['audio']=bytes(512);pos=state[10]
for _ in range(150):
 setword(u,s,19,state[1]+44100);state,out=run()
 assert state[10]==pos and all(abs(v)<=.500001 for v in out)
assert max(map(abs,out))>.1
# Changes of grain size/reverse/scatter/mix and ring wraps never overflow or amplify.
rng=random.Random(125)
for i in range(600):
 setword(u,s,18,cmd(freeze=i%3==0,reverse=i%2,size=(i*17)%249,scatter=(i*11)%256,mix=(i*3)%256))
 source['audio']=pack([f32(rng.uniform(-1.35,1.35)) for _ in range(128)])
 setword(u,s,19,state[1]+44100);state,out=run()
 assert all(math.isfinite(x) and abs(x)<1.35001 for x in out)
 assert 0<=state[12]<state[13]<=8192 and state[13]>=256
 assert all(v<65536 for v in [state[10],state[14],state[15]])
# Latched watchdog bypass, even with a later valid command/lease.
setword(u,s,19,state[1])
for _ in range(250):state,out=run()
assert state[20]==1 and pack(out)==source['audio'] and state[17]==0
setword(u,s,19,state[1]+44100);state,out=run();assert pack(out)==source['audio']
# Autonomous final fade and lifetime endpoint.
u,s,source,run=setup();setword(u,s,1,7938048-44160);setword(u,s,19,7938048+44100)
setword(u,s,11,65536);setword(u,s,18,cmd());u.mem_write(s+17*4,pack([.7]))
for _ in range(690):state,out=run()
assert state[0]==2 and state[1]==7938048 and pack(out)==source['audio']
state,out=run();assert state[0]==0 and state[9]==0
# Contract failures leave stock output unchanged.
for kw in [{'channels':1},{'frames':63},{'pointer':buf+4}]:
 u,s,source,run=setup(**kw);state,out=run();assert state[0]==0 and state[8]==1 and pack(out)==source['audio']
for value in [float('nan'),float('inf'),-float('inf'),17.,-17.]:
 u,s,source,run=setup();source['audio']=pack([.2]*127+[value]);state,out=run()
 assert state[0]==0 and state[8]==3 and bytes(u.mem_read(buf,512))==source['audio']
for invalid in [0x80000000,8,249<<4]:
 u,s,source,run=setup();setword(u,s,18,invalid);state,out=run();assert state[8]==2
# Stop after wet processing: no stale second-half output survives stock pause.
u,s,source,run=setup();setword(u,s,11,65536);setword(u,s,18,cmd());run()
setword(u,s,0,2);source['audio']=None;state,out=run()
assert state[0]==0 and state[9]==0 and pack(out)==bytes(512)
result={'actual_arm_code_tested':True,'dry_bit_exact':True,'record_fill_and_wrap':True,
'freeze_preserves_buffer':True,'reverse_and_size_changes_bounded':True,'dc_stereo_preserved':True,
'abi_fpscr_and_deck2_preserved':True,'watchdog_bypass_latched':True,'final_fade_and_stop':True,
'bad_inputs_and_commands_rejected':True,'pause_stop_tail_clean':True,'hardware_tested':False,
'seconds':round(time.monotonic()-started,2)}
(p/'hook_test_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
