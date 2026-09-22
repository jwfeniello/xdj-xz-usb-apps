from pathlib import Path
import struct,math,json,time,random,wave
exec((Path(__file__).parent/'test_hook.py').read_text().split('started=time.monotonic()')[0])
def word(u,s,i,v):u.mem_write(s+4*i,struct.pack('<I',v))
def get(u,s,i):return struct.unpack('<I',u.mem_read(s+4*i,4))[0]
def floats(u,s,i,n):return struct.unpack('<%df'%n,u.mem_read(s+4*i,4*n))
def command(fx=4,size=124,colour=0,on=1):return on|(size<<4)|(colour<<12)|(255<<20)|(fx<<28)
def ready(notes,size=124,colour=0):
 u,s,source,run=setup();word(u,s,11,65536);word(u,s,40,notes);word(u,s,18,command(size=size,colour=colour));source['audio']=bytes(512)
 def step():
  word(u,s,19,get(u,s,1)+44100);state,out=run();assert state[8]==0 and all(math.isfinite(x) and abs(x)<=16.001 for x in out);return state,out
 for _ in range(80):step()
 return u,s,source,step
started=time.monotonic();pitch=[]
for note in range(48):
 u,s,source,step=ready((1<<(note%12))|((note//12)<<12));source['audio']=pack([.1,.1]+[0.]*126);step();source['audio']=bytes(512);signal=[]
 for _ in range(100):state,out=step();signal.extend(out[::2])
 crossings=[]
 for i in range(1,len(signal)):
  if signal[i-1]<0<=signal[i]:crossings.append(i-1-signal[i-1]/(signal[i]-signal[i-1]))
 assert len(crossings)>3
 hz=44100*(len(crossings)-1)/(crossings[-1]-crossings[0]);expected=440*2**((36+note-69)/12);cents=1200*math.log2(hz/expected)
 assert abs(cents)<1,(note,hz,expected,cents)
 pitch.append(abs(cents))
# Measure stored modal decay with zero input; output saturation cannot mask unstable poles.
decays=[]
for size in [0,124,248]:
 u,s,source,step=ready(1|(2<<12),size);source['audio']=pack([.1,.1]+[0.]*126);step();source['audio']=bytes(512)
 start=math.hypot(*floats(u,s,42,2))
 for _ in range(100):step()
 finish=math.hypot(*floats(u,s,42,2));t60=-(6400/44100)*math.log(1000)/math.log(finish/start);expected=.1+2.9*size/248
 assert abs(t60/expected-1)<.02,(t60,expected);decays.append(t60)
# Retune must fade fully dry before committing the new note set; any 3-note chord is bounded.
u,s,source,step=ready(1|(1<<12));rng=random.Random(771);max_peak=0
for block in range(900):
 if block%60==0:
  mask=sum(1<<n for n in rng.sample(range(12),3));word(u,s,40,mask|((block//60%4)<<12))
 word(u,s,18,command(size=(block*17)%249,colour=(block*31)%256));before=get(u,s,41)
 source['audio']=pack([rng.uniform(-2,2) for _ in range(128)]);state,out=step()
 if get(u,s,41)!=before:assert get(u,s,17)==0
 max_peak=max(max_peak,max(map(abs,out)))
 assert all(math.isfinite(v) for v in floats(u,s,42,24))
 for k in range(42,66,2):assert sum(map(abs,floats(u,s,k,2)))<8.001
# All effect transitions involving the new mode, including active chord -> old effects.
for old in range(5):
 for new in range(5):
  for fx in [old,new]:
   word(u,s,18,command(fx));source['audio']=pack([.2,-.1]*64)
   for _ in range(70):step()
   assert get(u,s,21)==fx
# Bypass to exact dry, stock paused cleanup, invalid configs fail without touching output.
word(u,s,18,command(on=0))
for _ in range(230):state,out=step()
assert pack(out)==source['audio']
word(u,s,18,command());state,out=step();assert state[9]
word(u,s,0,2);source['audio']=None;state,out=step();assert state[0]==0 and pack(out)==bytes(512)
for bad in [0,15,1<<14,0x80000001]:
 u,s,source,run=setup();word(u,s,18,command());word(u,s,40,bad);state,out=run();assert state[8]==4 and pack(out)==source['audio']
# Synthetic C major chord impulse render for inspection.
u,s,source,step=ready((1|16|128)|(1<<12),248,160);samples=[]
for block in range(1400):
 source['audio']=pack([.5,.5]+[0.]*126) if block%350==0 else bytes(512);state,out=step();samples.extend(out)
with wave.open(str(p/'resonator_chord_demo.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100);w.writeframes(struct.pack('<%dh'%len(samples),*(max(-32767,min(32767,round(v*28000))) for v in samples)))
result={'passed':True,'actual_relocated_arm_code':True,'tested_notes':48,'max_pitch_error_cents':max(pitch),'measured_decay_seconds':decays,'retune_fades_to_dry':True,'all_ordered_effect_pairs':25,'three_voice_state_bounded':True,'invalid_note_configs_rejected':True,'bypass_bit_exact_and_pause_cleanup':True,'hardware_cpu_and_sound_pending':True,'seconds':time.monotonic()-started}
(p/'resonator_test_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
