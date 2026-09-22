# Evidence and remaining work

Status as of 2026-09-22. Physical reports refer to the original workspace builds;
portable repository builds need their own hardware confirmation.

| Work | Evidence | Limit |
| --- | --- | --- |
| USB-packaged native applications | Multiple physical launches | Firmware 1.25 only |
| Pong with presentation gating | Device log and user confirmation | Early timed demo, stopped playback |
| Jog-wheel/button input | Physical control tests and working games | Not every control is mapped |
| Game Boy and Genesis | User reports working games | Prebuilt private releases; source snapshots attached |
| ScummVM | User reports working Pajama Sam | Jog mouse, silent tested build; no touch integration |
| Touch coordinates | Physical corner/drag capture | Single contact; release bounce observed |
| Live overlay | Physical runs around 31 presentations/s | UI updates can be slower; occasional stalls |
| Four-effect bank | All effects used; clean timed runs | Deck 1 only; stock Beat FX must be off |
| Stronger vowel filter | Full physical timed run and sweep logged | Subjective sound feedback not recorded |
| Note-selectable resonator | 48 pitches and decay tested in ARM emulation | Built for USB; physical result not yet recorded |

The current DSP tests cover GRAINS, SCRAMBLE, ROBOT, VOWEL and RESONATOR. Resonator
supports up to three selected pitch classes in octaves 2-5. TIME sets nominal
0.1-3-second decay. Runtime in the complete local app is limited to three minutes.

## Repository work still to do

- Migrate the complete overlay, control reader and injector with portable builds.
- Replace locally generated system-font atlases with reproducible distributable assets.
- Integrate the emulator release-source snapshots into portable source builds.
- Add a video showing USB insertion, application launch and reboot to stock.
- Test the new hello example and portable builds on the actual deck.
- Choose a license before considering a public release.

These items do not change the visibility of this repository. No public release,
Pages site or external announcement has been made. Private archival game prereleases were added at the owner's request.
