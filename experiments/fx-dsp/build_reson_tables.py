from pathlib import Path
import math
p=Path(__file__).parent
def fl(x):return format(x,'.10e')+'f'
rot=[]
for midi in range(36,84):
 f=440*2**((midi-69)/12)
 rot.append('{'+','.join(fl(v) for h in (1,2) for v in (math.cos(2*math.pi*f*h/44100),math.sin(2*math.pi*f*h/44100)))+'}')
radius=[math.exp(math.log(.001)/(44100*(.1+2.9*i/248))) for i in range(249)]
(p/'reson_tables.h').write_text('/* C2-B5; fundamental/second harmonic; 100-3000ms T60. */\nstatic const float note_rotation[48][4]={'+','.join(rot)+'};\nstatic const float decay_radius[249]={'+','.join(fl(v) for v in radius)+'};\n')
