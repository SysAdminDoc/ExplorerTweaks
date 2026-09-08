#!/usr/bin/env python3
"""Reject stale screenshots, altered originals, broken guide links, and icon drift."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image

try:
    from .capture_marketing import SOURCE_PATHS, digest
except ImportError:
    from capture_marketing import SOURCE_PATHS, digest

ORIGINALS = {
    'direction-01-dimensional-folder.png': '2bd106ef47f9c55fd228d9c481bde172a31166e1bf0ca013602a145c758a9af2',
    'direction-02-selected-folder-controls.png': 'f655fa93a8d12c3676e1d070b893e7623c6f78a68311c5c504fc1685413bf27f',
    'direction-03-ribbon-controls.png': '715671200f9db1f4156c4e54dbaa5f3fb65cdd5ce3e69c9b77838adb55e2d2cb',
}
CATEGORIES = ('Appearance', 'Navigation', 'Taskbar', 'Theme', 'Tools')
SIZES = (16, 24, 32, 48, 64, 96, 128, 256, 512, 1024)
EXERCISED = {'category navigation', 'search', 'search restoration', 'file-extension switch',
             'setting explanation', 'dry-run registry plan'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_links(root, document):
    content = document.read_text(encoding='utf-8')
    links = re.findall(r'\]\(([^)]+)\)|src=["\']([^"\']+)["\']', content)
    for markdown, html in links:
        target = markdown or html
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith('#'):
            continue
        path = (document.parent / unquote(parsed.path)).resolve()
        require(path.is_relative_to(root) and path.is_file(), 'Broken local guide link: ' + target)


def verify(root):
    root = Path(root).resolve()
    source = (root / 'explorer_tweaks.py').read_text(encoding='utf-8')
    version = re.search(r'^APP_VERSION = "([0-9.]+)"$', source, re.M)[1]
    readme = (root / 'README.md').read_text(encoding='utf-8')
    require(f'# ExplorerTweaks v{version}' in readme and f'badge/version-{version}-' in readme,
            'README version differs from the product.')
    require(f'/v{version}/ExplorerTweaks-v{version}-win64.zip' in readme, 'Download link is stale.')
    metadata = (root / 'version_info.txt').read_text(encoding='utf-8')
    numeric = ', '.join(version.split('.') + ['0'])
    require(all(token in metadata for token in (f'filevers=({numeric})', f'prodvers=({numeric})',
                f"u'FileVersion', u'{version}.0'", f"u'ProductVersion', u'{version}.0'")), 'Executable version metadata differs.')
    for disclosure in ('switches apply immediately', 'sample configuration', "isn't Authenticode-signed"):
        require(disclosure in readme, 'Missing release disclosure: ' + disclosure)
    for relative in ('README.md', 'assets/brand/concepts/README.md', 'assets/marketing/README.md'):
        verify_links(root, root / relative)
    social = root / 'assets/marketing/social-card.png'
    require(digest(social) == digest(root / 'assets/brand/concepts/share-card-concept.png'),
            'Share artwork differs from the archived concept.')
    with Image.open(social) as picture:
        require(picture.format == 'PNG' and picture.width >= 1280 and picture.width == 2 * picture.height
                and social.stat().st_size < 1_000_000, 'Share artwork does not meet the upload requirements.')

    archive = root / 'assets/brand/concepts'
    for name, expected in ORIGINALS.items():
        require(digest(archive / name) == expected, 'Original artwork changed: ' + name)
        with Image.open(archive / name) as picture:
            require(picture.mode == 'RGBA' and picture.getextrema()[3][0] == 0,
                    'Original artwork lost real transparency: ' + name)
    selected = 'direction-02-selected-folder-controls.png'
    master = root / 'assets/brand/explorertweaks-mark-master.png'
    require(digest(master) == ORIGINALS[selected], 'Approved master differs from the supplied original.')
    selection = json.loads((archive / 'selection.json').read_text(encoding='utf-8-sig'))
    require(selection['selectedConcepts'] == [selected]
            and selection['selectedMasters'] == ['../explorertweaks-mark-master.png'], 'Approved selection changed.')
    with Image.open(master) as picture:
        mark = picture.crop(picture.getchannel('A').getbbox())
        mark.thumbnail((896, 896), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (1024, 1024))
        canvas.alpha_composite(mark, ((1024 - mark.width) // 2, (1024 - mark.height) // 2))
    for size in SIZES:
        with Image.open(root / f'branding/icon-{size}.png') as picture:
            expected = canvas.resize((size, size), Image.Resampling.LANCZOS)
            require(picture.mode == 'RGBA' and picture.size == (size, size)
                    and picture.tobytes() == expected.tobytes(), f'Icon export drift at {size}px.')
    with Image.open(root / 'branding/icon.ico') as icon:
        require(icon.ico.sizes() == {(size, size) for size in SIZES if size <= 256}, 'Missing Windows icon sizes.')

    shots = root / 'assets/screenshots'
    report = json.loads((shots / 'capture-report.json').read_text(encoding='utf-8'))
    require(report['schemaVersion'] == 1 and report['product'] == 'ExplorerTweaks'
            and report['version'] == version, 'Capture product or version is stale.')
    require(report['sampleData'] is True and report['privateDesktop'] is True
            and report['systemCommands'] is False, 'Capture isolation evidence is missing.')
    records = report['sourceFiles']
    require(len(records) == len(SOURCE_PATHS) and {item['path'] for item in records} == set(SOURCE_PATHS),
            'Runtime source inventory differs.')
    for item in records:
        path = root / item['path']
        require(path.stat().st_size == item['bytes'] and digest(path) == item['sha256'],
                'Capture source changed: ' + item['path'])
    captures = report['captures']
    names = [f'{index:02d}-{category.lower()}.png' for index, category in enumerate(CATEGORIES, 1)]
    require(len(captures) == len(names) and [item['file'] for item in captures] == names,
            'Capture inventory differs.')
    require([item['category'] for item in captures] == list(CATEGORIES), 'Capture categories differ.')
    require(len({item['sha256'] for item in captures}) == len(names), 'Duplicate screenshots.')
    for item in captures:
        path = shots / item['file']
        require(item['width'] == 1600 and item['height'] == 1000, 'Recorded screenshot dimensions differ.')
        require(path.stat().st_size == item['bytes'] and digest(path) == item['sha256'],
                'Screenshot changed: ' + item['file'])
        with Image.open(path) as picture:
            require(picture.format == 'PNG' and picture.size == (1600, 1000), 'Invalid screenshot format or size.')
            require(any(low != high for low, high in picture.convert('RGB').getextrema()), 'Blank screenshot.')
    require(digest(root / 'screenshot.png') == captures[0]['sha256'], 'Legacy screenshot is stale.')
    require(EXERCISED <= set(report['exercised']), 'Product interactions were not exercised.')
    layout, = report['layouts']
    require(layout['component'] == 'Taskbar' and layout['width'] >= layout['tray'] + layout['icons'] + 30,
            'Taskbar illustration is clipped.')
    return dict(version=version, originals=len(ORIGINALS), screenshots=len(captures), iconSizes=len(SIZES))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    print(json.dumps(verify(parser.parse_args().root), indent=2))
