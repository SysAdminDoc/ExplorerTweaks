#!/usr/bin/env python3
"""Regression checks for the product states shown in the guide."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import explorer_tweaks as product
from tools import capture_marketing, verify_marketing

ROOT = Path(__file__).resolve().parents[1]


class PreviewAccuracyTests(unittest.TestCase):
    def test_policy_locked_switch_does_not_write_and_restores_its_state(self):
        card = SimpleNamespace(_policy_locked=True, setting=SimpleNamespace(name='Policy controlled',
            enable_value=1, disable_value=0, reg_path='example', reg_name='value', reg_type='DWORD'),
            switch_var=Mock(get=Mock(return_value=True)), on_change=Mock(), _load_state=Mock())
        with patch.object(product.messagebox, 'showwarning') as warning, patch.object(product, 'set_registry_value') as write:
            product.SettingCard._toggle(card)
        warning.assert_called_once()
        write.assert_not_called()
        card._load_state.assert_called_once()
        card.on_change.assert_not_called()

    def test_marketing_setting_count_matches_the_catalog(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn(f'contains {len(product.get_all_settings())} registry settings', readme)
        self.assertNotIn('Maximum privacy', product.BUILTIN_PRESETS['Privacy']['description'])
        self.assertIn('selected Windows', product.BUILTIN_PRESETS['Privacy']['description'])

    def test_taskbar_colors_are_valid_tk_rgb_values(self):
        for palette in (product.TASKBAR_DARK, product.TASKBAR_LIGHT):
            for name, color in palette.items():
                with self.subTest(name=name, color=color):
                    self.assertRegex(color, r'^#[0-9a-fA-F]{6}$')

    def test_inverted_registry_settings_match_preview_and_switch_defaults(self):
        for value in (None, 0, 1):
            with self.subTest(value=value):
                app = SimpleNamespace(preview_state=product.PreviewState(), os_version=product.OSVersion.WINDOWS_11_25H2)
                with patch.object(product, 'get_registry_value', return_value=value), patch.object(product.SpecialSettings, 'get_classic_context_menu', return_value=False), patch.object(product.SpecialSettings, 'get_search_mode', return_value=1):
                    product.App._load_preview_state(app)
                self.assertEqual(app.preview_state.show_extensions, value == 0)
                self.assertEqual(app.preview_state.show_thumbnails, value != 1)


class CaptureSafetyTests(unittest.TestCase):
    def test_normal_start_does_not_create_a_private_capture_session(self):
        with patch.object(capture_marketing.ctypes, 'WinDLL', side_effect=AssertionError('Unexpected desktop API')):
            capture_marketing.prepare(['explorer_tweaks.py'])
            capture_marketing.prepare(['explorer_tweaks.py', '--dry-run'])
        self.assertIsNone(capture_marketing.SESSION)

    def test_capture_rejects_combined_commands_before_opening_a_desktop(self):
        with patch.object(capture_marketing.ctypes, 'WinDLL', side_effect=AssertionError('Unexpected desktop API')):
            for argv in (['app', '--marketing-capture'], ['app', '--marketing-capture', 'sample', '--wipe-recent'],
                         ['app', '--apply', 'settings.json', '--marketing-capture', 'sample']):
                with self.subTest(argv=argv), self.assertRaisesRegex(ValueError, 'alone'):
                    capture_marketing.prepare(argv)

    def test_capture_blocks_mutating_registry_and_process_events(self):
        for event in ('winreg.SetValue', 'winreg.SetValueEx', 'winreg.CreateKey', 'winreg.DeleteKey',
                      'winreg.DeleteValue', 'subprocess.Popen', 'os.system', 'os.startfile', 'os.startfile/2'):
            with self.subTest(event=event), self.assertRaisesRegex(RuntimeError, 'disabled'):
                capture_marketing.reject_system_mutation(event, ())
        capture_marketing.reject_system_mutation('winreg.OpenKey', ())


class MarketingEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='explorertweaks-evidence-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for folder in ('assets', 'branding'):
            shutil.copytree(ROOT / folder, self.root / folder)
        for relative in (*capture_marketing.SOURCE_PATHS, 'README.md', 'LICENSE', 'screenshot.png',
                         'version_info.txt', 'tools/render_readme_hero.py'):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        self.report_path = self.root / 'assets/screenshots/capture-report.json'
        self.report = json.loads(self.report_path.read_text(encoding='utf-8'))

    def save_report(self):
        self.report_path.write_text(json.dumps(self.report), encoding='utf-8')

    def test_current_assets_pass(self):
        self.assertEqual(verify_marketing.verify(self.root)['screenshots'], 5)

    def test_changed_original_is_rejected(self):
        path = self.root / 'assets/brand/concepts/direction-01-dimensional-folder.png'
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'Original artwork changed'):
            verify_marketing.verify(self.root)

    def test_stale_source_is_rejected(self):
        path = self.root / 'tools/capture_marketing.py'
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaisesRegex(ValueError, 'Capture source changed'):
            verify_marketing.verify(self.root)

    def test_missing_capture_is_rejected(self):
        self.report['captures'].pop()
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'Capture inventory'):
            verify_marketing.verify(self.root)

    def test_duplicate_capture_is_rejected(self):
        self.report['captures'][1]['sha256'] = self.report['captures'][0]['sha256']
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'Duplicate screenshots'):
            verify_marketing.verify(self.root)

    def test_system_commands_enabled_is_rejected(self):
        self.report['systemCommands'] = True
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'isolation'):
            verify_marketing.verify(self.root)

    def test_broken_local_image_is_rejected(self):
        path = self.root / 'README.md'
        path.write_text(path.read_text(encoding='utf-8') + '\n![Missing](assets/missing.png)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Broken local guide link'):
            verify_marketing.verify(self.root)

    def test_readme_rejects_a_duplicate_hero(self):
        path = self.root / 'README.md'
        path.write_text(path.read_text(encoding='utf-8') +
                        '\n![Repeated hero](assets/marketing/readme-hero.png)\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'exactly once'):
            verify_marketing.verify(self.root)

    def test_readme_rejects_content_before_the_hero(self):
        path = self.root / 'README.md'
        path.write_text('# Content before the hero\n\n' + path.read_text(encoding='utf-8'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'first README content'):
            verify_marketing.verify(self.root)

    def test_changed_readme_hero_is_rejected(self):
        path = self.root / 'assets/marketing/readme-hero.png'
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'archived final'):
            verify_marketing.verify(self.root)

    def test_clipped_taskbar_is_rejected(self):
        self.report['layouts'][0]['width'] = 1
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'Taskbar illustration is clipped'):
            verify_marketing.verify(self.root)

    def test_numeric_version_drift_is_rejected(self):
        path = self.root / 'version_info.txt'
        path.write_text(path.read_text(encoding='utf-8').replace('filevers=(2, 16, 2, 0)', 'filevers=(1, 0, 0, 0)'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'version metadata'):
            verify_marketing.verify(self.root)


if __name__ == '__main__':
    unittest.main()
