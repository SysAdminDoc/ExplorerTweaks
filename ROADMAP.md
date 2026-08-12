# ROADMAP

Actionable work only. Historical and completed roadmap material is archived in CHANGELOG.md; blocked work is kept in Roadmap_Blocked.md.

## Actionable Items

- [ ] P3 — Validate context-menu action `icon` field
  Why: The icon field passes through with zero validation while name/label/command are all pattern-checked; a malformed icon string is written directly to the registry.
  Where: explorer_tweaks.py validate_context_menu_action()
