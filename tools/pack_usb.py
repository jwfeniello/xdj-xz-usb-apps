"""Create and verify a USB autoexec package from a flat asset directory."""
import argparse, hashlib, io, re, struct
from pathlib import Path
import pycdlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def effective_key(path):
    lines = Path(path).read_bytes().splitlines()
    if not lines or len(lines[0]) < 31:
        raise ValueError("key file first line must contain at least 31 bytes")
    return lines[0][:31] + bytes(1)

def transform(data, key, decrypt=False):
    if len(data) % 512:
        raise ValueError("payload must be sector-aligned")
    output = bytearray()
    for offset in range(0, len(data), 512):
        iv = struct.pack("<I", offset // 512) + bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        ctx = cipher.decryptor() if decrypt else cipher.encryptor()
        output.extend(ctx.update(data[offset:offset+512]) + ctx.finalize())
    return bytes(output)

def package(assets, key):
    if "autoexec.sh" not in assets or b"\r" in assets["autoexec.sh"]:
        raise ValueError("assets need an LF-only autoexec.sh")
    iso = pycdlib.PyCdlib()
    iso.new(interchange_level=3, rock_ridge="1.09", vol_ident="XZ_USB_APP")
    for name, data in sorted(assets.items()):
        if not re.fullmatch(r"[a-z0-9_]+(?:\.[a-z0-9_]+)?", name):
            raise ValueError(f"unsupported flat asset name: {name}")
        iso.add_fp(io.BytesIO(data), len(data), iso_path="/"+name.upper()+";1", rr_name=name, file_mode=0o100555)
    stream = io.BytesIO()
    iso.write_fp(stream)
    iso.close()
    raw = stream.getvalue()
    encrypted = transform(raw, key)
    recovered = transform(encrypted, key, decrypt=True)
    assert recovered == raw
    check = pycdlib.PyCdlib()
    check.open_fp(io.BytesIO(recovered))
    for name, data in assets.items():
        out = io.BytesIO()
        check.get_file_from_iso_fp(out, rr_path="/"+name)
        assert out.getvalue() == data
        assert check.get_record(rr_path="/"+name).rock_ridge.get_file_mode() & 0o111 == 0o111
    check.close()
    return encrypted

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    entries = list(args.assets.iterdir())
    if any(not f.is_file() or f.is_symlink() for f in entries):
        raise ValueError("assets must contain only regular files")
    assets = {f.name: f.read_bytes() for f in entries}
    if len(assets) != len({name.upper() for name in assets}):
        raise ValueError("asset names collide in ISO")
    if args.output.resolve().parent == args.assets.resolve():
        raise ValueError("output must be outside assets directory")
    result = package(assets, effective_key(args.key_file))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    assert args.output.read_bytes() == result
    print(f"Verified {len(result)} bytes; SHA256 {hashlib.sha256(result).hexdigest()}")

if __name__ == "__main__":
    main()
