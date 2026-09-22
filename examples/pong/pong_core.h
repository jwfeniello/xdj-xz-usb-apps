#ifndef PONG_CORE_H
#define PONG_CORE_H
typedef unsigned short Pixel;
enum { W=800, H=480 };
typedef struct { int x,y,vx,vy,left,right,ticks; } Game;
static void rect(Pixel *p,int x,int y,int w,int h,Pixel c) {
 if(x<0){w+=x;x=0;} if(y<0){h+=y;y=0;}
 if(x+w>W)w=W-x;
 if(y+h>H)h=H-y;
 for(int j=0;j<h;j++)for(int i=0;i<w;i++)p[(y+j)*W+x+i]=c;
}
static void init_game(Game *g){g->x=400;g->y=220;g->vx=7;g->vy=4;g->left=220;g->right=220;g->ticks=0;}
static int follow(int at,int target){if(at<target-4)at+=5;if(at>target+4)at-=5;if(at<78)at=78;if(at>402)at=402;return at;}
static void tick(Game *g){
 g->ticks++;g->x+=g->vx;g->y+=g->vy;
 if(g->y<48){g->y=48;g->vy=-g->vy;}if(g->y>432){g->y=432;g->vy=-g->vy;}
 g->left=follow(g->left,g->y);g->right=follow(g->right,g->y);
 if(g->x<48){g->x=48;g->vx=7;}if(g->x>752){g->x=752;g->vx=-7;}
}
static void draw(Pixel *p,const Game *g){
 for(int i=0;i<W*H;i++)p[i]=0x0842;
 rect(p,24,28,752,3,0x981f);rect(p,24,449,752,3,0x981f);
 for(int y=44;y<440;y+=24)rect(p,398,y,4,12,0x4208);
 rect(p,32,g->left-36,12,72,0xc29f);rect(p,756,g->right-36,12,72,0xc29f);
 rect(p,g->x-6,g->y-6,12,12,0xffff);
 /* Shrinking bar indicates remaining frames in the 15-second demo. */
 int remain=300-g->ticks;if(remain<0)remain=0;
 rect(p,100,464,remain*2,5,0xc29f);
}
#endif
