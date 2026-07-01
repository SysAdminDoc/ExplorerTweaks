# Changelog

All notable changes to ExplorerTweaks will be documented in this file.

## [v2.15.0] - 2026-06-30

### Fixed
- Replaced 7 bare `except:` clauses with specific exception types to avoid catching `SystemExit` and `KeyboardInterrupt`.
- Fixed registry key handle leak in `get_registry_value` when `QueryValueEx` raises a non-`FileNotFoundError`.
- Fixed `is_photo_viewer_registered` key handle leak by moving `CloseKey` into a `finally` block.
- Fixed GUI crash when importing a malformed JSON profile file.
- Fixed `IndexError` crash when Windows returns a search mode value outside the expected 0-2 range.
- Fixed search clear leaving the GUI stuck on an empty search results page instead of restoring the previous category.
- Fixed live preview not reflecting actual system state for 6 settings (silent installs, Bing search, Cortana, search history, End Task menu, Aero Peek) that were hardcoded to defaults.
- Fixed `windows_cmd_quote` using incorrect `\"` escaping instead of Windows-correct `""` for registry shell commands.
- Fixed `.reg` export crash when a registry value is not directly `int`-compatible by adding explicit `int()` cast.
- Fixed JSON export and CLI export performing duplicate registry reads for each setting.
- Fixed diff view silently excluding Classic Context Menu and Search Mode from comparison results.
- Fixed `save_preset_to_file` omitting settings that haven't been explicitly written to registry; now includes all settings using their default values.
- Fixed `cli_apply` exiting with code 0 even when zero settings were applied; now exits 1 with a warning.
- Fixed `restore_backup_bundle` silently skipping wallpaper restore when target directory no longer exists; now logs a warning and increments the error count.
- Fixed `rollback_registry_operation` crash when snapshot is `None` for `delete_tree` operations.
- Fixed `execute_registry_plan` fragile error-path variable scoping by initializing the result before the try block.
- Added error handling to GUI Export, Export .reg, and Export .ps1 actions for file write failures.
- Fixed `create_icon.py` `import math` inside inner loop and `create_simple_icon` missing `append_images` so all ICO sizes are included.
- Added 9 regression tests covering error handling, rollback safety, preset save completeness, and cmd quoting.

## [v2.14.0] - 2026-06-30

### Added
- Added release packaging that produces a versioned ZIP, SHA256 manifest, and `INSTALL.txt` alongside the portable EXE.
- Added conditional Authenticode signing in `build.bat` when a local code-signing certificate is available.
- Documented install, uninstall, checksum verification, and unsigned-artifact behavior in the README.

## [v2.13.0] - 2026-06-30

### Added
- Added an English GUI message catalog for app chrome, Tools controls, common dialogs, and accessibility labels.
- Added accessibility metadata and high-contrast focus outlines for navigation buttons, shared cards, switches, radio controls, search, and the operation log.
- Added compact 1080px-wide layout support with wrapped Tools action grids and tests for localization/accessibility layout contracts.

## [v2.12.0] - 2026-06-30

### Changed
- Upgraded and pinned CustomTkinter, PyInstaller, and Pillow for repeatable GUI and portable EXE builds.
- Routed the build script through pinned requirements, `python -m pip check`, and the active Python interpreter's PyInstaller module.
- Removed the icon generator's hidden floating dependency install path and documented the dependency upgrade workflow.

## [v2.11.0] - 2026-06-30

### Added
- Added context-menu inventory for common HKCU/HKLM File, Directory, Background, and Drive shell roots.
- Added reversible context-menu enable/disable commands using `LegacyDisable` under managed inventory roots.
- Added HKCU-only context-menu action-pack export/import with target/name/command validation.
- Added a GUI Menu Inventory export action and unit coverage for action-pack safety boundaries.

## [v2.10.0] - 2026-06-30

### Added
- Added Explorer folder-view defaults preview for common folder templates.
- Added folder-view-only backup and restore bundles for the current user's Shell Bags registry state.
- Added Details, List, and Large Icons folder-view presets with CLI and GUI apply paths.
- Added tests for folder-view registry operation planning, preview summaries, and backup validation.

## [v2.9.0] - 2026-06-30

### Added
- Added policy/CSP metadata for mapped Explorer, Search, and CloudContent settings.
- Added managed-policy PowerShell export mode that writes mapped HKLM policy keys and reports omitted preference-only settings.
- Added `--export-intune-remediation PROFILE DIR` to generate Intune detection and remediation PowerShell script pairs.
- Added unit coverage for policy entry conversion, managed-policy script output, and Intune remediation export.

## [v2.8.0] - 2026-06-30

### Added
- Added Windows 11 25H2 detection for OS build `26200` and later.
- Added catalog tests that pin 24H2/25H2 detection and min/max build gating behavior.

### Fixed
- Unsupported settings filtered by OS min/max gates now show a category notice instead of disappearing silently.

## [v2.7.0] - 2026-06-28

### Added
- Added a persistent GUI operation log/status panel in the preview column.
- Added structured operation events for registry plans, refresh attempts, backup/restore, remote apply, recent-item cleanup, Send To removal, policy-lock warnings, and Explorer restart fallback.
- Added `--dry-run-report FILE` to write JSON operation reports from CLI workflows.

### Fixed
- Registry plan failures now serialize hive, path, action, error, and recovery hint details for diagnostics.

## [v2.6.0] - 2026-06-28

### Added
- Added refresh strategy metadata for registry-backed settings.
- Sent targeted shell notifications and theme broadcasts after successful local registry plans.
- Added a manual Refresh Shell GUI action and kept forced Explorer restart as an explicit fallback with status output.

### Fixed
- Replaced default "restart Explorer" completion guidance with targeted-refresh status in GUI and CLI apply flows.

## [v2.5.0] - 2026-06-28

### Added
- Added a shared registry plan/apply/verify/rollback engine for local settings writes.
- Routed GUI imports, preset apply, CLI apply, multi-user apply, Photo Viewer registration, classic context menu, shell-menu integration, and backup restore registry values through verified registry plans.
- Added dry-run registry plans with previous-value snapshots and per-operation recovery hints.

### Fixed
- Replaced backup restore `reg import` calls with parsed registry operations so restores can verify writes and roll back captured prior values on partial failure.
- Added PyInstaller multiprocessing freeze guards and a runtime hook so the portable EXE starts without recursive worker relaunch risk.

## [v2.4.1] - 2026-06-28

### Fixed
- Hardened backup restore ZIP validation before extraction or registry import.
- Rejected unsafe restore archives with parent-directory paths, absolute paths, duplicate manifests, non-whitelisted registry keys, and unexpected payload files.
- Added restore-bundle validation coverage for malicious archives and valid v2.4.0-compatible bundles.

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
