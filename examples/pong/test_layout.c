#include <assert.h>
#include <stdio.h>
#include "pong_core.h"
typedef unsigned int U;
static int valid(U *v,U *f){
 return v[0]==W&&v[1]==H&&v[2]>=W&&v[2]<=4096&&v[3]>=H&&v[3]<=4096&&v[4]<=v[2]-W&&v[5]<=v[3]-H
 &&v[6]==16&&v[7]==0&&v[8]==11&&v[9]==5&&v[10]==0&&v[11]==5&&v[12]==6&&v[13]==0
 &&v[14]==0&&v[15]==5&&v[16]==0&&v[18]==0&&v[20]==0&&f[6]==0&&f[8]==2
 &&f[11]>=v[2]*2&&f[11]<=8192&&(f[11]&1)==0&&f[5]>0&&f[5]<=16777216
 &&(v[5]+H-1)*f[11]+(v[4]+W)*2<=f[5];
}
static int unchanged(U*a,U*b,U*fa,U*fb){for(int i=0;i<21;i++)if(a[i]!=b[i])return 0;for(int i=4;i<12;i++)if(fa[i]!=fb[i])return 0;return 1;}

int main(void){
 U v[40]={0},f[20]={0};
 v[0]=800;v[1]=480;v[2]=800;v[3]=480;v[6]=16;
 v[8]=11;v[9]=5;v[11]=5;v[12]=6;v[15]=5;
 f[5]=800*480*2;f[8]=2;f[11]=1600;
 assert(valid(v,f));assert(unchanged(v,v,f,f));
 f[5]--;assert(!valid(v,f));f[5]++;
 v[6]=32;assert(!valid(v,f));v[6]=16;
 v[4]=1;assert(!valid(v,f));v[4]=0;
 v[5]=1;assert(!valid(v,f));v[5]=0;
 f[11]=1598;assert(!valid(v,f));f[11]=1601;assert(!valid(v,f));f[11]=1600;
 v[9]=6;assert(!valid(v,f));v[9]=5;
 f[6]=1;assert(!valid(v,f));f[6]=0;
 v[2]=1024;v[3]=960;v[4]=100;v[5]=480;f[11]=2048;f[5]=2048*960;assert(valid(v,f));
 f[5]=0xffffffff;assert(!valid(v,f));
 puts("PASS: display geometry, bounds, format, stride, offsets and size refusal tests.");return 0;
}
