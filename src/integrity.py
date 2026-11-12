"""Integrity checks for frozen inputs and byte-identical generated deliverables."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs():
    return sorted(p for folder in ['data/raw', 'data/reference', 'data/review', 'vendor']
                  for p in (ROOT / folder).rglob('*') if p.is_file())


def result_paths():
    return sorted(p for p in (ROOT/'results').rglob('*') if p.is_file())


def write_manifest(manifest, paths):
    manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in paths), encoding='utf-8')


def verify(manifest, paths):
    expected = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        h, name = line.split('  ', 1)
        expected[name] = h
    actual = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    differences = sorted(set(expected) ^ set(actual)) + sorted(k for k in expected.keys() & actual.keys() if expected[k] != actual[k])
    if differences:
        raise SystemExit('Integrity mismatch: ' + ', '.join(differences))
    print(f'OK: {len(actual)} files match {manifest.name}')


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'freeze-inputs':
        write_manifest(ROOT/'INPUTS.sha256', inputs())
    elif action == 'freeze-results':
        write_manifest(ROOT/'EXPECTED_RESULTS.sha256', result_paths())
    elif action == 'verify':
        verify(ROOT/'INPUTS.sha256', inputs())
    elif action == 'results':
        verify(ROOT/'EXPECTED_RESULTS.sha256', result_paths())
    else:
        raise SystemExit('Unknown integrity action')
