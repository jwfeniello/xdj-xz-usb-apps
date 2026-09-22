# Things that went wrong

## Pong flashed between two screens

Both Pong and the stock UI were presenting. Drawing faster did not solve the
ownership problem. Gating stock presentation during the short game fixed that
experiment. Live overlays later needed a different approach that preserves stock
updates rather than disabling the whole screen.

## A launcher failed before its panel appeared

The touch-hook startup check assumed `read` came from libc. On the device it
resolved to libpthread. Accepting either verified implementation fixed the
compatibility check. The old logs did not identify the failed startup check;
named checks made subsequent failures easier to interpret.

## The panel felt slow even though the display updated

The controller imposed an 80 ms redraw delay. Dirty-state redraw, a shorter
interval, touch-down actions and reduced USB logging helped. Display presentation
FPS and panel publication FPS are different measurements. The largest measured
wrapper time also includes waiting in the original Flip call, not just drawing.

## Switching away from DELAY disabled the custom effect

The controller cleared enable intent when the selector left its permitted
position. Returning therefore left it off. Separating requested enable state
from temporary selector/stock-FX gating fixed it. Hiding the panel now leaves
audio active and keeps the launcher available.

## The vowel filter was too subtle

At maximum wet it still mixed in 30% dry, and maximum brightness removed one of
the two resonances. VOWEL now reaches 100% wet, retains both peaks, and uses more
filtered gain with soft saturation. Other effects retain their 70% cap.

These are observations from the development sessions, not claims that the entire
firmware or hardware has been mapped.
