#include "dsp.h"
#include "bank_tables.h"
#include "reson_tables.h"
static float asfloat(U v){union{U u;float f;}x={.u=v};return x.f;}
static U asword(float v){union{U u;float f;}x={.f=v};return x.u;}
static U spawn(U *s,U scatter){
 U r=s[SEED];r^=r<<13;r^=r>>17;r^=r<<5;s[SEED]=r;
 U distance=8192+(((r>>16)*scatter)>>9);
 return (s[WRITEPOS]-distance)&65535;
}
/* No allocations, system calls, locks or external functions in the callback. */
void gran_process(U *s,float *out){
 U cmd=s[COMMAND];
 if((cmd&0x80000008u)||((cmd>>28)&7)>4||((cmd>>4)&255)>248){s[FAULT]=2;s[ENABLED]=0;return;}
 for(U i=0;i<128;i++)if((asword(out[i])&0x7fffffffu)>0x41800000u){s[FAULT]=3;s[ENABLED]=0;return;}
 if(s[FRAMES]>=s[LEASE])s[WATCHDOG]=1;
 float target=(float)((cmd>>20)&255)*(((cmd>>28)&7)==3?(1.0f/255.0f):(0.70f/255.0f));
 if(!(cmd&1)||s[WATCHDOG]||s[FRAMES]>=s[TOTAL]-44160||s[FILLED]<RING_FRAMES)target=0;
 U requested=(cmd>>28)&7,active=s[ACTIVE_FX],notes=s[RESON_NOTES];
 U count=0;for(U bits=notes&4095;bits;bits&=bits-1)count++;
 if(requested==4&&((notes&~16383u)||!count||count>3)){s[FAULT]=4;s[ENABLED]=0;return;}
 int changing=active!=requested||(active==4&&notes!=s[ACTIVE_NOTES]);
 float wet=asfloat(s[WET]);
 if(changing){
  target=0;
  if(wet<0.00001f){
   wet=0;active=requested;s[ACTIVE_FX]=active;s[PHASE]=0;s[HEAD0]=0;s[HEAD1]=0;s[OSC_PHASE]=0;
   for(U k=FILTER_STATE;k<STATE_WORDS;k++)if(k!=RESON_NOTES)s[k]=0;
   s[ACTIVE_NOTES]=notes;
  }
 }
 if(!changing)s[ACTIVE_CMD]=cmd;
 else cmd=s[ACTIVE_CMD];
 U size=(cmd>>4)&255,scatter=(cmd>>12)&255;
 float coeff[6];
 if(active==3){
  float morph=(float)size*(4.0f/248.0f);U v=(U)morph;if(v>3)v=3;float t=morph-(float)v;
  for(U k=0;k<6;k++)coeff[k]=formants[v][k]+t*(formants[v+1][k]-formants[v][k]);
 }
 U voices[3],voice_count=0;
 if(active==4){
  U selected=s[ACTIVE_NOTES];for(U n=0;n<12;n++)if(selected&(1u<<n))voices[voice_count++]=((selected>>12)&3)*12+n;
 }
 float radius=decay_radius[size],normalizer=voice_count?0.8f/(float)voice_count:0;
 U osc=s[OSC_PHASE],increment=(20+size*4)*97392u;
 float colour=(float)scatter*(1.0f/255.0f);
 float *ring=(float*)s[RING];U pos=s[WRITEPOS],filled=s[FILLED];
 U phase=s[PHASE],length=s[LENGTH],h0=s[HEAD0],h1=s[HEAD1];
 int touched=0;
 for(U i=0;i<64;i++){
  float left=out[2*i],right=out[2*i+1];
  if(active>=2||!(cmd&2)||filled<RING_FRAMES){
   ring[pos*2]=left;ring[pos*2+1]=right;pos=(pos+1)&65535;
   if(filled<RING_FRAMES)filled++;
  }
  wet+=(target-wet)*(changing?(1.0f/128.0f):(1.0f/1024.0f));
  if(target==0&&wet<0.00001f){wet=0;continue;}
  float gl=0,gr=0;
  if(active==0){
   if(phase==0){length=256+size*32;s[WRITEPOS]=pos;h0=spawn(s,scatter);}
   U half=length>>1;if(phase==half){s[WRITEPOS]=pos;h1=spawn(s,scatter);}
   U ramp=phase<half?phase:length-phase;float w=(float)ramp/(float)half;
   gl=ring[h1*2]+w*(ring[h0*2]-ring[h1*2]);gr=ring[h1*2+1]+w*(ring[h0*2+1]-ring[h1*2+1]);
   U step=(cmd&4)?65535:1;h0=(h0+step)&65535;h1=(h1+step)&65535;
   if(++phase==length)phase=0;
  }else if(active==1){
   if(phase==0){
    length=512+size*64;s[WRITEPOS]=pos;h0=(spawn(s,scatter)-8192)&65535;
    s[SLICE_STEP]=(cmd&4)||(s[SEED]&1)?65535:1;
   }
   U edge=phase<length-1-phase?phase:length-1-phase;float envelope=edge<64?(float)edge*(1.0f/64.0f):1.0f;
   gl=ring[h0*2]*envelope;gr=ring[h0*2+1]*envelope;h0=(h0+s[SLICE_STEP])&65535;
   if(++phase==length)phase=0;
  }else if(active==2){
   float carrier=sine256[osc>>24];float square=carrier<0?-1.0f:1.0f;
   carrier+=colour*(square-carrier);osc+=increment;gl=left*carrier;gr=right*carrier;
  }else if(active==3){
   float inputs[2]={left,right},outputs[2];
   for(U channel=0;channel<2;channel++){
    float bands[2];
    for(U band=0;band<2;band++){
     U k=FILTER_STATE+channel*4+band*2;float z1=asfloat(s[k]),z2=asfloat(s[k+1]);
     float b0=coeff[band*3],a1=coeff[band*3+1],a2=coeff[band*3+2];
     float y=b0*inputs[channel]+z1;
     s[k]=asword(z2-a1*y);s[k+1]=asword(-b0*inputs[channel]-a2*y);bands[band]=y;
    }
    /* Retain both vowel resonances at either brightness extreme. */
    float balance=0.2f+0.6f*colour;
    float y=3.0f*((1.0f-balance)*bands[0]+balance*bands[1]);
    float magnitude=y<0?-y:y;
    outputs[channel]=y/(1.0f+0.5f*magnitude);
   }
   gl=outputs[0];gr=outputs[1];
  }else{
   float inputs[2]={left,right},outputs[2];
   for(U channel=0;channel<2;channel++){
    float sum=0;
    for(U voice=0;voice<voice_count;voice++){
     float partial[2];
     for(U harmonic=0;harmonic<2;harmonic++){
      U k=RESON_STATE+channel*12+voice*4+harmonic*2;
      float re=asfloat(s[k]),im=asfloat(s[k+1]);
      float c=note_rotation[voices[voice]][harmonic*2],sn=note_rotation[voices[voice]][harmonic*2+1];
      float nr=radius*(c*re-sn*im)+inputs[channel]*0.025f;
      float ni=radius*(sn*re+c*im);
      /* Bound stored modal energy as well as the audible output. */
      float energy=(nr<0?-nr:nr)+(ni<0?-ni:ni);
      if(energy>8){float scale=8.0f/energy;nr*=scale;ni*=scale;}
      s[k]=asword(nr);s[k+1]=asword(ni);partial[harmonic]=ni;
     }
     sum+=partial[0]+colour*0.6f*partial[1];
    }
    float y=sum*normalizer,magnitude=y<0?-y:y;outputs[channel]=y/(1.0f+0.5f*magnitude);
   }
   gl=outputs[0];gr=outputs[1];
  }
  out[2*i]=left+wet*(gl-left);out[2*i+1]=right+wet*(gr-right);touched=1;

 }
 s[WRITEPOS]=pos;s[FILLED]=filled;s[PHASE]=phase;s[LENGTH]=length;s[HEAD0]=h0;s[HEAD1]=h1;s[WET]=asword(wet);s[OSC_PHASE]=osc;
 s[WROTE]=(U)touched;s[touched?PROCESSED:DRY]++;
 s[FRAMES]+=64;
 if(s[FRAMES]>=s[TOTAL])s[ENABLED]=2;
}
