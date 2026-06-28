# ROADMAP

Backlog for ExplorerTweaks. Goal: stay focused on File Explorer and closely related shell surfaces such as taskbar, context menus, and search.

## Research-Driven Additions

### P0

- [ ] P0 - Harden backup restore archive validation
  Why: Restore currently extracts ZIP members before validating paths, manifest schema, registry files, or backup provenance.
  Evidence: `explorer_tweaks.py::restore_backup_bundle`; Python zipfile docs; OWASP Zip Slip.
  Touches: `explorer_tweaks.py`, `tests/test_deployment_helpers.py`
  Acceptance: Malicious `..`, absolute-path, duplicate-manifest, non-whitelisted registry, and unexpected payload entries are rejected before extraction/import; valid v2.4.0 bundles still restore.
  Complexity: M

### P1

- [ ] P1 - Add a shared plan/apply/verify/rollback engine
  Why: GUI import, preset apply, CLI apply, multi-user apply, and restore all mutate registry state through direct writes with no common pre-change backup, per-setting verification, or rollback manifest.
  Evidence: `explorer_tweaks.py::set_registry_value`, `apply_profile_values`, `_import`, `_apply_preset`; WinSetView backup-first apply pattern.
  Touches: `explorer_tweaks.py`, `tests/test_deployment_helpers.py`
  Acceptance: Every local registry mutation can produce a dry-run plan, capture previous values, verify written values, report partial failures, and restore the captured previous state.
  Complexity: L

- [ ] P1 - Replace force-kill refresh with targeted shell notifications
  Why: `restart_explorer()` kills Explorer even for changes that can be refreshed with shell notifications or registry broadcasts.
  Evidence: `explorer_tweaks.py::restart_explorer`; Microsoft `SHChangeNotify` documentation.
  Touches: `explorer_tweaks.py`
  Acceptance: Settings declare a refresh strategy; supported changes use targeted notification first, and Explorer restart remains an explicit fallback with status output.
  Complexity: M

- [ ] P1 - Add operation logs, GUI status, and exportable dry-run reports
  Why: Backup, restore, deployment, policy lock, and registry write failures are summarized but not retained in a user-visible diagnostic trail.
  Evidence: `explorer_tweaks.py` messagebox/print flows; Winhance and WinUtil automation transparency.
  Touches: `explorer_tweaks.py`
  Acceptance: GUI has a persistent log/status panel, CLI can emit a structured dry-run report, and failures include path, hive, action, error, and recovery hint.
  Complexity: M

- [ ] P1 - Extend policy and deployment metadata for Intune/MDM
  Why: Existing PowerShell export is useful, but enterprise users need policy/CSP awareness and Settings Catalog/remediation packaging guidance for managed devices.
  Evidence: `explorer_tweaks.py::is_policy_locked`, `build_powershell_script`; Microsoft Policy CSP and Intune Settings Catalog docs.
  Touches: `explorer_tweaks.py`, `README.md`
  Acceptance: Settings can declare policy/CSP equivalents; exports distinguish preference writes from managed policy writes and can generate Intune remediation-ready script pairs.
  Complexity: L

- [ ] P1 - Add Windows 11 25H2 compatibility gates
  Why: The OS enum stops at 24H2 while competitors ship compatibility updates around Windows build changes.
  Evidence: `explorer_tweaks.py::OSVersion`, `get_windows_version`; StartAllBack and ExplorerPatcher compatibility cadence.
  Touches: `explorer_tweaks.py`, `tests/test_deployment_helpers.py`
  Acceptance: OS detection recognizes 25H2+ builds, unsupported or changed settings show clear warnings, and catalog tests pin min/max build behavior.
  Complexity: S

### P2

- [ ] P2 - Add Explorer folder-view defaults management
  Why: Explorer users commonly want consistent Details/List/Icon views, columns, grouping, and sort order across folder types.
  Evidence: WinSetView feature set; current ExplorerTweaks Appearance settings stop at single registry toggles.
  Touches: `explorer_tweaks.py`, `tests/test_deployment_helpers.py`
  Acceptance: User can preview, back up, apply, and restore folder-type view defaults for common templates without replacing Explorer.
  Complexity: XL

- [ ] P2 - Expand context-menu management beyond ExplorerTweaks entries
  Why: The app installs its own shell entries and manages Send To items, but competitors expose inventory, disable/enable, icons, Shift-only visibility, and reusable action packs.
  Evidence: `CONTEXT_MENU_TARGETS`, `get_sendto_entries`; ShellAnything and Easy Context Menu.
  Touches: `explorer_tweaks.py`
  Acceptance: User can inspect common HKCU/HKLM context-menu entries, disable reversible registry-backed entries, export/import a safe action pack, and restore previous state.
  Complexity: L

- [ ] P2 - Pin and upgrade GUI/build dependencies with repeatable artifacts
  Why: `requirements.txt` floats CustomTkinter and PyInstaller major behavior, making portable EXE builds non-reproducible.
  Evidence: `requirements.txt`; PyInstaller changelog; CustomTkinter PyPI release history.
  Touches: `requirements.txt`, `ExplorerTweaks.spec`, `build.bat`, `tests/test_deployment_helpers.py`
  Acceptance: Dependencies are pinned, upgrade notes are documented, build uses the pinned environment, and the EXE smoke path is testable without changing app behavior.
  Complexity: M

- [ ] P2 - Perform accessibility and localization pass
  Why: Custom widget controls, emoji labels, fixed minimum layout, modal-only feedback, and English-only strings limit usability compared with mature utilities that include language options.
  Evidence: `SettingCard`, `NavButton`, Tools page labels; WinSetView and Easy Context Menu language support.
  Touches: `explorer_tweaks.py`, `README.md`
  Acceptance: Visible strings come from a message catalog, high-contrast/focus states are verified, compact layout works below the current 1300px minimum where practical, and icon-only/emoji text has accessible labels or text alternatives.
  Complexity: L

### P3

- [ ] P3 - Improve release packaging and trust signals
  Why: A portable EXE exists, but distribution lacks a signed installer/ZIP manifest, checksums, and optional winget packaging metadata.
  Evidence: `build.bat`, `ExplorerTweaks.spec`, `dist/ExplorerTweaks.exe`; commercial and freeware comparator release pages.
  Touches: `build.bat`, `ExplorerTweaks.spec`, `README.md`
  Acceptance: Release artifacts include clean rebuild, checksum manifest, versioned ZIP, install/uninstall notes, and signing when a certificate is available.
  Complexity: M
