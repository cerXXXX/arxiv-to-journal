"""Extract the locked offline wheels; pip and a virtual environment are optional."""
import hashlib
from pathlib import Path
import platform
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def bootstrap():
    if sys.version_info[:2] != (3, 12) or sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise SystemExit('Supported frozen runtime: CPython 3.12 on Linux x86_64 (offline wheels are included).')
    dest = ROOT / '.deps'
    wheels = sorted((ROOT / 'vendor/wheels').glob('*.whl'))
    if len(wheels) != 3:
        raise SystemExit('Expected three locked distribution wheels')
    digest = hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in wheels)).hexdigest()
    stamp = dest / '.wheel-digest'
    if not stamp.exists() or stamp.read_text() != digest:
        dest.mkdir(exist_ok=True)
        for p in wheels:
            with zipfile.ZipFile(p) as archive:
                archive.extractall(dest)
        stamp.write_text(digest)
    sys.path.insert(0, str(dest))
    return dest


if __name__ == '__main__':
    bootstrap()
