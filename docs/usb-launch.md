# USB launch mechanism

On the tested 1.25 system, `autoexec.bin` at the root of a USB drive is used by an
existing application-launch path. It is an encrypted ISO containing `autoexec.sh`
and its payload. The package is mounted at `/mnt/iso`, and the launcher receives
the USB mount path as its first argument. This is not the `.UPD` firmware-update
format and does not use the update footer.

The experiments use an ISO9660 filesystem with Rock Ridge filenames and executable
permissions. Encryption follows the device's existing cryptoloop convention:
AES-256-CBC, independently for each 512-byte sector. The IV is the sector number
as a little-endian 32-bit value followed by twelve zero bytes. The key derivation
matches the observed util-linux string-copy behavior: first 31 bytes of the key
file's first line, then a NUL. The key itself is not in this repository.

## Application lifetime

The shell launcher must return for the stock mount notification to finish.
Blocking it with a game can prevent normal USB browsing. Later experiments copy
the executable into `/dev/shm`, change working directory away from the mounted
ISO, and detach the worker. The script then returns. The worker must arrange its
own cleanup and log output. The early Pong example deliberately blocks for a
short, stopped-playback test and is not the pattern for a long-running player.

Use separate drives for application testing (USB1) and music (USB2) when following
the audio experiments. Tested hooks are temporary RAM writes to the running
application, not persistent installation. Reboot with the application USB removed
to avoid immediately launching it again.

The small hello example only executes briefly and writes a new report directory.
It does not change process memory, the screen, input routing or audio. This new
minimal example is locally build/package-tested; the underlying launch mechanism
has been tested with the earlier applications, not this exact hello build yet.
