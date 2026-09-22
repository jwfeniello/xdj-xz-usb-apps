# Building the examples

The original builds used Zig **0.13.0** and Python. Install the Python dependencies
with `python -m pip install -r requirements.txt`. Put Zig on PATH or pass `--zig`.
ARM Linux static executables avoid depending on the unit's old dynamic libraries.

From the repository root:

```sh
python tools/build_example.py hello
python tools/pack_usb.py --assets build/hello --key-file private/aes256.key --output dist/hello/autoexec.bin
```

The packaging key must be supplied from your own local research inputs. It is not
shipped here; obtaining/extracting that input is outside this initial guide.
The package writer decrypts its output and checks the ISO assets before saving it.
It does not copy anything to a USB drive or modify a device.

For a first device test, boot normally with playback stopped, then place the
resulting `autoexec.bin` at the root of the application USB and insert USB1.
Hello writes `XZ_HELLO<number>/report.txt`; nothing should appear on screen.
Safely remove the drive and inspect the report. This exact example still needs
its first physical test. Preserve any existing launcher before replacing it.

## Pong

```sh
python tools/build_example.py pong
python tools/pack_usb.py --assets build/pong --key-file private/aes256.key --output dist/pong/autoexec.bin
```

The source and launcher come from the tested, presentation-gated demo. It changes
one checked flag in the running stock application to stop competing presentation,
runs roughly 15 seconds of Pong, then restores the flag. The watchdog lasts 25
seconds; allow around 35 seconds before removing the drive. Playback should be
stopped. This historical launcher uses a fixed `XZ_PONG2` report directory and
refuses to run if that directory already exists. Preserve/move an older report
before repeating it. The new portable build has not itself been retested on hardware.

## Effect DSP

From `experiments/fx-dsp`, set the `ZIG` environment variable if Zig is not on PATH:

```sh
python build_reson_tables.py
python build_hook.py
python test_hook.py
python test_bank.py
python test_resonator.py
```

This builds and tests a relocatable ARM processing hook, not a complete USB app.
Tests use Unicorn and mock the stock audio callback. They check numerical behavior,
ABI preservation and cleanup; they do not measure device CPU headroom or audio xruns.
The hardware injector and panel migration are tracked in `docs/status.md`.
