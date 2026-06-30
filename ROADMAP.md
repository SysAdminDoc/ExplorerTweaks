# ROADMAP

Backlog for ExplorerTweaks. Goal: stay focused on File Explorer and closely related shell surfaces such as taskbar, context menus, and search.

## Research-Driven Additions

### P3

- [ ] P3 - Improve release packaging and trust signals
  Why: A portable EXE exists, but distribution lacks a signed installer/ZIP manifest, checksums, and optional winget packaging metadata.
  Evidence: `build.bat`, `ExplorerTweaks.spec`, `dist/ExplorerTweaks.exe`; commercial and freeware comparator release pages.
  Touches: `build.bat`, `ExplorerTweaks.spec`, `README.md`
  Acceptance: Release artifacts include clean rebuild, checksum manifest, versioned ZIP, install/uninstall notes, and signing when a certificate is available.
  Complexity: M
