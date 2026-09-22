typedef unsigned int U;
enum { ENABLED,FRAMES,TOTAL,CALLS,PROCESSED,DRY,BUFFER,RING,FAULT,WROTE,
 WRITEPOS,FILLED,PHASE,LENGTH,HEAD0,HEAD1,SEED,WET,COMMAND,LEASE,WATCHDOG,ACTIVE_FX,ACTIVE_CMD,OSC_PHASE,SLICE_STEP,FILTER_STATE,
 RESON_NOTES=40,ACTIVE_NOTES,RESON_STATE,STATE_WORDS=72 };
#define RING_FRAMES 65536u
#define AUDIO_RING_OFFSET 16384u
#define TEST_FRAMES 7938048u
static inline U pack_command(U on,U freeze,U reverse,U size,U scatter,U mix){
 return (on&1)|((freeze&1)<<1)|((reverse&1)<<2)|((size&255)<<4)|((scatter&255)<<12)|((mix&255)<<20);
}

static inline U pack_bank(U on,U freeze,U reverse,U size,U scatter,U mix,U effect){return pack_command(on,freeze,reverse,size,scatter,mix)|((effect&7)<<28);}
