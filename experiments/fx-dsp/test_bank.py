from pathlib import Path
import json,math,random,struct,wave,time
exec((Path(__file__).parent/'test_hook.py').read_text().split('started=time.monotonic()')[0])
def word(u,s,i,v):u.mem_write(s+4*i,struct.pack('<I',v))
def get(u,s,i):return struct.unpack('<I',u.mem_read(s+4*i,4))[0]
def command(fx,size=56,colour=128,mix=220,on=1,freeze=0,reverse=0):return on|(freeze<<1)|(reverse<<2)|(size<<4)|(colour<<12)|(mix<<20)|(fx<<28)
def ready():
 u,s,source,run=setup();word(u,s,11,65536)
 ring=[]
 for n in range(65536):
  v=.3*math.sin(n*.04)+.15*math.sin(n*.11);ring.extend([v,-v])
 u.mem_write(base+16384,pack(ring));return u,s,source,run
started=time.monotonic();r=random.Random(38);summaries=[]
for fx in range(4):
 u,s,source,run=ready();samples=[]
 for block in range(2100):
  word(u,s,19,get(u,s,1)+44100)
  # Widely changing controls exercise state, stability, bounds and mixed stereo.
  size=[0,56,124,248][(block//150)%4];colour=[0,128,255][(block//211)%3]
  word(u,s,18,command(fx,size,colour,255,freeze=int(fx<2 and block>1500),reverse=block//300%2))
  values=[]
  for n in range(64):
   t=(block*64+n)/44100
   v=.28*math.sin(2*math.pi*220*t)+.18*math.sin(2*math.pi*880*t)+r.uniform(-.06,.06)
   values.extend([v,-v*.8])
  source['audio']=pack(values);state,out=run()
  assert state[8]==0 and state[20]==0 and state[0]==1
  assert all(math.isfinite(v) and abs(v)<=2.0001 for v in out)
  if block>40:assert get(u,s,21)==fx
  samples.extend(out)
 # Smoothly bypass each algorithm to bit-exact dry; active processing never leaks to deck 2 (run assertion).
 word(u,s,18,command(fx,on=0));source['audio']=pack([.3,-.2]*64)
 for _ in range(220):word(u,s,19,get(u,s,1)+44100);state,out=run()
 assert pack(out)==source['audio']
 # Normal stop after wet processing clears the tail left by the stock pause path.
 word(u,s,18,command(fx));word(u,s,19,get(u,s,1)+44100);state,out=run();assert state[9]
 word(u,s,0,2);source['audio']=None;state,out=run();assert state[0]==0 and pack(out)==bytes(512)
 with wave.open(str(p/('bank_demo_%d.wav'%fx)),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(44100)
  w.writeframes(struct.pack('<%dh'%len(samples),*(max(-32767,min(32767,round(v*20000))) for v in samples)))
 summaries.append({'effect':fx,'seconds':2100*64/44100,'peak':max(map(abs,samples))})
# Every ordered switch pair must reach the new processor, including switching while dry.
u,s,source,run=ready();source['audio']=pack([.25,-.5]*64)
for old in range(4):
 for new in range(4):
  for fx in [old,new]:
   word(u,s,18,command(fx))
   for _ in range(70):
    was=get(u,s,21)
    word(u,s,19,get(u,s,1)+44100);state,out=run()
    assert state[8]==0 and all(math.isfinite(v) and abs(v)<=2.0001 for v in out)
    if get(u,s,21)!=was:assert get(u,s,17)==0
   assert get(u,s,21)==fx
# Robot: a DC input becomes a 440 Hz carrier plus the expected dry component.
u,s,source,run=ready();source['audio']=pack([.5,-.5]*64);word(u,s,18,command(2,size=105,colour=0,mix=255));signal=[]
for block in range(800):
 word(u,s,19,get(u,s,1)+44100);state,out=run()
 if block>100:signal.extend(out[::2])
def amplitude(signal,hz):
 a=sum(x*math.cos(2*math.pi*hz*i/44100) for i,x in enumerate(signal));b=sum(x*math.sin(2*math.pi*hz*i/44100) for i,x in enumerate(signal));return 2*math.hypot(a,b)/len(signal)
assert amplitude(signal,440)>.30 and amplitude(signal,300)<.01
# Vowel A low formant should favour 800 Hz over a far-below-formant test tone.
def vowel_energy(hz):
 u,s,source,run=ready();word(u,s,18,command(3,size=0,colour=0,mix=255));energy=0;count=0
 for block in range(220):
  inputs=[.25*math.sin(2*math.pi*hz*(block*64+n)/44100) for n in range(64)]
  source['audio']=pack([v for x in inputs for v in [x,x]])
  word(u,s,19,get(u,s,1)+44100);state,out=run()
  if block>120:
   for x,y in zip(inputs,out[::2]):energy+=y*y;count+=1
 return math.sqrt(energy/count)
assert vowel_energy(800)>4*vowel_energy(100)
# Repeated high-amplitude impulses and maximum morph sweep remain finite.
u,s,source,run=ready()
for block in range(600):
 word(u,s,18,command(3,size=(block*17)%249,colour=(block*31)%256,mix=255));word(u,s,19,get(u,s,1)+44100)
 source['audio']=pack(([16.,-16.]+[0.]*126) if block%3==0 else [0.]*128)
 state,out=run();assert state[8]==0 and all(math.isfinite(v) and abs(v)<=16.001 for v in out)
result={'passed':True,'actual_arm_code':True,'effects':summaries,'ordered_switch_pairs':16,'robot_440hz_verified':True,'vowel_formant_response_verified':True,'extreme_input_stability':True,'dry_bypass_bit_exact':True,'abi_deck2_and_pause_cleanup':True,'seconds':time.monotonic()-started,'hardware_tested':False}
(p/'bank_test_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
