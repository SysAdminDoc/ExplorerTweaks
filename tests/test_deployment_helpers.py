import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch

import explorer_tweaks as et


REPO_ROOT = Path(__file__).resolve().parents[1]


class BuildRepeatabilityTests(unittest.TestCase):
    def test_requirements_pin_gui_and_build_dependencies(self):
        requirements = [
            line.strip()
            for line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        pins = {}

        for requirement in requirements:
            self.assertIn("==", requirement, f"{requirement} must use an exact version pin")
            name, version = requirement.split("==", 1)
            self.assertRegex(version, r"^\d+\.\d+\.\d+$")
            pins[name.lower()] = version

        self.assertEqual(pins["customtkinter"], "6.0.0")
        self.assertEqual(pins["pyinstaller"], "6.21.0")
        self.assertEqual(pins["pillow"], "12.2.0")

    def test_build_script_uses_pinned_environment(self):
        build_script = (REPO_ROOT / "build.bat").read_text(encoding="utf-8").lower()

        self.assertIn("set app_version=2.14.0", build_script)
        self.assertIn("set build_venv=.build-venv", build_script)
        self.assertIn("set generated_icon=0", build_script)
        self.assertIn("python -m venv", build_script)
        self.assertIn("-m pip install --requirement requirements.txt", build_script)
        self.assertIn("-m pip check", build_script)
        self.assertIn("-m pyinstaller --noconfirm explorertweaks.spec", build_script)
        self.assertIn('if "%generated_icon%"=="1" if exist "icon.ico" del /q "icon.ico"', build_script)
        self.assertNotIn("pip install pillow", build_script)

    def test_build_script_creates_release_trust_artifacts(self):
        build_script = (REPO_ROOT / "build.bat").read_text(encoding="utf-8").lower()

        self.assertIn("set release_basename=explorertweaks-v%app_version%-win64", build_script)
        self.assertIn("set checksum_file=explorertweaks-v%app_version%-sha256sums.txt", build_script)
        self.assertIn("set zip_file=%release_basename%.zip", build_script)
        self.assertIn("set-authenticodesignature", build_script)
        self.assertIn("no code-signing cert found; skipping signing", build_script)
        self.assertIn("install.txt", build_script)
        self.assertIn("$notes = @(('explorertweaks v' + $env:app_version)", build_script)
        self.assertIn("('run get-filehash -algorithm sha256 explorertweaks.exe and compare it with ' + $env:checksum_file + '.')", build_script)
        self.assertIn("function get-sha256hex", build_script)
        self.assertIn("system.security.cryptography.sha256", build_script)
        self.assertIn("compress-archive", build_script)
        self.assertNotIn("tools > remove", build_script)

    def test_pyinstaller_spec_keeps_runtime_hook_and_version_metadata(self):
        spec = (REPO_ROOT / "ExplorerTweaks.spec").read_text(encoding="utf-8")

        self.assertIn('runtime_hooks=["assets/runtime_hook_mp.py"]', spec)
        self.assertIn('version="version_info.txt"', spec)
        self.assertIn('collect_all("customtkinter")', spec)

    def test_icon_generator_does_not_install_dependencies(self):
        icon_generator = (REPO_ROOT / "create_icon.py").read_text(encoding="utf-8")

        self.assertNotIn("subprocess.check_call", icon_generator)
        self.assertNotIn("['pip', 'install'", icon_generator)
        self.assertNotIn('["pip", "install"', icon_generator)
        self.assertIn("python -m pip install --requirement requirements.txt", icon_generator)


class AccessibilityLocalizationTests(unittest.TestCase):
    def test_gui_message_catalog_contains_required_english_strings(self):
        catalog = et.GUI_MESSAGES[et.DEFAULT_LOCALE]
        missing = [key for key in et.REQUIRED_GUI_MESSAGE_KEYS if key not in catalog or not catalog[key]]

        self.assertFalse(missing)
        self.assertEqual(et.msg("tools.title"), "Tools")
        self.assertEqual(et.msg("tools.folder_summary", configured=2, total=7), "2/7 folder templates configured.")
        self.assertEqual(et.msg("access.switch", name="Show File Extensions"), "Show File Extensions toggle")

    def test_compact_layout_and_focus_tokens_are_pinned(self):
        self.assertLessEqual(et.APP_MIN_WIDTH, 1080)
        self.assertLessEqual(et.APP_MIN_HEIGHT, 680)
        self.assertLessEqual(et.PREVIEW_WIDTH, 420)
        self.assertIn("focus", et.UI)
        self.assertRegex(et.UI["focus"], r"^#[0-9a-fA-F]{6}$")
        self.assertLessEqual(et.SETTING_WRAP_LENGTH, 320)


class DeploymentHelperTests(unittest.TestCase):
    def setUp(self):
        et.clear_operation_log()

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

    def test_profile_registry_entries_can_target_managed_policy_mappings(self):
        entries, special = et.profile_registry_entries(
            {
                "show_extensions": True,
                "bing_search": False,
                "classic_context_menu": True,
                "show_hidden": True,
            },
            et.get_all_settings(),
            managed_policy=True,
        )

        by_name = {entry["name"]: entry for entry in entries}
        self.assertEqual(by_name["HideFileExt"]["path"], r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
        self.assertEqual(by_name["HideFileExt"]["value"], 0)
        self.assertEqual(by_name["DisableSearchBoxSuggestions"]["path"], r"Software\Policies\Microsoft\Windows\Explorer")
        self.assertEqual(by_name["DisableSearchBoxSuggestions"]["value"], 1)
        self.assertEqual(by_name["DisableSearchBoxSuggestions"]["source"], "managed_policy")
        self.assertIn("Classic Context Menu", special["_policy_omitted"])
        self.assertIn("Show Hidden Files", special["_policy_omitted"])

    def test_managed_policy_powershell_script_targets_hklm_and_marks_source(self):
        entries, special = et.profile_registry_entries(
            {"cortana": False},
            et.get_all_settings(),
            managed_policy=True,
        )

        script = et.build_powershell_script(entries, special, managed_policy=True)

        self.assertIn("Mode: managed policy", script)
        self.assertIn("Registry::HKEY_LOCAL_MACHINE", script)
        self.assertIn("Source = 'managed_policy'", script)
        self.assertIn("AllowCortana", script)
        self.assertNotIn("Registry::HKEY_USERS", script)

    def test_intune_remediation_export_writes_detection_and_remediation_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.json"
            out_dir = Path(tmp) / "intune"
            profile.write_text(
                json.dumps({"settings": {"bing_search": False, "show_hidden": True}}),
                encoding="utf-8",
            )

            result = et.export_intune_remediation(str(profile), str(out_dir))

            detect = Path(result["detect"]).read_text(encoding="utf-8-sig")
            remediate = Path(result["remediate"]).read_text(encoding="utf-8-sig")
            self.assertNotIn(b"\r\r\n", Path(result["detect"]).read_bytes())
            self.assertNotIn(b"\r\r\n", Path(result["remediate"]).read_bytes())
            self.assertEqual(result["settings"], 1)
            self.assertIn("exit 0", detect)
            self.assertIn("exit 1", detect)
            self.assertIn("DisableSearchBoxSuggestions", detect)
            self.assertIn("Mode: managed policy", remediate)
            self.assertIn("DisableSearchBoxSuggestions", remediate)
            self.assertIn("Show Hidden Files", result["omitted"])

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

    def test_operation_report_payload_includes_registry_error_recovery_hint(self):
        operation = et.registry_set_operation(r"Software\ExplorerTweaks\Test", "A", 1, "DWORD")

        with patch.object(
            et,
            "capture_registry_operation_snapshot",
            return_value=et.RegistryValueSnapshot(False),
        ), patch.object(et, "apply_registry_operation"), patch.object(
            et,
            "verify_registry_operation",
            return_value=False,
        ), patch.object(et, "rollback_registry_operation"):
            report = et.execute_registry_plan([operation], label="failing plan", dry_run=False)

        payload = et.operation_report_payload()

        self.assertFalse(report.success)
        self.assertEqual(payload["registry_plans"][0]["label"], "failing plan")
        self.assertIn("Recovery hint", payload["registry_plans"][0]["errors"][0])
        self.assertEqual(payload["registry_plans"][0]["operations"][0]["hive"], "HKCU")
        self.assertEqual(payload["registry_plans"][0]["operations"][0]["action"], "set_value")

    def test_write_operation_report_writes_json_file(self):
        operation = et.registry_set_operation(r"Software\ExplorerTweaks\Test", "A", 1, "DWORD")
        with patch.object(
            et,
            "capture_registry_operation_snapshot",
            return_value=et.RegistryValueSnapshot(True, 0, et.winreg.REG_DWORD),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                et.execute_registry_plan([operation], label="dry plan", dry_run=True)

        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "report.json"
            et.write_operation_report(str(report_path))
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["app"], et.APP_NAME)
        self.assertEqual(payload["version"], et.APP_VERSION)
        self.assertEqual(payload["registry_plans"][0]["label"], "dry plan")

    def test_cli_dry_run_report_writes_structured_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "cli-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(et.__file__).resolve()),
                    "--preset",
                    "Minimal",
                    "--dry-run",
                    "--dry-run-report",
                    str(report_path),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["app"], et.APP_NAME)
        self.assertTrue(payload["dry_run"])
        self.assertTrue(payload["registry_plans"])
        self.assertTrue(any(event["action"] == "cli" for event in payload["events"]))

    def test_theme_settings_declare_theme_refresh_strategy(self):
        settings = {setting.id: setting for setting in et.get_all_settings()}

        self.assertEqual(settings["dark_system"].refresh_strategy, et.REFRESH_THEME_BROADCAST)
        self.assertEqual(settings["dark_apps"].refresh_strategy, et.REFRESH_THEME_BROADCAST)
        self.assertEqual(settings["show_extensions"].refresh_strategy, et.REFRESH_SHELL_NOTIFY)

    def test_windows_version_detects_24h2_and_25h2_builds(self):
        with patch.object(et.platform, "version", return_value="10.0.26100"):
            self.assertEqual(et.get_windows_version(), et.OSVersion.WINDOWS_11_24H2)
        with patch.object(et.platform, "version", return_value="10.0.26200"):
            self.assertEqual(et.get_windows_version(), et.OSVersion.WINDOWS_11_25H2)
        with patch.object(et.platform, "version", return_value="10.0.30000"):
            self.assertEqual(et.get_windows_version(), et.OSVersion.WINDOWS_11_25H2)

    def test_setting_support_gates_pin_25h2_min_max_behavior(self):
        min_25h2 = et.RegistrySetting(
            id="future",
            name="Future",
            description="Future setting",
            category="Test",
            subcategory="Test",
            reg_path=r"Software\ExplorerTweaks\Test",
            reg_name="Future",
            reg_type="DWORD",
            enable_value=1,
            disable_value=0,
            default_value=0,
            min_os=et.OSVersion.WINDOWS_11_25H2,
        )
        max_24h2 = et.RegistrySetting(
            id="legacy",
            name="Legacy",
            description="Legacy setting",
            category="Test",
            subcategory="Test",
            reg_path=r"Software\ExplorerTweaks\Test",
            reg_name="Legacy",
            reg_type="DWORD",
            enable_value=1,
            disable_value=0,
            default_value=0,
            max_os=et.OSVersion.WINDOWS_11_24H2,
        )

        self.assertFalse(et.is_setting_supported(min_25h2, et.OSVersion.WINDOWS_11_24H2))
        self.assertTrue(et.is_setting_supported(min_25h2, et.OSVersion.WINDOWS_11_25H2))
        self.assertTrue(et.is_setting_supported(max_24h2, et.OSVersion.WINDOWS_11_24H2))
        self.assertFalse(et.is_setting_supported(max_24h2, et.OSVersion.WINDOWS_11_25H2))

    def test_folder_view_details_operations_reset_bags_and_set_templates(self):
        operations = et.build_folder_view_operations("details", reset_existing=True)
        delete_paths = [operation.path for operation in operations if operation.action == "delete_tree"]
        set_operations = [operation for operation in operations if operation.action == "set_value"]

        self.assertIn(et.FOLDER_VIEW_BAGMRU_PATH, delete_paths)
        self.assertIn(et.FOLDER_VIEW_BAGS_PATH, delete_paths)
        self.assertEqual(len(set_operations), len(et.folder_view_template_paths()) * 5)
        mode_values = {
            (operation.path, operation.name): operation.value
            for operation in set_operations
            if operation.name in ("Mode", "LogicalViewMode", "IconSize", "GroupView")
        }
        for _, path in et.folder_view_template_paths():
            self.assertEqual(mode_values[(path, "Mode")], 4)
            self.assertEqual(mode_values[(path, "LogicalViewMode")], 1)
            self.assertEqual(mode_values[(path, "IconSize")], 16)
            self.assertEqual(mode_values[(path, "GroupView")], 0)

    def test_folder_view_preview_reports_configured_templates(self):
        def fake_get(path, name, hive=et.winreg.HKEY_CURRENT_USER):
            if name == "Mode" and path == et.FOLDER_VIEW_ALLFOLDERS_PATH:
                return 4
            return None

        with patch.object(et, "get_registry_value", side_effect=fake_get):
            preview = et.folder_view_defaults_preview()

        self.assertTrue(preview[0]["configured"])
        self.assertEqual(preview[0]["values"]["Mode"], 4)
        self.assertFalse(preview[1]["configured"])

    def test_folder_view_backup_rejects_non_folder_registry_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "bad_folder_view.zip"
            manifest = {
                "app": et.APP_NAME,
                "type": et.FOLDER_VIEW_BACKUP_TYPE,
                "version": et.APP_VERSION,
                "created_utc": "2026-06-30T00:00:00+00:00",
                "registry_exports": [{"key": r"HKCU\Software\Evil", "file": "registry/evil.reg"}],
                "missing_registry_paths": [],
            }
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(et.BACKUP_MANIFEST_FILE, json.dumps(manifest))
                zf.writestr("registry/evil.reg", self._valid_reg_file())

            with zipfile.ZipFile(bundle, "r") as zf:
                with self.assertRaises(et.BackupBundleValidationError):
                    et.validate_folder_view_backup_zip(zf)

    def test_context_menu_action_pack_operations_are_hkcu_bounded(self):
        operations = et.context_menu_action_operations(
            {
                "target": "folder_background",
                "name": "OpenTools",
                "label": "Open Tools",
                "command": r"explorer.exe %V",
                "icon": "shell32.dll,1",
                "shift_only": True,
            }
        )

        paths = [operation.path for operation in operations]
        self.assertIn(r"Software\Classes\Directory\Background\shell\OpenTools", paths)
        self.assertIn(r"Software\Classes\Directory\Background\shell\OpenTools\command", paths)
        self.assertTrue(all(operation.hive == et.winreg.HKEY_CURRENT_USER for operation in operations))
        self.assertTrue(any(operation.name == "Extended" for operation in operations))

    def test_context_menu_action_rejects_unsafe_target_and_name(self):
        with self.assertRaises(ValueError):
            et.validate_context_menu_action(
                {
                    "target": "hklm",
                    "name": "Bad",
                    "label": "Bad",
                    "command": "cmd.exe",
                }
            )
        with self.assertRaises(ValueError):
            et.validate_context_menu_action(
                {
                    "target": "files",
                    "name": r"..\Bad",
                    "label": "Bad",
                    "command": "cmd.exe",
                }
            )

    def test_context_menu_entry_id_must_stay_under_inventory_roots(self):
        self.assertTrue(
            et.is_context_menu_inventory_path(
                "HKCU",
                r"Software\Classes\Directory\shell\ExplorerTweaks",
            )
        )
        self.assertFalse(
            et.is_context_menu_inventory_path(
                "HKCU",
                r"Software\Microsoft\Windows\CurrentVersion\Run\Bad",
            )
        )

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
