# Changelog

All notable changes to ExplorerTweaks will be documented in this file.

## [v2.4.0] - 2026-06-27

### Added
- PowerShell deployment export for current-user and all-loaded-user registry hives.
- Profile-to-PowerShell export and PSRemoting dry-run/apply support.
- Multi-user local profile/preset apply across `HKU\.DEFAULT` and loaded user SIDs.
- Backup/restore bundles containing ExplorerTweaks registry exports, wallpaper, and taskbar pins.
- Right-click shell integration that launches ExplorerTweaks focused on the relevant category.
- Sunrise/sunset dark-mode auto-switch scheduled task using Windows Location API or explicit coordinates.
- Unit coverage for deployment script generation, remote target parsing, and dark-mode script generation.

### Fixed
- Corrected inverted registry setting conversion so profile/preset apply writes values such as `HideFileExt=0` for "Show File Extensions".
- Made JSON profile loading tolerate UTF-8 BOMs from PowerShell-generated files.
- Fixed `.reg` export encoding to emit a valid UTF-16 registry file.

## [v2.3.0] - 2026-06-19

### Added
- CLI mode: `--apply`, `--preset`, `--export`, `--dry-run`, `--wipe-recent`, `--list-presets`
- Dry-run mode: preview all registry operations without writing
- Policy-aware detection: warns when a setting is locked by Group Policy (orange GP badge)
- Search across all settings with fuzzy matching in the sidebar
- Built-in presets: Minimal, Privacy, Power User (one-click apply from Tools page)
- Save/load user presets as JSON files
- Per-setting "why it matters" info text (click the ? icon to expand)
- Send To folder manager: list and remove shell:sendto entries
- Recent items wipe: one-shot clear for Jump Lists, AutomaticDestinations, CustomDestinations
- Classic Photo Viewer restore: register/unregister Windows Photo Viewer for common image types
- Export as .reg file for easy undo/deployment on other machines
- Diff view: compare current system state against any profile or built-in preset
- Tools page in sidebar grouping all utility features

## [v2.2.0]

- Pixel-accurate Windows 11 File Explorer and Taskbar simulation
- 40+ registry-backed settings with live preview
- Export/Import JSON configurations
- OS-aware filtering (Win10/Win11 version-gated settings)

## [v1.2.0]

- Initial public release
- Add screenshot to README
- Add files via upload
