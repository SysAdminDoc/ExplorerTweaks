#!/usr/bin/env python3
"""Build provenance and an offline release package from verified source assets."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import zipfile

from capture_marketing import SOURCE_PATHS, digest

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.search(r'^APP_VERSION = "([0-9.]+)"', (ROOT / 'explorer_tweaks.py').read_text(encoding='utf-8'), re.M)[1]


def write_provenance():
    metadata = (ROOT / 'version_info.txt').read_text(encoding='utf-8')
    numeric = ', '.join(VERSION.split('.') + ['0'])
    for token in (f'filevers=({numeric})', f'prodvers=({numeric})', f"u'{VERSION}.0'"):
        if token not in metadata:
            raise ValueError('Executable version metadata is stale: ' + token)
    payload = dict(product='ExplorerTweaks', version=VERSION, python=platform.python_version(), sourceFiles=[dict(path=name, bytes=(ROOT / name).stat().st_size, sha256=digest(ROOT / name)) for name in SOURCE_PATHS])
    output = ROOT / 'build/build-provenance.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def package():
    from verify_marketing import verify
    verify(ROOT)
    binary = ROOT / 'dist/ExplorerTweaks.exe'
    if not binary.is_file():
        raise ValueError('Build the executable first.')
    provenance = ROOT / 'build/build-provenance.json'
    recorded = json.loads(provenance.read_text(encoding='utf-8'))
    if recorded['version'] != VERSION or any(digest(ROOT / item['path']) != item['sha256'] for item in recorded['sourceFiles']):
        raise ValueError('Runtime source changed after the executable build.')
    with tempfile.TemporaryDirectory(prefix='explorertweaks-package-capture-') as temporary:
        capture_dir = Path(temporary)
        subprocess.run([str(binary), '--marketing-capture', str(capture_dir)], check=True,
                       timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
        capture_bytes = (capture_dir / 'capture-report.json').read_text(encoding='utf-8').encode('utf-8')
        capture_report = json.loads(capture_bytes)
        if (capture_report['executableSha256'] != digest(binary)
                or capture_report['sourceFiles'] != recorded['sourceFiles']
                or capture_report['version'] != VERSION
                or capture_report['privateDesktop'] is not True
                or capture_report['sampleData'] is not True
                or capture_report['systemCommands'] is not False):
            raise ValueError('Executable capture provenance differs.')
        approved = json.loads((ROOT / 'assets/screenshots/capture-report.json').read_text(encoding='utf-8'))
        if capture_report['captures'] != approved['captures'] or capture_report['exercised'] != approved['exercised']:
            raise ValueError('Executable screenshots differ. Review new candidates before packaging.')
        if any(digest(capture_dir / item['file']) != item['sha256'] for item in approved['captures']):
            raise ValueError('Executable screenshot bytes differ from the accepted guide.')
    files = {'ExplorerTweaks.exe': binary, 'README.md': ROOT / 'README.md', 'LICENSE': ROOT / 'LICENSE', 'build-provenance.json': provenance}
    for folder in ('assets', 'branding'):
        for path in (ROOT / folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                files[path.relative_to(ROOT).as_posix()] = path
    payloads = {name: path.read_bytes() for name, path in files.items()}
    payloads['assets/screenshots/capture-report.json'] = capture_bytes
    payloads['INSTALL.txt'] = (f'ExplorerTweaks v{VERSION}\n\nExtract this folder and run ExplorerTweaks.exe. Normal GUI switches apply immediately. Read README.md and export a profile before changing settings.\n\nThe executable is unsigned unless its Windows signature reports a trusted publisher. Verify the release checksum.\n\nBefore deleting the app, remove any Shell Menu and Auto Dark integrations you installed. Deleting the app does not undo registry changes. Restore your saved profile or backup separately.\n').encode('utf-8')
    # Keep the licenses of installed application dependencies in the download.
    for name in ('customtkinter', 'darkdetect', 'packaging', 'pillow'):
        distribution = importlib.metadata.distribution(name)
        licenses = [item for item in distribution.files or [] if any(part.lower().startswith(('license', 'copying')) for part in item.parts)]
        if not licenses:
            raise ValueError('No bundled license found for ' + name)
        for item in licenses:
            path = Path(distribution.locate_file(item))
            if path.is_file():
                payloads[f'licenses/{name}/{item.as_posix()}'] = path.read_bytes()
    python_root = Path(sys.base_prefix)
    license_files = [python_root / 'LICENSE.txt', python_root / 'tcl/tk8.6/license.terms']
    for path in license_files:
        if not path.is_file():
            raise ValueError('Missing interpreter or Tk license: ' + str(path))
        payloads['licenses/python/' + path.relative_to(python_root).as_posix()] = path.read_bytes()
    manifest = dict(product='ExplorerTweaks', version=VERSION, files=[dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) for name, data in sorted(payloads.items())])
    payloads['release-manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    if any(Path(name).is_absolute() or '..' in Path(name).parts for name in payloads):
        raise ValueError('Unsafe release archive path.')
    archive = ROOT / f'dist/ExplorerTweaks-v{VERSION}-win64.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != set(payloads) or any(bundle.read(name) != data for name, data in payloads.items()):
            raise ValueError('ZIP differs from verified package inputs.')
    outputs = [dict(file=path.name, bytes=path.stat().st_size, sha256=digest(path)) for path in (binary, archive)]
    (ROOT / f'dist/ExplorerTweaks-v{VERSION}-SHA256SUMS.txt').write_text(''.join(f"{item['sha256']}  {item['file']}\n" for item in outputs), encoding='ascii')
    (ROOT / 'dist/release-manifest.json').write_text(json.dumps(dict(product='ExplorerTweaks', version=VERSION, artifacts=outputs, packagedFileCount=len(payloads)), indent=2) + '\n', encoding='utf-8')
    print(f'Verified exact {len(payloads)}-file ZIP: {archive}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--provenance', action='store_true')
    mode.add_argument('--package', action='store_true')
    options = parser.parse_args()
    write_provenance() if options.provenance else package()
