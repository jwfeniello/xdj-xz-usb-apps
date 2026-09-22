#include <assert.h>
#include <stdio.h>
#include "pong_core.h"
static Pixel pixels[W*H+2];
int main(void){
 Game g;init_game(&g);pixels[0]=0x1234;pixels[W*H+1]=0xabcd;
 int left=0,right=0,up=0,down=0;
 for(int i=0;i<20000;i++){
  tick(&g);assert(g.x>=48&&g.x<=752&&g.y>=48&&g.y<=432);
  assert(g.left>=78&&g.left<=402&&g.right>=78&&g.right<=402);
  left|=g.vx<0;right|=g.vx>0;up|=g.vy<0;down|=g.vy>0;
  if(i<300){draw(pixels+1,&g);assert(pixels[0]==0x1234&&pixels[W*H+1]==0xabcd);}
 }
 assert(left&&right&&up&&down);
 puts("PASS: 20000 simulation ticks, 300 rendered frames, bounds and canaries.");return 0;
}
