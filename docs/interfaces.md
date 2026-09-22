# Interfaces found so far

Addresses below refer to the exact **1.25 ARM application**, not the 1.26 image
used in some earlier disassembly sessions. The running application's MD5 in the
tested launcher is `03722341b24045b36d3869b0c4c9968c`. An address by itself is not
a sufficient compatibility check; tested injectors also verify layouts and methods.

## Display

The main display is 800 x 480 RGB565. Direct framebuffer drawing works, but the
stock application can immediately draw over it. Early Pong avoided that by
clearing presentation bit 0 in layer 0's checked flags at `0x01afada8`. The layer
stride is 164 bytes. Later overlays wrap the surface's DirectFB Flip method,
save the affected back-buffer pixels, draw the panel, present by copy and restore
the pixels. A clean frame is required before removing that hook to avoid ghosts.

## Touch

Manager pointer: `0x01c8a208`; its `+0x74` member points to the touch object.
Processed pressed/X/Y fields are at `+0xdc`, `+0xe0`, `+0xe4`. Processed coordinates
increase rightward and downward. Read stable snapshots; do not invert again.
A physical capture observed release bounce around 20 ms. The later UI uses a
60 ms release grace while reacting to button touch-down immediately.

Selective touch forwarding intercepts the verified touch read call and suppresses
only gestures that begin inside the overlay. Ownership remains fixed through a
drag. Original-firmware instruction emulation passes outside-touch comparisons;
recent physical captures contain no outside gestures, so that part remains an
on-device validation gap.

## Controls

Manager `+0x50` points to the mixer object. Its cached 56-byte status frame starts
at `+0x17c`. Offset 30 holds the effect selector, 31 the stock FX on/off state,
and 36-37 the little-endian TIME value. Read twice and reject unstable copies.
Rebase TIME after selector changes; each stock effect can have a different value.
Continuous LEVEL/DEPTH is not established on this ARM-readable path.

## Audio

The tested Deck 1 interception point follows the original callback at `0x3f078`.
Engine singleton: `0x010e95e8`; original vtable pointer: `0x003cf2d0`.
Blocks contain 64 stereo frames of interleaved float data at 44.1 kHz. Preserve
Deck 2 and the original callback/postcallback contracts. A previous wet block
must be completely cleared before a paused stock callback that only clears half
of the stereo buffer. The tests include this failure case.

The mixer has separate SuperH and TI DSP components. The RAM-only ARM audio hook
does not replace their firmware algorithms or gain their arbitrary channel routing.
