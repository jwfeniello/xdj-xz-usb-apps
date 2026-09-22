# Effect-processing core

Original DSP source and the ARM callback wrapper from the RAM-only effect bank.
See ../../docs/building.md for commands and ../../docs/status.md for evidence.
No firmware, packaging keys, library instruction signatures or system-font data
are included. This folder alone is not a runnable USB application: the injector,
control reader, panel and launcher still need migration.

`build_hook.py` compiles position-independent objects separately, then verifies
that the linked payload has no unresolved symbols or relocation requirements.
`build_reson_tables.py` generates note rotations and decay constants offline.
The processing callback allocates nothing and calls no external math functions.

Physical feedback exists for the four-effect bank. The resonator tests measure
pitch and decay in instruction emulation; a physical result is still pending.
