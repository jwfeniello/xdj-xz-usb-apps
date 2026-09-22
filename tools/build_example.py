"""Build an ARM example into build/<name>; does not touch USB devices."""
import argparse, os, shutil, subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", choices=["hello", "pong"])
    parser.add_argument("--zig", default=os.environ.get("ZIG", "zig"))
    args = parser.parse_args()
    source = ROOT / "examples" / args.example
    output = ROOT / "build" / args.example
    output.mkdir(parents=True, exist_ok=True)
    binary = output / args.example
    command = [args.zig, "cc", "-target", "arm-linux-musleabi", "-mcpu=cortex_a9", "-mfloat-abi=soft", "-marm", "-Os", "-static", "-no-pie"]
    if args.example == "pong":
        command += ["-nostdlib", "-fno-stack-protector", "-fno-builtin", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wl,-e,_start", "-Wl,--build-id=none"]
    command += [str(source / (args.example + ".c")), "-o", str(binary)]
    subprocess.run(command, check=True)
    with binary.open("rb") as stream:
        elf = ELFFile(stream)
        assert elf.elfclass == 32 and elf.little_endian and elf["e_machine"] == "EM_ARM"
        assert elf["e_type"] == "ET_EXEC" and not elf["e_flags"] & 0x400
        assert not any(s["p_type"] in ("PT_INTERP", "PT_DYNAMIC") for s in elf.iter_segments())
    shutil.copyfile(source / "autoexec.sh", output / "autoexec.sh")
    print(f"Built static ARM example: {output}")

if __name__ == "__main__":
    main()
