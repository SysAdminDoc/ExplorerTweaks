# Research - ExplorerTweaks

## Executive Summary
ExplorerTweaks is a Windows 10/11 File Explorer and shell configuration utility with a dark CustomTkinter GUI, live previews, JSON/.reg/.ps1 export, PSRemoting deployment, multi-loaded-user registry application, backup/restore bundles, context-menu entry install, and sunrise/sunset dark-mode automation. Its strongest shape is not deep shell replacement; it is reversible, registry-first Explorer policy for power users and small IT fleets. Highest-value direction: harden restore safety first, then add an auditable apply/rollback pipeline, richer enterprise exports, safer shell refresh, and focused Explorer/context-menu capabilities that stay registry-backed. Top opportunities: secure ZIP restore validation, transactional apply/rollback plans, operation logs and GUI status, 25H2-aware setting catalog, Intune/remediation export, folder-view defaults, context-menu cleanup/action packs, dependency/build pinning, accessibility/i18n pass, and signed/packaged distribution.

## Product Map
- Core workflows: browse/search settings, toggle registry-backed Explorer/taskbar/search/privacy/theme options, preview visual effects, export/import profiles, apply presets locally or through PowerShell/PSRemoting.
- Core workflows: create/restore backup bundles, wipe recent items, manage Send To entries, restore Photo Viewer, install ExplorerTweaks shell entries, install dark-mode scheduled task.
- User personas: Windows power user, helpdesk/desktop admin, small fleet maintainer, privacy/performance tweaker, fresh-install setup owner.
- Platforms and distribution: Windows 10/11, Python 3.8+, CustomTkinter GUI, CLI, PyInstaller portable EXE; current OS detection tops out at Windows 11 24H2.
- Key integrations and data flows: HKCU/HKU registry writes, reg.exe export/import, PowerShell deployment scripts, WinRM Invoke-Command, Task Scheduler, Windows Location API, AppData scripts/logs, ZIP backup bundles.

## Competitive Landscape
- ExplorerPatcher: deep taskbar/Start/Explorer restoration with updater and uninstall paths. Learn: clear update/uninstall recovery UX and version-compatibility notices. Avoid: shell patching/injection that breaks across Windows cumulative updates.
- Windhawk: mod ecosystem for Windows behavior using global injection and hooks. Learn: searchable community modules and compatibility metadata. Avoid: process-wide hooking; it contradicts ExplorerTweaks' registry-first safety lane.
- Winhance and Chris Titus Tech WinUtil: broad Windows setup tools with presets, searchable toggles, app install/removal, and automation. Learn: configuration files, admin-mode clarity, and preset transparency. Avoid: becoming a general debloat/app installer.
- WinSetView: focused Explorer folder-view defaults with backup, restore, language selection, and explicit "nothing changes until submit" workflow. Learn: staged review, folder-type matrix, backup-first apply, and Windows-update reapply guidance. Avoid: complex folder-type UI until the current apply pipeline can roll back safely.
- ShellAnything and Easy Context Menu: context-menu customization, dynamic actions, icons, Shift-only entries, cleanup, and multilingual support. Learn: context-menu inventory and reversible action packs. Avoid: in-process shell extensions or unbounded arbitrary command execution.
- StartAllBack and Start11: commercial taskbar/Start products monetize advanced taskbar/Start restoration and rapid Windows build compatibility. Learn: compatibility matrix, release cadence, and polished restore/update flows. Avoid: competing on patched taskbar implementations.
- Winaero Tweaker/Bloatynosy/Ultimate Windows Tweaker class: many tweaks with simple categorized UIs. Learn: breadth matters only when paired with warnings and reversibility. Avoid: low-signal tweak accumulation beyond Explorer and closely related shell surfaces.

## Security, Privacy, and Reliability
- Verified: `restore_backup_bundle()` in `explorer_tweaks.py` uses `ZipFile.extractall(temp_path)` before validating members, manifest schema, registry file paths, or expected backup provenance. Python documents inspection before extracting untrusted archives; this is the top fix.
- Verified: restore imports every manifest-listed `.reg` file via `reg import` without whitelisting against `backup_registry_paths(get_all_settings())` or `EXTRA_BACKUP_REGISTRY_PATHS`.
- Verified: apply/import/preset paths call `set_registry_value()` directly and do not create a pre-change restore point, per-setting rollback record, or post-write verification.
- Verified: `restart_explorer()` force-kills `explorer.exe`; Microsoft exposes shell change notification APIs that may refresh many setting changes without killing Explorer.
- Verified: GUI actions mostly report through modal message boxes; CLI prints summaries. There is no unified operation log, crash log, exportable dry-run report, or per-setting error list.
- Verified: policy-lock detection exists but maps only a small set of policy paths; Microsoft Policy CSP and ADMX docs expose richer registry mappings for Search, CloudContent, Explorer, and Experience settings.

## Architecture Assessment
- `explorer_tweaks.py` is a 3,100+ line combined model, registry layer, script generator, backup engine, CLI, and GUI. Split candidates: settings catalog, registry/apply engine, backup engine, deployment exporters, GUI widgets, and preview widgets.
- `get_all_settings()` is the right declarative center, but it lacks fields for risk level, refresh requirement, policy/CSP mapping, rollback strategy, Windows build verification, and admin requirement.
- `restore_backup_bundle()`, `create_backup_bundle()`, `apply_profile_values()`, `cli_apply()`, `_import()`, and `_apply_preset()` need a shared plan/apply/verify engine so GUI, CLI, PS export, and remote apply behave identically.
- Tests currently cover deployment helpers only in `tests/test_deployment_helpers.py`; missing coverage includes malicious backup archives, manifest validation, backup restore whitelist behavior, settings catalog OS gates, policy detection, import/apply rollback, and CLI failure exits.
- Dependency constraints are loose: `customtkinter>=5.2.0` and `pyinstaller>=6.0.0`. Current public releases show CustomTkinter 6.0.0 and PyInstaller 6.21.0, so builds should be pinned and compatibility-tested instead of floating.
- UI accessibility gaps: emoji/icon text, custom switches/radio buttons, modal-only feedback, fixed minimum 1300x750 layout, and limited screen-reader/focus-state verification. i18n is absent while comparator tools show demand for language selection.

## Rejected Ideas
- Shell patching/taskbar injection from ExplorerPatcher, Windhawk, StartAllBack, and Start11: high user value but high breakage risk and contrary to registry-first reversibility.
- Full Explorer replacement or tabbed file manager parity from Files, Explorer++, Directory Opus, and OneCommander: duplicates a different product category.
- General debloat/app-install suite parity from Winhance, WinUtil, and Bloatynosy: would dilute the Explorer/shell focus and raise admin-risk surface.
- In-process shell-extension/plugin DLL model from ShellAnything: too hard to debug and too risky for a Python utility; registry-only context-menu packs are the safer subset.
- Mobile support: not applicable to a Windows registry and Explorer shell utility.
- Multi-user collaboration/sync: not applicable; the relevant multi-user work is local/remote Windows profile targeting, rollback, and auditability.

## Sources
### Direct OSS and freeware
- https://github.com/valinet/ExplorerPatcher
- https://github.com/ramensoftware/windhawk
- https://github.com/memstechtips/Winhance
- https://github.com/ChrisTitusTech/winutil
- https://github.com/builtbybel/Bloatynosy
- https://github.com/LesFerch/WinSetView
- https://github.com/end2endzone/ShellAnything
- https://www.sordum.org/7615/easy-context-menu-v1-6/
- https://winaero.com/winaero-tweaker/
- https://github.com/derceg/explorerplusplus
- https://github.com/w4po/ExplorerTabUtility

### Commercial and adjacent tools
- https://www.startallback.com/
- https://www.stardock.com/products/start11/
- https://www.gpsoft.com.au/
- https://www.onecommander.com/

### Platform, security, and dependencies
- https://docs.python.org/3/library/zipfile.html
- https://owasp.org/www-community/vulnerabilities/Zip_Slip
- https://learn.microsoft.com/en-us/windows/win32/shell/context-menu-handlers
- https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shchangenotify
- https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-experience
- https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-explorer
- https://learn.microsoft.com/en-us/intune/device-configuration/settings-catalog/
- https://pyinstaller.org/en/stable/CHANGES.html
- https://pyinstaller.org/en/stable/spec-files.html
- https://pypi.org/project/customtkinter/

## Open Questions
- Which Windows 11 25H2 build should be the local validation target for Explorer/taskbar/search registry behavior?
- Is code-signing material available for release EXEs, or should the next distribution pass produce unsigned artifacts plus hash verification only?
