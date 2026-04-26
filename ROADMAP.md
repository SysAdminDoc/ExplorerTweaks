# ROADMAP

Backlog for ExplorerTweaks. Goal: stay focused on File Explorer + closely related shell surfaces
(taskbar, context menus, search) rather than drift into being another full Winaero clone.

## Planned Features

### Settings coverage
- **Context menu editor** — add/remove "Open with" entries, manage `HKCR\*\shell` and
  `HKCR\Directory\shell` verbs, reorder entries. Biggest gap versus Winaero.
- **Send To folder manager** — list/edit/reorder `shell:sendto` entries inline.
- **Pin-to-Start and Pin-to-Quick-Access cleanup** — bulk-remove stuck pins.
- **Libraries editor** — add/remove folders from each Library, restore default set.
- **Default icons** — override the generic folder icon, Recycle Bin full/empty, Drive icons by
  letter (seen in Winaero; missing here).
- **Recent-items explicit wipe** — one-shot clear for Jump Lists, AutomaticDestinations,
  CustomDestinations.

### Windows 11 24H2 / 25H2 parity
- **Widget board, Copilot, Recall** — targeted disables with version-gated visibility.
- **"File Explorer address bar AI" toggle** for 25H2 builds that add it.
- **Classic photo viewer restore** (register `PhotoViewer.dll` verbs).

### Safety
- **System Restore point creation** before any bulk apply (PowerShell `Checkpoint-Computer`).
- **Signed `.reg` export / import** — undo any change by double-clicking the generated `.reg`.
- **Dry-run mode** — print the registry operations without writing, useful for auditing before
  running on a managed machine.
- **Policy-aware detection** — warn when a setting is locked by Group Policy (HKLM\...\Policies)
  so users aren't confused why a toggle won't stick.

### UX
- **Search across all settings** with fuzzy matching and category scoping.
- **Presets / profiles** — "Minimal", "Privacy", "Power User", plus user-savable JSON profiles.
- **Diff view** between current system state and a profile.
- **Per-setting "why it matters" link** — small info icon linking to a documented explanation.

### Distribution
- **Single-file PyInstaller exe** signed with Authenticode; drop loose `.py` from releases.
- **Scoop and Winget manifests**.
- **CLI mode** — `ExplorerTweaks.exe --apply profile.json` for scripted provisioning.

## Competitive Research

- **Winaero Tweaker** — the dominant free all-in-one, covers hundreds of tweaks and has a universal
  undo. ExplorerTweaks should not duplicate it; focus on live preview and curated Explorer-specific
  coverage instead.
- **OFGB (Oh Frick Go Back)** — single-purpose ad remover for Windows 11. Worth integrating the
  ad-specific toggles as a preset so users don't need both tools.
- **Microsoft PowerToys** — official, limited Explorer tweaks (File Locksmith, PowerRename). Don't
  overlap; complement by linking to PowerToys features where appropriate.
- **privacy.sexy** — script-generation site. Mirror its category data model and let users import
  its JSON recipes.

## Nice-to-Haves

- **Right-click shell extension** to launch ExplorerTweaks focused on the setting behind whatever
  was right-clicked (e.g. right-click Recycle Bin -> jump to Recycle Bin tweaks).
- **Registry file generator** — emit a `.reg` / `.ps1` covering the current UI state for IT
  deployment.
- **Remote apply** over PSRemoting / Intune PowerShell to push a profile to a fleet.
- **Multi-user mode** — apply settings for all local users (HKU\.DEFAULT + per-profile
  iteration).
- **Backup/restore bundle** including registry subtrees + wallpaper + taskbar pin layout.
- **Darkmode auto-switch** tied to sunrise/sunset via Location API.

## Open-Source Research (Round 2)

### Related OSS Projects
- **ExplorerPatcher** — https://github.com/valinet/ExplorerPatcher — C hooks into `explorer.exe` shell components; most feature-dense Win10/11 tweaker. No registry-only, replaces shell DLLs.
- **ExplorerTabUtility** — https://github.com/w4po/ExplorerTabUtility — Auto-converts new Explorer windows into tabs on Win11 22H2+. C#/WinForms, system-tray driven.
- **Explorer++** — https://github.com/derceg/explorerplusplus — Lightweight portable Explorer replacement with tabbed browsing, registry or JSON config.
- **ShellAnything** — https://github.com/end2endzone/ShellAnything — XML-driven Explorer context-menu customizer; good model for user-authored action packs.
- **FastBrowse** — https://github.com/UnmappedStack/FastBrowse — Experimental fast Explorer alternative; useful benchmark for "slow Explorer" complaints.
- **Winhance** — https://github.com/memstechtips/Winhance — PowerShell-based Windows customization suite; overlaps many of the same reg tweaks.

### Features to Borrow
- Tab-convert-on-open behavior from `ExplorerTabUtility` — detect new `explorer.exe` windows and merge into existing Explorer tabs.
- XML/JSON rule packs from `ShellAnything` — let users ship context-menu additions alongside a tweak profile.
- Registry-only reversibility from `Winhance` — every tweak must have a matching restore entry so uninstall = clean system.
- `ExplorerPatcher`'s per-category UI grouping (Taskbar / Start / File Explorer / System Tray) — cleaner than a flat toggle list at 50+ options.
- Portable mode with JSON config (from `Explorer++`) — run from USB, settings travel with the binary.
- Classic-vs-modern context-menu toggle (`{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}` InprocServer32) — this is the #1 request across all comparable tools.

### Patterns & Architectures Worth Studying
- **Hooking vs registry**: `ExplorerPatcher` uses DLL injection for live reconfiguration; `ExplorerTweaks` uses registry + explorer restart. Consider a hybrid: registry for persistent, IAccessible/UIA for preview.
- **Profile diffing** (`Winhance`): export current registry state → diff against profile → apply only the delta. Avoids repeatedly writing identical keys.
- **Shell notification broadcast**: `SHChangeNotify(SHCNE_ASSOCCHANGED)` + `WM_SETTINGCHANGE` for live refresh without restarting Explorer. Most tools restart; this pattern avoids it for many tweaks.
- **Sandboxed preview** (`ShellAnything`): render context menus in a VM/mock shell before committing — reduces "why did my right-click break" support load.
