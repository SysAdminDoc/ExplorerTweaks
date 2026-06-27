import unittest

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


if __name__ == "__main__":
    unittest.main()
