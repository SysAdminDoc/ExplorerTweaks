# ROADMAP

Backlog for ExplorerTweaks. Goal: stay focused on File Explorer and closely related shell surfaces such as taskbar, context menus, and search.

## Research-Driven Additions

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
