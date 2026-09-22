import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from pack_usb import effective_key, package, transform

class PackagingTests(unittest.TestCase):
    def test_key_copy_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            keyfile = Path(folder) / "test.key"
            keyfile.write_bytes(b"0123456789abcdefghijklmnopqrstuVignored\n")
            key = effective_key(keyfile)
            self.assertEqual(key, b"0123456789abcdefghijklmnopqrstu" + bytes(1))
            blob = package({"autoexec.sh": b"#!/bin/sh\nexit 0\n", "hello": b"test fixture"}, key)
            raw = transform(blob, key, decrypt=True)
            self.assertEqual(raw[0x8000:0x8007], b"\x01CD001\x01")
            self.assertNotEqual(blob, raw)
    def test_invalid_assets(self):
        for assets in [{}, {"autoexec.sh": b"#!/bin/sh\r\n"}, {"autoexec.sh": b"x", "../escape": b"x"}]:
            with self.assertRaises(ValueError): package(assets, bytes(32))
    def test_sector_alignment(self):
        with self.assertRaises(ValueError): transform(b"bad", bytes(32))

if __name__ == "__main__": unittest.main()
