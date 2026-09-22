/* ARM EABI Linux syscalls only: no libc, loader, installation, audio or inputs. */
#include "pong_core.h"
typedef unsigned int U;
_Static_assert(sizeof(U)==4,"32-bit ABI required");
static Pixel frame[W*H], backup[W*H];
static long call6(long n,long a,long b,long c,long d,long e,long f){
 register long r0 __asm__("r0")=a;register long r1 __asm__("r1")=b;
 register long r2 __asm__("r2")=c;register long r3 __asm__("r3")=d;
 register long r4 __asm__("r4")=e;register long r5 __asm__("r5")=f;
 register long r7 __asm__("r7")=n;
 __asm__ volatile("svc 0":"+r"(r0):"r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5),"r"(r7):"memory","cc");return r0;
}
static void say(const char *s){U n=0;while(s[n])n++;call6(4,1,(long)s,n,0,0,0);}
static void number(U v){char b[12];int n=0;do{b[n++]=(char)('0'+v%10);v/=10;}while(v);for(int i=n-1;i>=0;i--)call6(4,1,(long)&b[i],1,0,0,0);}
static int info(int fd,U *v,U *f){return call6(54,fd,0x4600,(long)v,0,0,0)>=0 && call6(54,fd,0x4602,(long)f,0,0,0)>=0;}
static int valid(U *v,U *f){
 return v[0]==W&&v[1]==H&&v[2]>=W&&v[2]<=4096&&v[3]>=H&&v[3]<=4096&&v[4]<=v[2]-W&&v[5]<=v[3]-H
 &&v[6]==16&&v[7]==0&&v[8]==11&&v[9]==5&&v[10]==0&&v[11]==5&&v[12]==6&&v[13]==0
 &&v[14]==0&&v[15]==5&&v[16]==0&&v[18]==0&&v[20]==0&&f[6]==0&&f[8]==2
 &&f[11]>=v[2]*2&&f[11]<=8192&&(f[11]&1)==0&&f[5]>0&&f[5]<=16777216
 &&(v[5]+H-1)*f[11]+(v[4]+W)*2<=f[5];
}
static int unchanged(U*a,U*b,U*fa,U*fb){for(int i=0;i<21;i++)if(a[i]!=b[i])return 0;for(int i=4;i<12;i++)if(fa[i]!=fb[i])return 0;return 1;}
__attribute__((used)) int run(void){
 U v[40]={0},f[20]={0},now[40]={0},nf[20]={0};Game g;
 say("XZ_PONG_ARM_STARTED\n");
 int fd=(int)call6(5,(long)"/dev/fb0",2,0,0,0,0);
 if(fd<0){say("FB_OPEN_FAILED\n");return 1;}
 if(!info(fd,v,f)){say("FB_QUERY_FAILED\n");return 2;}
 say("width=");number(v[0]);say(" height=");number(v[1]);say(" bpp=");number(v[6]);say(" stride=");number(f[11]);say(" bytes=");number(f[5]);say("\n");
 if(!valid(v,f)){say("UNSUPPORTED_DISPLAY_NO_WRITE\n");return 3;}
 long mapped=call6(192,0,f[5],3,1,fd,0);
 if((U)mapped>=(U)-4095){say("MMAP_FAILED\n");return 4;}
 volatile Pixel *mem=(volatile Pixel *)mapped;U stride=f[11]/2,origin=v[5]*stride+v[4];
 for(int y=0;y<H;y++)for(int x=0;x<W;x++)backup[y*W+x]=mem[origin+y*stride+x];
 say("PONG_DRAW_BEGIN_300_FRAMES\n");init_game(&g);
 for(int k=0;k<300;k++){
  if(!info(fd,now,nf)||!valid(now,nf)||!unchanged(v,now,f,nf)){say("DISPLAY_CHANGED_ABORT\n");break;}
  tick(&g);draw(frame,&g);
  for(int y=0;y<H;y++)for(int x=0;x<W;x++)mem[origin+y*stride+x]=frame[y*W+x];
  long delay[2]={0,50000000};call6(162,(long)delay,0,0,0,0,0);
 }
 if(info(fd,now,nf)&&valid(now,nf)&&unchanged(v,now,f,nf)){
  for(int y=0;y<H;y++)for(int x=0;x<W;x++)mem[origin+y*stride+x]=backup[y*W+x];
  say("SAVED_SCREEN_RESTORED\n");
 }else say("RESTORE_SKIPPED_MODE_CHANGED\n");
 call6(91,mapped,f[5],0,0,0,0);call6(6,fd,0,0,0,0,0);say("XZ_PONG_EXIT\n");return 0;
}
__attribute__((naked,noreturn)) void _start(void){__asm__ volatile("bl run\nmov r7, #1\nsvc 0\nb .");}
