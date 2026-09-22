# USB applications on the XDJ-XZ

Running custom applications from a USB drive on an otherwise stock Pioneer XDJ-XZ.
No hardware modification or firmware flashing is required for the experiments
here. Some applications temporarily change the running software in RAM. Rebooting
returns the device to normal operation; applications can leave logs on the USB.

Tested on **firmware 1.25**. Other firmware versions are not validated.

This started with a logo experiment and grew into games, emulators, a live screen
overlay, and audio effects. The interesting part is the launch mechanism: the
stock software already has a path for running a packaged application from USB.
The rest of this repository documents how to use the hardware once code is running.

## Start here

- [How the USB launch works](docs/usb-launch.md)
- [Build and package an application](docs/building.md)
- [Hardware interfaces and firmware-specific addresses](docs/interfaces.md)
- [What has actually been tested](docs/status.md)
- [Things that went wrong](docs/lessons.md)

## In this repository

| Directory | Contents |
| --- | --- |
| `examples/hello` | Small log-only application; the easiest place to start |
| `examples/pong` | Source from the presentation-gated Pong experiment |
| `experiments/fx-dsp` | Effect algorithms, ARM hook, and instruction-emulation tests |
| `tools` | ARM example builder and USB package writer |
| `captures` | Selected results from physical tests |

The local experiments have also run Game Boy, Genesis and ScummVM applications.
Full prebuilt Sonic and Pok?mon packages, including their bundled game data,
are available in the [private releases](docs/releases.md). Emulator source snapshots
accompany those downloads; the ports are not yet integrated into this source tree. The complete effect-bank injector/UI is also still being prepared;
`fx-dsp` is the processing core, not a ready-to-install effect application.

## Current limits

This is research code, not a supported application platform. Our custom live DSP
currently processes Deck 1, not arbitrary mixer channels. Returning from tested
applications works, but recovering from every possible crash is not established.
A service-mode USB prompt does not demonstrate recovery from damaged firmware.
None of these experiments requires a firmware update.

Long-running applications need to release the stock USB launch handler. See the
launch notes before adapting a desktop program or running it during playback.
Firmware images, extracted vendor libraries and packaging keys are absent.
The source tree excludes ROMs and commercial game data; the private archival
releases described above do contain the bundled games.

## About the notes

Hardware testing and interpretation were done through an iterative research
session with AI assistance for code, tooling and analysis. Physical observations,
emulator checks and unresolved assumptions are identified separately.

This private repository is being assembled from the working research directory.
A redistribution license for the original project code has not been selected yet.
