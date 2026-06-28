import contextlib
import io
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

import explorer_tweaks as et


class DeploymentHelperTests(unittest.TestCase):
    def test_profile_registry_entries_convert_inverted_bool_and_specials(self):
        setting = et.RegistrySetting(
            id="show_extensions",
            name="Show File Extensions",
            description="Display extensions",
            category="Appearance",
            subcategory="File Display",
            reg_path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            reg_name="HideFileExt",
            reg_type="DWORD",
            enable_value=0,
            disable_value=1,
            default_value=1,
            inverted=True,
        )

        entries, special = et.profile_registry_entries(
            {
                "show_extensions": True,
                "classic_context_menu": True,
                "search_mode": 1,
            },
            [setting],
        )

        self.assertEqual(entries[0]["value"], 0)
        self.assertEqual(special["classic_context_menu"], True)
        self.assertEqual(special["search_mode"], 1)

    def test_powershell_script_supports_all_user_default_and_specials(self):
        entries = [
            {
                "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "name": "HideFileExt",
                "type": "DWORD",
                "value": 0,
            }
        ]

        script = et.build_powershell_script(
            entries,
            {"classic_context_menu": True, "search_mode": 1},
            default_all_users=True,
        )

        self.assertIn("param([switch]$CurrentUserOnly)", script)
        self.assertIn(r"Registry::HKEY_USERS\.DEFAULT", script)
        self.assertIn("SearchboxTaskbarMode", script)
        self.assertIn(r"InprocServer32", script)
        self.assertIn("HideFileExt", script)

    def test_darkmode_script_uses_location_api_and_coordinate_overrides(self):
        script = et.build_darkmode_auto_switch_script(40.123456789, -75.987654321)

        self.assertIn("$ConfiguredLatitude = 40.12345679", script)
        self.assertIn("$ConfiguredLongitude = -75.98765432", script)
        self.assertIn("Windows.Devices.Geolocation.Geolocator", script)
        self.assertIn("AppsUseLightTheme", script)
        self.assertIn("SystemUsesLightTheme", script)

    def test_parse_computer_targets_deduplicates_repeated_inputs(self):
        targets = et.parse_computer_targets(["pc-a, pc-b", "pc-a"], "pc-c,pc-b")

        self.assertEqual(targets, ["pc-a", "pc-b", "pc-c"])

    def test_registry_plan_rolls_back_applied_steps_after_failed_verification(self):
        operations = [
            et.registry_set_operation(r"Software\ExplorerTweaks\Test", "A", 1, "DWORD"),
            et.registry_set_operation(r"Software\ExplorerTweaks\Test", "B", 2, "DWORD"),
        ]

        with patch.object(
            et,
            "capture_registry_operation_snapshot",
            side_effect=[
                et.RegistryValueSnapshot(True, 0, et.winreg.REG_DWORD),
                et.RegistryValueSnapshot(False),
            ],
        ), patch.object(et, "apply_registry_operation") as apply, patch.object(
            et,
            "verify_registry_operation",
            side_effect=[True, False],
        ), patch.object(et, "rollback_registry_operation") as rollback:
            report = et.execute_registry_plan(operations, label="test plan", dry_run=False)

        self.assertFalse(report.success)
        self.assertEqual(apply.call_count, 2)
        self.assertEqual(rollback.call_count, 2)
        self.assertEqual(report.verified, 1)
        self.assertEqual(report.rolled_back, 2)
        self.assertIn("verification", report.errors[0])

    def test_registry_plan_dry_run_reports_previous_value(self):
        operation = et.registry_set_operation(r"Software\ExplorerTweaks\Test", "A", 1, "DWORD")

        with patch.object(
            et,
            "capture_registry_operation_snapshot",
            return_value=et.RegistryValueSnapshot(True, 0, et.winreg.REG_DWORD),
        ):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                report = et.execute_registry_plan([operation], label="dry plan", dry_run=True)

        self.assertTrue(report.success)
        self.assertEqual(report.planned, 1)
        self.assertIn("previous: 0 (DWORD)", output.getvalue())
        self.assertIn("REFRESH dry plan: shell_notify", output.getvalue())
        self.assertIsNotNone(report.refresh)

    def test_registry_plan_sends_refresh_after_successful_apply(self):
        operation = et.registry_set_operation(r"Software\ExplorerTweaks\Test", "A", 1, "DWORD")
        refresh_report = et.ShellRefreshReport("test plan", False, [et.REFRESH_SHELL_NOTIFY])

        with patch.object(
            et,
            "capture_registry_operation_snapshot",
            return_value=et.RegistryValueSnapshot(False),
        ), patch.object(et, "apply_registry_operation"), patch.object(
            et,
            "verify_registry_operation",
            return_value=True,
        ), patch.object(et, "refresh_registry_changes", return_value=refresh_report) as refresh:
            report = et.execute_registry_plan([operation], label="test plan", dry_run=False)

        self.assertTrue(report.success)
        self.assertIs(report.refresh, refresh_report)
        refresh.assert_called_once_with([operation], "test plan")

    def test_theme_settings_declare_theme_refresh_strategy(self):
        settings = {setting.id: setting for setting in et.get_all_settings()}

        self.assertEqual(settings["dark_system"].refresh_strategy, et.REFRESH_THEME_BROADCAST)
        self.assertEqual(settings["dark_apps"].refresh_strategy, et.REFRESH_THEME_BROADCAST)
        self.assertEqual(settings["show_extensions"].refresh_strategy, et.REFRESH_SHELL_NOTIFY)

    def test_restart_explorer_dry_run_reports_explicit_fallback(self):
        original_dry_run = et.DRY_RUN
        et.DRY_RUN = True
        try:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertTrue(et.restart_explorer())
        finally:
            et.DRY_RUN = original_dry_run

        self.assertIn("RESTART Explorer fallback", output.getvalue())

    def test_parse_reg_file_operations_supports_common_export_values(self):
        raw = (
            "Windows Registry Editor Version 5.00\r\n\r\n"
            "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced]\r\n"
            '"HideFileExt"=dword:00000000\r\n'
            '"SampleString"="C:\\\\Temp"\r\n'
            '"SampleBinary"=hex:01,02,ff\r\n'
            "@=\"\"\r\n"
        ).encode("utf-16")

        operations = et.parse_reg_file_operations(raw, "registry/advanced.reg")

        self.assertEqual(len(operations), 4)
        self.assertEqual(operations[0].name, "HideFileExt")
        self.assertEqual(operations[0].value, 0)
        self.assertEqual(operations[1].value, r"C:\Temp")
        self.assertEqual(operations[2].value, b"\x01\x02\xff")
        self.assertEqual(operations[3].name, "")

    def _valid_registry_key(self):
        return r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"

    def _valid_reg_file(self):
        return (
            "Windows Registry Editor Version 5.00\r\n\r\n"
            "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced]\r\n"
            '"HideFileExt"=dword:00000000\r\n'
        ).encode("utf-16")

    def _manifest(self, registry_exports=None, wallpaper=None, taskbar_pins=None):
        return {
            "app": et.APP_NAME,
            "version": "2.4.0",
            "created_utc": "2026-06-27T00:00:00+00:00",
            "registry_exports": registry_exports or [],
            "missing_registry_paths": [],
            "wallpaper": wallpaper,
            "taskbar_pins": taskbar_pins,
        }

    def _write_bundle(self, bundle_path: Path, entries):
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name, payload in entries:
                if isinstance(payload, (dict, list)):
                    payload = json.dumps(payload)
                zf.writestr(name, payload)

    def test_restore_rejects_parent_directory_member_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            outside = Path(tmp) / "evil.reg"
            self._write_bundle(
                bundle,
                [
                    ("manifest.json", self._manifest()),
                    ("../evil.reg", "payload"),
                ],
            )

            with patch.object(et.subprocess, "run") as run:
                with self.assertRaises(et.BackupBundleValidationError):
                    et.restore_backup_bundle(str(bundle))

            run.assert_not_called()
            self.assertFalse(outside.exists())

    def test_validate_backup_rejects_absolute_member_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            self._write_bundle(
                bundle,
                [
                    ("manifest.json", self._manifest()),
                    ("/absolute.reg", "payload"),
                ],
            )

            with self.assertRaises(et.BackupBundleValidationError):
                et.validate_backup_bundle(str(bundle))

    def test_validate_backup_rejects_duplicate_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    zf.writestr("manifest.json", json.dumps(self._manifest()))
                    zf.writestr("manifest.json", json.dumps(self._manifest()))

            with self.assertRaises(et.BackupBundleValidationError):
                et.validate_backup_bundle(str(bundle))

    def test_validate_backup_rejects_non_whitelisted_manifest_registry_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            self._write_bundle(
                bundle,
                [
                    (
                        "manifest.json",
                        self._manifest(
                            registry_exports=[
                                {"key": r"HKCU\Software\Evil", "file": "registry/evil.reg"}
                            ]
                        ),
                    ),
                    ("registry/evil.reg", self._valid_reg_file()),
                ],
            )

            with self.assertRaises(et.BackupBundleValidationError):
                et.validate_backup_bundle(str(bundle))

    def test_validate_backup_rejects_non_whitelisted_reg_file_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            self._write_bundle(
                bundle,
                [
                    (
                        "manifest.json",
                        self._manifest(
                            registry_exports=[
                                {"key": self._valid_registry_key(), "file": "registry/advanced.reg"}
                            ]
                        ),
                    ),
                    (
                        "registry/advanced.reg",
                        "Windows Registry Editor Version 5.00\r\n\r\n[HKEY_LOCAL_MACHINE\\Software\\Evil]\r\n",
                    ),
                ],
            )

            with self.assertRaises(et.BackupBundleValidationError):
                et.validate_backup_bundle(str(bundle))

    def test_validate_backup_rejects_unexpected_payload_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            self._write_bundle(
                bundle,
                [
                    ("manifest.json", self._manifest()),
                    ("unexpected.txt", "payload"),
                ],
            )

            with self.assertRaises(et.BackupBundleValidationError):
                et.validate_backup_bundle(str(bundle))

    def test_restore_accepts_valid_v24_bundle_with_registry_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "good.zip"
            self._write_bundle(
                bundle,
                [
                    (
                        "manifest.json",
                        self._manifest(
                            registry_exports=[
                                {"key": self._valid_registry_key(), "file": "registry/advanced.reg"}
                            ]
                        ),
                    ),
                    ("registry/advanced.reg", self._valid_reg_file()),
                ],
            )

            report = et.RegistryPlanReport("restore", False, [])
            with patch.object(et, "execute_registry_plan", return_value=report) as execute:
                results = et.restore_backup_bundle(str(bundle))

            self.assertEqual(results, {"registry_imported": 1, "files_restored": 0, "errors": 0})
            execute.assert_called_once()
            operations = execute.call_args.args[0]
            self.assertEqual(len(operations), 1)
            self.assertEqual(operations[0].path, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
            self.assertEqual(operations[0].name, "HideFileExt")
            self.assertEqual(operations[0].value, 0)

    def test_restore_dry_run_still_rejects_invalid_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad.zip"
            self._write_bundle(
                bundle,
                [
                    ("manifest.json", self._manifest()),
                    ("unexpected.txt", "payload"),
                ],
            )

            original_dry_run = et.DRY_RUN
            et.DRY_RUN = True
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(et.BackupBundleValidationError):
                        et.restore_backup_bundle(str(bundle))
            finally:
                et.DRY_RUN = original_dry_run


if __name__ == "__main__":
    unittest.main()
