from pathlib import Path
import subprocess,json,os
from elftools.elf.elffile import ELFFile
p=Path(__file__).resolve().parent
zig=os.environ.get('ZIG','zig')
common=[zig,'cc','-target','arm-linux-musleabi','-mcpu=cortex_a9','-marm','-mfloat-abi=softfp','-mfpu=neon']
for source in ['hook.S','dsp.c']:
 subprocess.run(common+['-c',str(p/source),'-O2','-ffreestanding','-fPIC','-fvisibility=hidden','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-vectorize','-fno-slp-vectorize','-o',str(p/(source+'.o'))],check=True)
subprocess.run(common+['-nostdlib','-static','-no-pie','-Wl,-e,gran_hook',str(p/'hook.S.o'),str(p/'dsp.c.o'),'-Wl,-T,'+str(p/'link.ld'),'-o',str(p/'gran_hook.elf')],check=True)
with (p/'gran_hook.elf').open('rb') as f:
 e=ELFFile(f); section=e.get_section_by_name('.text');code=section.data(); assert section['sh_addr']==0 and len(code)<12288
 assert not any(sec['sh_flags']&2 and sec['sh_size'] and sec.name!='.text' for sec in e.iter_sections())
 assert not any(sym['st_shndx']=='SHN_UNDEF' and sym.name for sym in e.get_section_by_name('.symtab').iter_symbols())
 assert not any(s['sh_type'] in ('SHT_REL','SHT_RELA') and s.num_relocations() for s in e.iter_sections())
 symbols={s.name:s['st_value']-section['sh_addr'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name.startswith('gran_')}
(p/'gran_hook.bin').write_bytes(code)
(p/'gran_layout.json').write_text(json.dumps(symbols,indent=2))
(p/'hook_data.h').write_text('static const unsigned char hook_code[]={'+','.join(map(str,code))+'};\n'+''.join(f'#define {k.upper()} {v}u\n' for k,v in symbols.items()))

print(symbols,'bytes',len(code))
