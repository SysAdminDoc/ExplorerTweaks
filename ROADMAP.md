# ROADMAP

Backlog for ExplorerTweaks. Goal: stay focused on File Explorer and closely related shell surfaces such as taskbar, context menus, and search.

## Research-Driven Additions

### P2

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
