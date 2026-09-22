# Private prebuilt game releases

The release assets preserve the existing complete builds, including bundled game
data. They are private archival prereleases, separate from the source-only tree.
Do not treat them as ROM-free public emulator distributions.

- [Pok?mon Red unlimited](https://github.com/jwfeniello/xdj-xz-usb-apps/releases/tag/pokemon-red-v0.2): complete application ZIP and matching Peanut-GB/frontend source.
- [Sonic builds](https://github.com/jwfeniello/xdj-xz-usb-apps/releases/tag/sonic-v0.2): silent build, experimental audio build, and PicoDrive/component/frontend source snapshot.

Each application ZIP has an `autoexec.bin` to copy to the USB root, controls,
limitations, hash and notices. Only one `autoexec.bin` can occupy the root at a
time. No compilation is needed for these downloads. Firmware 1.25 only; use
normal boot and stop both decks before launching. Follow the included exit steps.

Pok?mon has no sound or persistent saves. Its original timed build was tested on
hardware; the unlimited revision lacks a recorded dedicated physical test.
Sonic silent was hardware-tested; Sonic audio remains experimental with recorded
underruns. Source snapshots retain original build paths requiring local adjustment.
Encryption keys and toolchains are not included.
