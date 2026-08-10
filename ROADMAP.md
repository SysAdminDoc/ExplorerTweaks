# ROADMAP

Actionable work only. Historical and completed roadmap material is archived in CHANGELOG.md; blocked work is kept in Roadmap_Blocked.md.

## Actionable Items

- [ ] P2 — Split dark_system and dark_apps into separate preview fields
  Why: Both map to preview_key="dark_mode", so toggling one overwrites the other's preview state; the live preview shows a single dark/light mode that doesn't reflect Windows' split system-vs-app theming.
  Where: explorer_tweaks.py (RegistrySetting definitions, PreviewState, ThemePreview)

- [ ] P3 — Validate context-menu action `icon` field
  Why: The icon field passes through with zero validation while name/label/command are all pattern-checked; a malformed icon string is written directly to the registry.
  Where: explorer_tweaks.py validate_context_menu_action()

- [ ] P3 — Add `disable_network_thumbs` to preview state
  Why: The "No Network Thumbs" setting has no preview_key and no corresponding PreviewState field, so it has no live preview feedback.
  Where: explorer_tweaks.py get_all_settings(), PreviewState
