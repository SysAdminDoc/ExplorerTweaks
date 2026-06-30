# ExplorerTweaks v2.11.0

![Version](https://img.shields.io/badge/Version-2.11.0-1DB954?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)

ExplorerTweaks is a Windows File Explorer and shell configuration utility with a dark CustomTkinter GUI, live preview, profile import/export, and deployment tooling for local users, IT scripts, and PSRemoting.

![Screenshot](screenshot.png)

## Features

- Live Explorer and taskbar preview for file extensions, hidden files, status bar, taskbar buttons, theme mode, and Windows 11 navigation items.
- More than 50 File Explorer, taskbar, search, privacy, performance, and Windows 11 shell toggles.
- Built-in presets for Minimal, Privacy, and Power User setups.
- JSON profile export/import plus diff view against saved profiles or built-in presets.
- CLI apply/export, dry-run mode, preset listing, recent-items wipe, and policy-lock warnings.
- Shared registry plan/apply/verify/rollback engine for local GUI, CLI, preset, multi-user, and restore operations.
- Targeted shell/theme refresh after supported changes, with forced Explorer restart kept as an explicit fallback.
- Persistent GUI operation log/status panel plus structured JSON operation reports from CLI dry-runs.
- Windows 11 25H2-aware OS detection and min/max build gates for setting catalog compatibility.
- Managed policy metadata for mapped settings plus Intune remediation detection/remediation script export.
- Explorer folder-view defaults preview, backup, restore, and Details/List/Large Icons preset apply.
- Context-menu inventory, reversible `LegacyDisable` toggles, and HKCU action-pack export/import.
- PowerShell deployment script export for current-user or all-loaded-user registry hives.
- PSRemoting profile push for fleets that already have WinRM access configured.
- Multi-user local apply across `HKU\.DEFAULT` and loaded user SIDs.
- Backup/restore bundles for ExplorerTweaks registry subtrees, wallpaper, and taskbar pins, with archive validation before restore.
- Right-click shell entries that launch ExplorerTweaks focused on the relevant settings category.
- Sunrise/sunset dark-mode auto-switch using Windows Location API or explicit latitude/longitude overrides.
- Send To folder manager, classic context menu toggle, classic Photo Viewer registration, and `.reg` export.

## Quick Start

```powershell
git clone https://github.com/SysAdminDoc/ExplorerTweaks.git
cd ExplorerTweaks
pip install -r requirements.txt
python explorer_tweaks.py
```

Build the portable executable:

```powershell
build.bat
```

The executable is written to `dist\ExplorerTweaks.exe`.

## CLI Usage

```powershell
python explorer_tweaks.py --list-presets
python explorer_tweaks.py --preset "Power User" --dry-run
python explorer_tweaks.py --preset "Power User" --dry-run --dry-run-report report.json
python explorer_tweaks.py --apply profile.json
python explorer_tweaks.py --apply profile.json --all-users
python explorer_tweaks.py --export settings.json
python explorer_tweaks.py --export settings.reg --format reg
python explorer_tweaks.py --export settings.ps1 --format ps1 --all-users
python explorer_tweaks.py --export settings-policy.ps1 --format ps1 --managed-policy
python explorer_tweaks.py --export-profile-ps1 profile.json deploy.ps1 --all-users
python explorer_tweaks.py --export-profile-ps1 profile.json deploy-policy.ps1 --managed-policy
python explorer_tweaks.py --export-intune-remediation profile.json .\intune-remediation
python explorer_tweaks.py --remote-apply profile.json --computer PC-01 --computer PC-02 --dry-run
python explorer_tweaks.py --backup ExplorerTweaks_backup.zip
python explorer_tweaks.py --restore ExplorerTweaks_backup.zip
python explorer_tweaks.py --folder-view-preview
python explorer_tweaks.py --folder-view-backup folder_views.zip
python explorer_tweaks.py --folder-view-apply details --folder-view-backup-before folder_views.zip
python explorer_tweaks.py --folder-view-restore folder_views.zip
python explorer_tweaks.py --context-menu-list
python explorer_tweaks.py --context-menu-inventory context_menu_inventory.json
python explorer_tweaks.py --context-menu-disable "HKCU|Software\Classes\Directory\shell\Example"
python explorer_tweaks.py --context-menu-export-pack context_menu_pack.json
python explorer_tweaks.py --context-menu-import-pack context_menu_pack.json --dry-run
python explorer_tweaks.py --install-context-menu
python explorer_tweaks.py --uninstall-context-menu
python explorer_tweaks.py --install-darkmode-auto-switch
python explorer_tweaks.py --install-darkmode-auto-switch --darkmode-lat 40.7128 --darkmode-lon -74.0060
python explorer_tweaks.py --uninstall-darkmode-auto-switch
python explorer_tweaks.py --wipe-recent
```

## Setting Categories

- Appearance: file extensions, hidden files, protected OS files, checkboxes, compact view, thumbnails, type overlays, status bar, title/address path display.
- Navigation: launch target, nav pane expansion, all folders, separate process, restore windows at logon, sharing wizard.
- Privacy: recent files, frequent folders, document/app tracking, OneDrive sync provider notifications, suggested app installs.
- Search: Bing web results, Cortana consent, search history, taskbar search mode.
- Taskbar: Task View, Widgets, centered icons, End Task menu.
- Performance: taskbar animations, Aero Peek, thumbnail cache, network `thumbs.db`, Snap Assist, Snap Layouts.
- Theme: app and system dark mode.
- Windows 11: Gallery and classic context menu.
- Tools: presets, Send To cleanup, recent-items wipe, Photo Viewer, profile diff, deployment, backup/restore, shell integration, auto dark mode.

## Deployment Notes

`--format ps1` exports the current machine state as a PowerShell script. By default it applies to the current user; pass `--all-users` to make the script target `HKU\.DEFAULT` and all loaded user SIDs unless the script is run with `-CurrentUserOnly`.

Pass `--managed-policy` with PowerShell exports to write mapped HKLM policy keys instead of preference keys. Settings without a declared policy/CSP equivalent are omitted and reported. `--export-intune-remediation PROFILE DIR` writes `ExplorerTweaks_detect.ps1` and `ExplorerTweaks_remediate.ps1` for Intune remediation packages.

`--remote-apply` uses PowerShell Remoting and assumes WinRM access is already configured for the target computers. It does not manage credentials or enable remoting.

The dark-mode auto-switch installs a per-user scheduled task named `\ExplorerTweaks\DarkModeAutoSwitch`. If Windows Location access is disabled, reinstall with `--darkmode-lat` and `--darkmode-lon`.

Folder-view defaults manage the current user's Explorer Shell Bags defaults. `--folder-view-apply` resets existing folder view bags, writes the selected preset for common folder templates, and should be paired with `--folder-view-backup-before` or the GUI's automatic backup.

Context-menu inventory scans common HKCU/HKLM File, Directory, Background, and Drive shell roots. Disable/enable operations only set or remove `LegacyDisable` on entries under those inventory roots. Action packs import only into approved HKCU shell roots.

## Registry Locations

ExplorerTweaks writes user-level registry settings under:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\CabinetState
HKCU\Software\Microsoft\Windows\CurrentVersion\Search
HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
HKCU\Software\Microsoft\Windows\DWM
HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}
HKCU\Software\Classes\Directory\shell
HKCU\Software\Classes\Directory\Background\shell
HKCU\Software\Classes\Drive\shell
HKCU\Software\Classes\DesktopBackground\Shell
```

Most settings do not require administrator rights. Multi-user mode can only touch user hives that are already loaded.

## Development

```powershell
python -m unittest discover -s tests -v
python -m py_compile explorer_tweaks.py
python explorer_tweaks.py --help
```

## License

MIT. See [LICENSE](LICENSE).

## Disclaimer

This tool modifies Windows Registry settings. Export settings or create a backup bundle before large changes, and restart Explorer where Windows requires it.
